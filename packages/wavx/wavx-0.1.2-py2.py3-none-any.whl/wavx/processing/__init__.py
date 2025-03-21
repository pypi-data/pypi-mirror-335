#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WavX 音频处理模块

包含各种音频处理和转换功能
"""

# 导入子模块
from . import normalization

# 为方便使用，直接导出一些常用函数
from .normalization import normalize_rms, normalize_to_target 