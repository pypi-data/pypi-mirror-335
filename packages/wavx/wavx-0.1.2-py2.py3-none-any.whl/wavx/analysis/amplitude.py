#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音频振幅分析模块

提供音频文件的幅度、响度和相关声学参数的分析功能
"""

import numpy as np
import soundfile as sf
import librosa
import warnings
from typing import Dict, Any, Optional, Union, Tuple


def analyze_amplitude(
    audio_file: str,
    rms_window_ms: float = 50.0,
    consider_dc: bool = True,
) -> Dict[str, Any]:
    """
    分析音频文件的振幅和响度信息

    参数:
        audio_file (str): 音频文件路径
        rms_window_ms (float): RMS窗口大小(毫秒)
        consider_dc (bool): 是否考虑DC偏移

    返回:
        Dict[str, Any]: 包含各种振幅和响度测量值的字典
    """
    # 读取音频文件
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y, sr = librosa.load(audio_file, sr=None, mono=False)
    
    # 确保y是二维数组 [channels, samples]
    if y.ndim == 1:
        y = y.reshape(1, -1)
    
    # 获取bit depth
    sf_info = sf.info(audio_file)
    bit_depth = sf_info.subtype.split('_')[-1]
    if bit_depth.isdigit():
        bit_depth = int(bit_depth)
    else:
        # 估计bit depth
        bit_depth = int(np.ceil(np.log2(np.max(np.abs(y)) * 2)))
    
    # 计算窗口大小(样本数)
    window_size = int(rms_window_ms * sr / 1000)
    
    # 计算最大和最小样本值
    max_sample = np.max(y) * (2**(bit_depth-1) - 1)
    min_sample = np.min(y) * (2**(bit_depth-1) - 1)
    
    # 计算峰值幅度(dB)
    peak_amplitude = 20 * np.log10(np.max(np.abs(y)))
    
    # 计算TP(True Peak) - 过采样检测真实峰值
    y_over = librosa.resample(y, orig_sr=sr, target_sr=sr*4)
    true_peak_amplitude = 20 * np.log10(np.max(np.abs(y_over)))
    
    # 检查可能的剪切样本数量
    clipped_samples = np.sum(np.abs(y) >= 0.99)
    
    # 计算RMS值
    def calculate_rms(signal):
        if consider_dc:
            return np.sqrt(np.mean(signal**2))
        else:
            # 移除DC偏移
            return np.sqrt(np.mean((signal - np.mean(signal))**2))
    
    # 总体RMS
    total_rms = calculate_rms(y)
    total_rms_db = 20 * np.log10(total_rms) if total_rms > 0 else -np.inf
    
    # 分段RMS
    num_windows = y.shape[1] // window_size
    rms_segments = []
    
    for i in range(num_windows):
        segment = y[:, i*window_size:(i+1)*window_size]
        rms = calculate_rms(segment)
        rms_segments.append(rms)
    
    rms_segments = np.array(rms_segments)
    max_rms = np.max(rms_segments)
    min_rms = np.min(rms_segments)
    avg_rms = np.mean(rms_segments)
    
    max_rms_db = 20 * np.log10(max_rms) if max_rms > 0 else -np.inf
    min_rms_db = 20 * np.log10(min_rms) if min_rms > 0 else -np.inf
    avg_rms_db = 20 * np.log10(avg_rms) if avg_rms > 0 else -np.inf
    
    # 计算DC偏移
    dc_offset = np.mean(y) * 100  # 以百分比表示
    
    # 计算动态范围
    dynamic_range = max_rms_db - min_rms_db
    used_dynamic_range = np.ptp(20 * np.log10(np.clip(rms_segments, 1e-10, None)))
    
    # 计算响度 (旧版)
    loudness_old = total_rms_db
    
    # 感知响度 (简化版)
    # 应用A加权过滤器来模拟人耳感知
    y_weighted = librosa.A_weighting(librosa.db_to_power(librosa.amplitude_to_db(y)))
    perceived_loudness_old = 20 * np.log10(np.sqrt(np.mean(y_weighted**2)))
    
    # ITU-R BS.1770-3 响度
    # 简化版实现
    try:
        import pyloudnorm as pyln
        
        # 创建BS.1770-4测量器
        meter = pyln.Meter(sr)
        loudness_lufs = meter.integrated_loudness(y.T)
    except ImportError:
        # 如果没有pyloudnorm，使用简化实现
        # K加权滤波
        y_filtered = librosa.effects.preemphasis(y, coef=0.98)
        loudness_lufs = -0.691 + 10 * np.log10(np.mean(y_filtered**2)) - 10
    
    # 整合所有测量结果
    results = {
        "peak_amplitude": round(peak_amplitude, 2),
        "true_peak_amplitude": round(true_peak_amplitude, 2),
        "max_sample_value": int(max_sample),
        "min_sample_value": int(min_sample),
        "clipped_samples": int(clipped_samples),
        "total_rms_amplitude": round(total_rms_db, 2),
        "max_rms_amplitude": round(max_rms_db, 2),
        "min_rms_amplitude": round(min_rms_db, 2),
        "avg_rms_amplitude": round(avg_rms_db, 2),
        "dc_offset": round(dc_offset, 2),
        "bit_depth": bit_depth,
        "dynamic_range": round(dynamic_range, 2),
        "used_dynamic_range": round(used_dynamic_range, 2),
        "loudness_old": round(loudness_old, 2),
        "perceived_loudness_old": round(perceived_loudness_old, 2),
        "loudness_lufs": round(loudness_lufs, 2),
        "sample_rate": sr,
        "channels": y.shape[0],
        "duration": y.shape[1] / sr,
        "rms_window_ms": rms_window_ms,
        "consider_dc": consider_dc,
    }
    
    return results


def print_amplitude_info(info: Dict[str, Any]) -> None:
    """
    打印音频振幅分析信息

    参数:
        info (Dict[str, Any]): 由analyze_amplitude返回的振幅信息字典
    """
    print("===== 音频振幅分析 =====")
    print(f"峰值幅度:\t{info['peak_amplitude']} dB")
    print(f"实际峰值幅度:\t{info['true_peak_amplitude']}dBTP")
    print(f"最大采样值:\t{info['max_sample_value']}")
    print(f"最小采样值:\t{info['min_sample_value']}")
    print(f"可能的剪断样本:\t{info['clipped_samples']}")
    print(f"总计 RMS 振幅：\t{info['total_rms_amplitude']} dB")
    print(f"最大 RMS 振幅:\t{info['max_rms_amplitude']} dB")
    print(f"最小 RMS 振幅:\t{info['min_rms_amplitude']} dB")
    print(f"平均 RMS 振幅:\t{info['avg_rms_amplitude']} dB")
    print(f"DC 偏移:\t{info['dc_offset']}%")
    print(f"测量位深度:\t{info['bit_depth']}")
    print(f"动态范围:\t{info['dynamic_range']} dB")
    print(f"使用的动态范围:\t{info['used_dynamic_range']} dB")
    print(f"响度（旧版）:\t{info['loudness_old']} dB")
    print(f"感知响度（旧版）:\t{info['perceived_loudness_old']} dB")
    print(f"ITU-R BS.1770-3 响度: {info['loudness_lufs']} LUFS")
    print("\n附加信息:")
    print(f"采样率: {info['sample_rate']} Hz")
    print(f"声道数: {info['channels']}")
    print(f"持续时间: {info['duration']:.2f} 秒")
    print(f"使用 RMS 窗口 {info['rms_window_ms']} 毫秒")
    print(f"考虑 DC = {info['consider_dc']}")
    print("========================") 