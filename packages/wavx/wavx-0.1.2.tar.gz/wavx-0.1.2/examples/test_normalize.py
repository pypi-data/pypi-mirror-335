#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试WavX库的RMS标准化功能
将指定的音频文件标准化到-30dB FS
"""

import os
import sys
import time

# 添加当前目录到Python路径，以便可以导入wavx
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import wavx

input_file = r"C:\Users\admin\Desktop\250228_QUEST\voice\wanting\250226_ba_la_300_500ms.wav"
output_file = r"C:\Users\admin\Desktop\250228_QUEST\voice\wanting\250226_ba_la_300_500ms_30ei.wav"
target_rms_db = -30.0
original_info = wavx.analysis.amplitude.analyze_amplitude(input_file)
normalization_info = wavx.processing.normalization.normalize_to_target(
        input_file=input_file,
        output_file=output_file,
        target_rms_db=target_rms_db,
        reference_type="square"
)
    
# 打印标准化信息
print(f"\n音频 '{os.path.basename(input_file)}' 已从 {normalization_info['original_rms_db']:.2f} dB FS 调整到 {normalization_info['processed_rms_db']:.2f} dB FS")
