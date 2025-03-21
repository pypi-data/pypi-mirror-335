# WavX 文档 / WavX Documentation

[English](#wavx-documentation) | [中文](#wavx-文档)

## WavX Documentation

WavX is a Python library for audio analysis and processing, providing a simple yet powerful API for handling various audio-related tasks. This documentation provides an overview of WavX's features and usage.

### Available Modules

- [Amplitude Analysis](./amplitude/amplitude_analysis.md) - Tools for analyzing audio amplitude and loudness
- [RMS Normalization](./processing/normalization.md) - Tools for normalizing audio files to a target RMS level

### Installation

```bash
pip install wavx
```

### Basic Usage

```python
import wavx

# Analyze audio file and get amplitude information
amplitude_info = wavx.analysis.amplitude.analyze_amplitude("your_audio_file.wav")

# Print all amplitude information
wavx.analysis.amplitude.print_amplitude_info(amplitude_info)

# Normalize audio file to target RMS
normalization_info = wavx.processing.normalization.normalize_to_target(
    "input.wav",
    "output.wav",
    target_rms_db=-20.0
)
```

### Command Line Interface

WavX also provides a command-line interface for quick analysis and processing:

```bash
# Show help
wavx --help

# Analyze amplitude
wavx amplitude your_audio_file.wav

# Normalize audio
wavx normalize input.wav output.wav --target -18.0
```

### Project Structure

```
wavx/
├── docs/                           # Documentation
│   ├── index.md                    # This documentation index
│   ├── amplitude/
│   │   └── amplitude_analysis.md   # Amplitude analysis documentation
│   └── processing/
│       └── normalization.md        # RMS normalization documentation
├── examples/                       # Usage examples 
├── wavx/                           # Core package
│   ├── analysis/                   # Analysis modules
│   ├── processing/                 # Processing modules
│   ├── utils/                      # Utility functions
│   └── tests/                      # Unit tests
├── README.md                       # English README
└── README_zh.md                    # Chinese README
```

### Contributing

Contributions to the code, questions, or suggestions are welcome! Please refer to the [GitHub repository](https://github.com/yourusername/wavx) for more information.

### Version History

- v0.1.0 (2025-03-20): Initial release with amplitude analysis functionality
- v0.1.1 (2025-03-20): Added docs directory and bilingual README files
- v0.1.2 (2025-03-20): Added RMS normalization functionality

---

## WavX 文档

WavX 是一个用于音频分析和处理的Python库，提供简单而强大的API来处理各种音频相关任务。本文档提供了WavX的功能和用法概述。

### 可用模块

- [振幅分析](./amplitude/amplitude_analysis.md) - 用于分析音频振幅和响度的工具
- [RMS标准化](./processing/normalization.md) - 用于将音频文件标准化到目标RMS电平的工具

### 安装

```bash
pip install wavx
```

### 基本用法

```python
import wavx

# 分析音频文件并获取振幅信息
amplitude_info = wavx.analysis.amplitude.analyze_amplitude("your_audio_file.wav")

# 打印所有振幅信息
wavx.analysis.amplitude.print_amplitude_info(amplitude_info)

# 将音频文件标准化到目标RMS电平
normalization_info = wavx.processing.normalization.normalize_to_target(
    "input.wav",
    "output.wav",
    target_rms_db=-20.0
)
```

### 命令行界面

WavX还提供了命令行界面用于快速分析和处理：

```bash
# 显示帮助
wavx --help

# 分析振幅
wavx amplitude your_audio_file.wav

# 标准化音频
wavx normalize input.wav output.wav --target -18.0
```

### 项目结构

```
wavx/
├── docs/                           # 文档
│   ├── index.md                    # 本文档索引
│   ├── amplitude/
│   │   └── amplitude_analysis.md   # 振幅分析文档
│   └── processing/
│       └── normalization.md        # RMS标准化文档
├── examples/                       # 使用示例
├── wavx/                           # 核心包
│   ├── analysis/                   # 分析模块
│   ├── processing/                 # 处理模块
│   ├── utils/                      # 工具函数
│   └── tests/                      # 单元测试
├── README.md                       # 英文README
└── README_zh.md                    # 中文README
```

### 贡献

欢迎对代码贡献、提问或提出改进建议！请参考[GitHub仓库](https://github.com/yourusername/wavx)获取更多信息。

### 版本历史

- v0.1.0 (2025-03-20): 初始版本，包含振幅分析功能
- v0.1.1 (2025-03-20): 添加docs目录和双语README文件
- v0.1.2 (2025-03-20): 添加RMS标准化功能