#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WavX - 音频分析和处理工具库

WavX是一个模块化的音频处理库，提供各种声学分析和处理功能。
"""

__version__ = '0.1.2'
__author__ = 'Chord'

# 导入子模块
from . import analysis
from . import utils
from . import processing

# 设置日志
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
