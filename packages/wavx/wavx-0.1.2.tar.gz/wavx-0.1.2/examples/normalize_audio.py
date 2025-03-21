#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WavX 音频标准化示例

这个示例展示了如何使用WavX库将音频文件标准化到指定的RMS电平
"""

import os
import sys
import argparse

# 添加父目录到Python路径，以便可以导入wavx
# 注意：安装库后不需要这一步
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import wavx


def main():
    """主函数，解析命令行参数并标准化音频文件"""
    parser = argparse.ArgumentParser(description='将音频文件标准化到指定的RMS电平')
    parser.add_argument('input_file', help='输入音频文件路径')
    parser.add_argument('output_file', help='输出音频文件路径')
    parser.add_argument('--target', '-t', type=float, default=-20.0, help='目标RMS电平(dB FS)，默认为-20dB')
    parser.add_argument('--reference', '-r', choices=['square', 'sine'], default='square', 
                         help='参考信号类型，可选"square"或"sine"，默认为"square"')
    parser.add_argument('--freq', '-f', type=float, default=1000.0, help='参考信号频率(Hz)，默认为1000Hz')
    args = parser.parse_args()
    
    try:
        # 首先分析原始音频文件
        print(f"分析原始音频文件: {args.input_file}")
        original_info = wavx.analysis.amplitude.analyze_amplitude(args.input_file)
        print("原始音频信息:")
        wavx.analysis.amplitude.print_amplitude_info(original_info)
        
        print("\n正在标准化音频...")
        # 标准化音频文件
        normalization_info = wavx.processing.normalization.normalize_to_target(
            input_file=args.input_file,
            output_file=args.output_file,
            target_rms_db=args.target,
            reference_type=args.reference,
            reference_freq=args.freq
        )
        
        # 打印标准化结果
        wavx.processing.normalization.print_normalization_info(normalization_info)
        
        # 分析处理后的音频文件
        print(f"\n分析处理后的音频文件: {args.output_file}")
        processed_info = wavx.analysis.amplitude.analyze_amplitude(args.output_file)
        print("处理后音频信息:")
        wavx.analysis.amplitude.print_amplitude_info(processed_info)
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())