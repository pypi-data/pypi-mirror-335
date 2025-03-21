#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
振幅分析模块的测试
"""

import unittest
import os
import numpy as np
import soundfile as sf
import tempfile

from wavx.analysis import amplitude


class TestAmplitudeAnalysis(unittest.TestCase):
    """测试振幅分析功能"""
    
    def setUp(self):
        """创建测试用的音频文件"""
        # 创建一个正弦波测试音频
        self.sr = 44100  # 采样率
        self.duration = 1  # 秒
        self.freq = 440  # Hz
        
        # 生成音频数据
        t = np.linspace(0, self.duration, int(self.sr * self.duration), endpoint=False)
        self.y = 0.5 * np.sin(2 * np.pi * self.freq * t)
        
        # 创建临时文件
        fd, self.temp_file = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        
        # 保存到.wav文件
        sf.write(self.temp_file, self.y, self.sr, subtype='PCM_16')
    
    def tearDown(self):
        """删除测试用的临时文件"""
        if os.path.exists(self.temp_file):
            os.unlink(self.temp_file)
    
    def test_analyze_amplitude(self):
        """测试振幅分析函数"""
        # 分析音频文件
        results = amplitude.analyze_amplitude(self.temp_file)
        
        # 检查关键测量值是否合理
        self.assertIsInstance(results, dict)
        self.assertIn('peak_amplitude', results)
        self.assertIn('true_peak_amplitude', results)
        self.assertIn('total_rms_amplitude', results)
        
        # 测试峰值幅度是否接近预期值 (0.5 振幅的正弦波 ≈ -6 dB)
        expected_peak_db = 20 * np.log10(0.5)
        self.assertAlmostEqual(results['peak_amplitude'], expected_peak_db, delta=1)
        
        # 测试RMS是否接近预期值 (正弦波RMS = 振幅/√2)
        expected_rms_db = 20 * np.log10(0.5 / np.sqrt(2))
        self.assertAlmostEqual(results['total_rms_amplitude'], expected_rms_db, delta=1)
        
        # 测试采样率是否正确
        self.assertEqual(results['sample_rate'], self.sr)
    
    def test_print_amplitude_info(self):
        """测试打印函数不抛出异常"""
        results = amplitude.analyze_amplitude(self.temp_file)
        try:
            amplitude.print_amplitude_info(results)
        except Exception as e:
            self.fail(f"print_amplitude_info抛出了异常: {e}")


if __name__ == '__main__':
    unittest.main() 