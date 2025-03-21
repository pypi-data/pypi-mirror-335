# 音频RMS标准化 / Audio RMS Normalization

[English](#audio-rms-normalization) | [中文](#音频rms标准化)

## Audio RMS Normalization

The normalization module provides tools for adjusting audio files to match a target RMS (Root Mean Square) level. This is commonly used in audio production to standardize the loudness of different audio files.

### Features

- Normalize audio data to a specified RMS level
- Support for both array-based and file-based normalization
- Generation of reference signals (sine and square waves)
- Detailed information about the normalization process

### API Usage

```python
from wavx.processing import normalization

# Normalize an audio file to -20 dB FS using a square wave reference
result = normalization.normalize_to_target(
    input_file="input.wav",
    output_file="output.wav",
    target_rms_db=-20.0,
    reference_type="square",  # or "sine"
    reference_freq=1000.0     # reference frequency in Hz
)

# Print the normalization information
normalization.print_normalization_info(result)

# Direct normalization of audio data arrays
import numpy as np
audio_data = np.random.uniform(-0.5, 0.5, (2, 44100))  # stereo audio
normalized_data = normalization.normalize_rms(
    audio_data=audio_data,
    target_rms_db=-18.0
)
```

### Command Line Usage

```bash
# Basic normalization
wavx normalize input.wav output.wav

# With custom parameters
wavx normalize input.wav output.wav --target -18.0 --reference sine --freq 500
```

### Parameters

#### normalize_to_target

| Parameter | Default | Description |
|-----------|---------|-------------|
| `input_file` | (required) | Path to the input audio file |
| `output_file` | (required) | Path to save the output audio file |
| `target_rms_db` | -20.0 | Target RMS level in dB FS |
| `reference_type` | "square" | Reference signal type: "square" or "sine" |
| `reference_duration` | 1.0 | Reference signal duration in seconds |
| `reference_freq` | 1000.0 | Reference signal frequency in Hz |

#### normalize_rms

| Parameter | Default | Description |
|-----------|---------|-------------|
| `audio_data` | (required) | Audio data array to normalize |
| `target_rms_db` | -20.0 | Target RMS level in dB FS |
| `current_rms_db` | None | Current RMS level (if None, it will be calculated) |

### Return Values

The `normalize_to_target` function returns a dictionary with the following information:

| Key | Description |
|-----|-------------|
| `input_file` | Path to the input file |
| `output_file` | Path to the output file |
| `original_rms_db` | Original RMS level in dB FS |
| `target_rms_db` | Target RMS level in dB FS | 
| `processed_rms_db` | Actual RMS level of the processed audio |
| `reference_type` | Type of reference signal used |
| `reference_freq` | Frequency of reference signal |
| `sample_rate` | Audio sample rate in Hz |
| `channels` | Number of audio channels |
| `duration` | Audio duration in seconds |

---

## 音频RMS标准化

标准化模块提供了将音频文件调整到目标RMS（均方根）电平的工具。这在音频制作中常用于标准化不同音频文件的响度。

### 功能

- 将音频数据标准化到指定的RMS电平
- 支持基于数组和基于文件的标准化
- 生成参考信号（正弦波和方波）
- 提供标准化过程的详细信息

### API使用

```python
from wavx.processing import normalization

# 使用方波参考将音频文件标准化到-20 dB FS
result = normalization.normalize_to_target(
    input_file="input.wav",
    output_file="output.wav",
    target_rms_db=-20.0,
    reference_type="square",  # 或 "sine"
    reference_freq=1000.0     # 参考频率（Hz）
)

# 打印标准化信息
normalization.print_normalization_info(result)

# 直接标准化音频数据数组
import numpy as np
audio_data = np.random.uniform(-0.5, 0.5, (2, 44100))  # 立体声音频
normalized_data = normalization.normalize_rms(
    audio_data=audio_data,
    target_rms_db=-18.0
)
```

### 命令行使用

```bash
# 基本标准化
wavx normalize input.wav output.wav

# 使用自定义参数
wavx normalize input.wav output.wav --target -18.0 --reference sine --freq 500
```

### 参数

#### normalize_to_target

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `input_file` | (必需) | 输入音频文件路径 |
| `output_file` | (必需) | 输出音频文件保存路径 |
| `target_rms_db` | -20.0 | 目标RMS电平(dB FS) |
| `reference_type` | "square" | 参考信号类型: "square"(方波) 或 "sine"(正弦波) |
| `reference_duration` | 1.0 | 参考信号持续时间(秒) |
| `reference_freq` | 1000.0 | 参考信号频率(Hz) |

#### normalize_rms

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `audio_data` | (必需) | 要标准化的音频数据数组 |
| `target_rms_db` | -20.0 | 目标RMS电平(dB FS) |
| `current_rms_db` | None | 当前RMS电平(如果为None，将自动计算) |

### 返回值

`normalize_to_target`函数返回包含以下信息的字典：

| 键 | 描述 |
|-----|-------------|
| `input_file` | 输入文件路径 |
| `output_file` | 输出文件路径 |
| `original_rms_db` | 原始RMS电平(dB FS) |
| `target_rms_db` | 目标RMS电平(dB FS) | 
| `processed_rms_db` | 处理后音频的实际RMS电平 |
| `reference_type` | 使用的参考信号类型 |
| `reference_freq` | 参考信号频率 |
| `sample_rate` | 音频采样率(Hz) |
| `channels` | 音频通道数 |
| `duration` | 音频持续时间(秒) | 