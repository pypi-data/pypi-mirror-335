# WavX

WavX 是一个用于音频分析和处理的Python库，提供简单而强大的API来处理各种音频相关任务。

## 特性

- 音频文件分析，包括振幅、响度和声学参数测量
- 音频处理，包括RMS电平标准化
- 模块化设计，易于扩展
- 简洁直观的API接口

## 安装

```bash
pip install wavx
```

## 快速开始

### 分析音频文件振幅信息

```python
import wavx

# 分析音频文件并获取振幅信息
amplitude_info = wavx.analysis.amplitude.analyze_amplitude("your_audio_file.wav")

# 打印所有振幅信息
wavx.analysis.amplitude.print_amplitude_info(amplitude_info)

# 或者获取特定信息
print(f"峰值幅度: {amplitude_info['peak_amplitude']} dB")
print(f"总计 RMS 振幅: {amplitude_info['total_rms_amplitude']} dB")
```

### 将音频文件标准化到目标RMS电平

```python
import wavx

# 将音频文件标准化到 -20 dB FS
result = wavx.processing.normalization.normalize_to_target(
    input_file="input.wav",
    output_file="output.wav",
    target_rms_db=-20.0,
    reference_type="square"  # 或 "sine"
)

# 打印标准化信息
wavx.processing.normalization.print_normalization_info(result)
```

## 项目结构

```
wavx/
├── docs/
│   ├── amplitude/
│   │   └── amplitude_analysis.md  # 振幅分析文档
│   └── processing/
│       └── normalization.md       # RMS标准化文档
├── examples/
│   ├── analyze_audio.py           # 音频分析示例
│   └── normalize_audio.py         # 音频标准化示例
├── wavx/
│   ├── __init__.py                # 包初始化
│   ├── cli.py                     # 命令行界面
│   ├── analysis/
│   │   ├── __init__.py            # 分析模块初始化
│   │   └── amplitude.py           # 振幅分析功能
│   ├── processing/
│   │   ├── __init__.py            # 处理模块初始化
│   │   └── normalization.py       # RMS标准化功能
│   ├── tests/
│   │   ├── __init__.py            # 测试初始化
│   │   ├── test_amplitude.py      # 振幅分析测试
│   │   └── test_normalization.py  # 标准化测试
│   └── utils/
│       └── __init__.py            # 工具模块初始化
├── README.md                      # 英文文档
├── README_zh.md                   # 中文文档
├── requirements.txt               # 项目依赖
└── setup.py                       # 包安装配置
```

## 命令行使用

安装后，可以从命令行使用WavX：

```bash
# 基本振幅分析
wavx amplitude path/to/audio.wav

# 使用自定义参数
wavx amplitude path/to/audio.wav --window 100 --no-dc

# RMS标准化
wavx normalize input.wav output.wav --target -18.0

# 使用自定义参考信号
wavx normalize input.wav output.wav --reference sine --freq 500
```

## 未来扩展

模块化设计允许简单扩展：

1. **更多分析功能**：
   - 频谱分析
   - 谐波分析
   - 混响和空间特性分析

2. **更多音频处理功能**：
   - 均衡器
   - 噪声消除
   - 动态范围压缩
   - 重采样和格式转换

3. **可视化功能**：
   - 波形显示
   - 频谱图
   - 响度/RMS历史图

## 版本记录

- v0.1.0 (2025-03-20): 初始版本，包含振幅分析功能
- v0.1.1 (2025-03-20): 添加docs目录和双语README文件
- v0.1.2 (2025-03-20): 添加RMS标准化功能

## 贡献

欢迎对代码贡献、提问或提出改进建议！

## 许可证

MIT 许可证 