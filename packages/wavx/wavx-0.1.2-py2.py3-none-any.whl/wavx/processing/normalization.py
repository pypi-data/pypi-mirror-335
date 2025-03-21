#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音频标准化模块

提供音频电平标准化和调整功能
"""

import os
import numpy as np
import soundfile as sf
import librosa
import warnings
from typing import Dict, Any, Optional, Union, Tuple

from ..analysis import amplitude


def normalize_rms(
    audio_data: np.ndarray,
    target_rms_db: float = -20.0,
    current_rms_db: Optional[float] = None,
) -> np.ndarray:
    """
    将音频数据标准化到指定的RMS电平

    参数:
        audio_data (np.ndarray): 音频数据数组
        target_rms_db (float): 目标RMS电平，单位dB
        current_rms_db (Optional[float]): 当前RMS电平，如果为None则会自动计算

    返回:
        np.ndarray: 标准化后的音频数据
    """
    # 确保音频是二维数组 [channels, samples]
    if audio_data.ndim == 1:
        audio_data = audio_data.reshape(1, -1)
    
    # 如果未提供当前RMS，则计算
    if current_rms_db is None:
        # 计算当前RMS
        rms = np.sqrt(np.mean(audio_data**2))
        current_rms_db = 20 * np.log10(rms) if rms > 0 else -100.0
    
    # 计算增益
    gain_db = target_rms_db - current_rms_db
    gain_linear = 10 ** (gain_db / 20.0)
    
    # 应用增益
    normalized_audio = audio_data * gain_linear
    
    # 防止失真，如果最大值大于1.0，则缩放
    max_val = np.max(np.abs(normalized_audio))
    if max_val > 0.99:
        normalized_audio = normalized_audio * (0.99 / max_val)
    
    return normalized_audio


def reference_sine_wave(
    duration: float = 1.0,
    amplitude: float = 1.0,
    freq: float = 1000.0,
    sample_rate: int = 44100,
) -> np.ndarray:
    """
    生成参考正弦波

    参数:
        duration (float): 持续时间，单位秒
        amplitude (float): 振幅，1.0代表满刻度
        freq (float): 频率，单位Hz
        sample_rate (int): 采样率，单位Hz

    返回:
        np.ndarray: 正弦波数据 [1, samples]
    """
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    sine_wave = amplitude * np.sin(2 * np.pi * freq * t)
    return sine_wave.reshape(1, -1)


def reference_square_wave(
    duration: float = 1.0,
    amplitude: float = 1.0,
    freq: float = 1000.0,
    sample_rate: int = 44100,
) -> np.ndarray:
    """
    生成参考方波

    参数:
        duration (float): 持续时间，单位秒
        amplitude (float): 振幅，1.0代表满刻度
        freq (float): 频率，单位Hz
        sample_rate (int): 采样率，单位Hz

    返回:
        np.ndarray: 方波数据 [1, samples]
    """
    t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
    square_wave = amplitude * np.sign(np.sin(2 * np.pi * freq * t))
    return square_wave.reshape(1, -1)


def normalize_to_target(
    input_file: str,
    output_file: str,
    target_rms_db: float = -20.0,
    reference_type: str = "square",
    reference_duration: float = 1.0,
    reference_freq: float = 1000.0,
) -> Dict[str, Any]:
    """
    将音频文件标准化到指定的RMS电平，并保存结果

    参数:
        input_file (str): 输入音频文件路径
        output_file (str): 输出音频文件路径
        target_rms_db (float): 目标RMS电平，单位dB
        reference_type (str): 参考信号类型，可选 "square" 或 "sine"
        reference_duration (float): 参考信号持续时间，单位秒
        reference_freq (float): 参考信号频率，单位Hz

    返回:
        Dict[str, Any]: 包含标准化信息的字典
    """
    # 读取音频文件
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y, sr = librosa.load(input_file, sr=None, mono=False)
    
    # 确保y是二维数组 [channels, samples]
    if y.ndim == 1:
        y = y.reshape(1, -1)
    
    # 获取原始音频的RMS信息
    original_info = amplitude.analyze_amplitude(input_file)
    original_rms_db = original_info["total_rms_amplitude"]
    
    # 创建参考信号
    if reference_type.lower() == "sine":
        ref_signal = reference_sine_wave(
            duration=reference_duration,
            amplitude=1.0,
            freq=reference_freq,
            sample_rate=sr
        )
    else:  # 默认使用方波
        ref_signal = reference_square_wave(
            duration=reference_duration,
            amplitude=1.0,
            freq=reference_freq,
            sample_rate=sr
        )
    
    # 标准化参考信号到目标RMS电平
    ref_rms = np.sqrt(np.mean(ref_signal**2))
    ref_rms_db = 20 * np.log10(ref_rms) if ref_rms > 0 else -100
    normalized_ref = normalize_rms(ref_signal, target_rms_db, ref_rms_db)
    
    # 标准化音频到与参考信号相同的RMS电平
    normalized_audio = normalize_rms(y, target_rms_db, original_rms_db)
    
    # 保存输出文件
    sf_info = sf.info(input_file)
    sf.write(
        output_file,
        normalized_audio.T,
        sr,
        subtype=sf_info.subtype
    )
    
    # 分析处理后的音频
    processed_info = amplitude.analyze_amplitude(output_file)
    processed_rms_db = processed_info["total_rms_amplitude"]
    
    # 整合结果信息
    result = {
        "input_file": input_file,
        "output_file": output_file,
        "original_rms_db": original_rms_db,
        "target_rms_db": target_rms_db,
        "processed_rms_db": processed_rms_db,
        "reference_type": reference_type,
        "reference_freq": reference_freq,
        "sample_rate": sr,
        "channels": y.shape[0],
        "duration": y.shape[1] / sr,
    }
    
    return result


def print_normalization_info(info: Dict[str, Any]) -> None:
    """
    打印标准化处理信息

    参数:
        info (Dict[str, Any]): 由normalize_to_target返回的信息字典
    """
    print("===== 音频RMS标准化 =====")
    print(f"输入文件: {info['input_file']}")
    print(f"输出文件: {info['output_file']}")
    print(f"原始RMS电平: {info['original_rms_db']:.2f} dB FS")
    print(f"目标RMS电平: {info['target_rms_db']:.2f} dB FS")
    print(f"处理后RMS电平: {info['processed_rms_db']:.2f} dB FS")
    print(f"\n音频 '{os.path.basename(info['input_file'])}' 已从 {info['original_rms_db']:.2f} dB FS 调整到 {info['processed_rms_db']:.2f} dB FS")
    print(f"参考信号类型: {info['reference_type']}")
    print(f"参考信号频率: {info['reference_freq']} Hz")
    print(f"采样率: {info['sample_rate']} Hz")
    print(f"声道数: {info['channels']}")
    print(f"持续时间: {info['duration']:.2f} 秒")
    print("=========================") 