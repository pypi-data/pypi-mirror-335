#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WavX 音频分析示例

这个示例展示了如何使用WavX库分析音频文件的振幅信息
"""

import os
import sys
import argparse

# 添加父目录到Python路径，以便可以导入wavx
# 注意：安装库后不需要这一步
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import wavx


def main():
    """主函数，解析命令行参数并分析音频文件"""
    parser = argparse.ArgumentParser(description='分析音频文件的振幅信息')
    parser.add_argument('audio_file', help='音频文件路径')
    parser.add_argument('--window', type=float, default=50.0, help='RMS窗口大小(毫秒)')
    parser.add_argument('--no-dc', action='store_false', dest='consider_dc', help='不考虑DC偏移')
    args = parser.parse_args()
    
    try:
        # 分析音频文件
        print(f"分析音频文件: {args.audio_file}")
        print(f"RMS窗口大小: {args.window} ms")
        print(f"考虑DC偏移: {args.consider_dc}")
        print("正在分析...")
        
        # 调用分析函数
        amplitude_info = wavx.analysis.amplitude.analyze_amplitude(
            args.audio_file,
            rms_window_ms=args.window,
            consider_dc=args.consider_dc
        )
        
        # 打印结果
        wavx.analysis.amplitude.print_amplitude_info(amplitude_info)
        
        # 如果需要，也可以直接访问特定信息
        print("\n特定信息示例:")
        print(f"峰值幅度: {amplitude_info['peak_amplitude']} dB")
        print(f"响度 (LUFS): {amplitude_info['loudness_lufs']} LUFS")
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 