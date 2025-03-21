#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
标准化模块的测试
"""

import unittest
import os
import numpy as np
import soundfile as sf
import tempfile

from wavx.processing import normalization
from wavx.analysis import amplitude


class TestNormalization(unittest.TestCase):
    """测试音频标准化功能"""
    
    def setUp(self):
        """创建测试用的音频文件"""
        # 创建一个正弦波测试音频
        self.sr = 44100  # 采样率
        self.duration = 1  # 秒
        self.freq = 440  # Hz
        
        # 生成音频数据 - 较小的振幅，用于测试放大
        t = np.linspace(0, self.duration, int(self.sr * self.duration), endpoint=False)
        self.y_quiet = 0.1 * np.sin(2 * np.pi * self.freq * t)
        
        # 生成音频数据 - 较大的振幅，用于测试降低
        self.y_loud = 0.8 * np.sin(2 * np.pi * self.freq * t)
        
        # 创建临时文件
        fd, self.quiet_file = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        fd, self.loud_file = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        fd, self.output_file = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        # 保存到.wav文件
        sf.write(self.quiet_file, self.y_quiet, self.sr, subtype='PCM_16')
        sf.write(self.loud_file, self.y_loud, self.sr, subtype='PCM_16')
    
    def tearDown(self):
        """删除测试用的临时文件"""
        for file in [self.quiet_file, self.loud_file, self.output_file]:
            if os.path.exists(file):
                os.unlink(file)
    
    def test_normalize_rms_array(self):
        """测试RMS标准化数组函数"""
        # 测试将安静的音频提高到目标电平
        target_rms_db = -20.0
        normalized = normalization.normalize_rms(
            audio_data=self.y_quiet.reshape(1, -1),
            target_rms_db=target_rms_db
        )
        
        # 计算normalized的RMS
        rms = np.sqrt(np.mean(normalized**2))
        normalized_rms_db = 20 * np.log10(rms)
        
        # 检查标准化后的RMS是否接近目标值
        self.assertAlmostEqual(normalized_rms_db, target_rms_db, delta=0.5)
    
    def test_normalize_to_target_quiet(self):
        """测试将安静的音频标准化到指定RMS"""
        target_rms_db = -20.0
        
        # 获取原始RMS
        original_info = amplitude.analyze_amplitude(self.quiet_file)
        original_rms_db = original_info["total_rms_amplitude"]
        
        # 标准化音频
        result = normalization.normalize_to_target(
            input_file=self.quiet_file,
            output_file=self.output_file,
            target_rms_db=target_rms_db
        )
        
        # 检查结果字典
        self.assertEqual(result["input_file"], self.quiet_file)
        self.assertEqual(result["output_file"], self.output_file)
        self.assertEqual(result["target_rms_db"], target_rms_db)
        self.assertAlmostEqual(result["processed_rms_db"], target_rms_db, delta=0.5)
        
        # 确认增益是否正确应用 (安静音频应该被放大)
        self.assertGreater(result["processed_rms_db"], original_rms_db)
    
    def test_normalize_to_target_loud(self):
        """测试将响亮的音频标准化到指定RMS"""
        target_rms_db = -20.0
        
        # 获取原始RMS
        original_info = amplitude.analyze_amplitude(self.loud_file)
        original_rms_db = original_info["total_rms_amplitude"]
        
        # 标准化音频
        result = normalization.normalize_to_target(
            input_file=self.loud_file,
            output_file=self.output_file,
            target_rms_db=target_rms_db
        )
        
        # 检查结果字典
        self.assertEqual(result["input_file"], self.loud_file)
        self.assertEqual(result["output_file"], self.output_file)
        self.assertEqual(result["target_rms_db"], target_rms_db)
        self.assertAlmostEqual(result["processed_rms_db"], target_rms_db, delta=0.5)
        
        # 确认增益是否正确应用 (响亮音频应该被降低)
        self.assertLess(result["processed_rms_db"], original_rms_db)
    
    def test_reference_signals(self):
        """测试参考信号生成"""
        # 测试正弦波
        sine = normalization.reference_sine_wave(
            duration=0.1,
            amplitude=0.5,
            freq=1000,
            sample_rate=44100
        )
        
        # 检查形状和峰值
        self.assertEqual(sine.shape[0], 1)  # 单声道
        self.assertEqual(sine.shape[1], 4410)  # 0.1秒 * 44100 Hz
        self.assertAlmostEqual(np.max(np.abs(sine)), 0.5, delta=0.01)  # 幅度
        
        # 测试方波
        square = normalization.reference_square_wave(
            duration=0.1,
            amplitude=0.5,
            freq=1000,
            sample_rate=44100
        )
        
        # 检查形状和峰值
        self.assertEqual(square.shape[0], 1)  # 单声道
        self.assertEqual(square.shape[1], 4410)  # 0.1秒 * 44100 Hz
        self.assertAlmostEqual(np.max(np.abs(square)), 0.5, delta=0.01)  # 幅度


if __name__ == '__main__':
    unittest.main() 