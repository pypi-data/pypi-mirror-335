#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WavX 音频分析模块

包含各种音频分析功能的模块集合
"""

from . import amplitude

# 为方便使用，直接导出一些常用函数
from .amplitude import analyze_amplitude, print_amplitude_info
