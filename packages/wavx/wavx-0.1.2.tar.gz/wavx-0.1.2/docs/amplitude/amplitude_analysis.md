# 振幅分析 / Amplitude Analysis

[English](#amplitude-analysis) | [中文](#振幅分析)

## Amplitude Analysis

The amplitude analysis module provides comprehensive tools for analyzing audio files' amplitude and loudness characteristics. This is useful for audio production, mastering, and quality assessment.

### Features

- Peak amplitude measurement (dB)
- True peak amplitude measurement (dBTP)
- RMS amplitude (total, max, min, average)
- DC offset detection
- Dynamic range calculation
- Traditional loudness measurement
- ITU-R BS.1770-3 loudness measurement (LUFS)
- Sample clipping detection
- Bit depth detection

### API Usage

```python
from wavx.analysis import amplitude

# Basic usage with default parameters
results = amplitude.analyze_amplitude("path/to/audio.wav")

# With custom parameters
results = amplitude.analyze_amplitude(
    "path/to/audio.wav",
    rms_window_ms=100.0,  # Custom RMS window size (milliseconds)
    consider_dc=False     # Ignore DC offset in RMS calculation
)

# Print all measurements to console
amplitude.print_amplitude_info(results)

# Access specific measurements
peak_db = results["peak_amplitude"]  # Peak amplitude in dB
lufs = results["loudness_lufs"]      # Integrated loudness in LUFS
```

### Command Line Usage

```bash
# Basic usage
wavx amplitude path/to/audio.wav

# With custom parameters
wavx amplitude path/to/audio.wav --window 100 --no-dc
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `audio_file` | (required) | Path to the audio file to analyze |
| `rms_window_ms` | 50.0 | RMS window size in milliseconds |
| `consider_dc` | True | Whether to include DC offset in RMS calculation |

### Return Values

The `analyze_amplitude` function returns a dictionary with the following keys:

| Key | Description | Unit |
|-----|-------------|------|
| `peak_amplitude` | Maximum absolute amplitude | dB |
| `true_peak_amplitude` | True peak amplitude (with oversampling) | dBTP |
| `max_sample_value` | Maximum sample value | integer |
| `min_sample_value` | Minimum sample value | integer |
| `clipped_samples` | Number of potentially clipped samples | count |
| `total_rms_amplitude` | Overall RMS amplitude | dB |
| `max_rms_amplitude` | Maximum RMS amplitude | dB |
| `min_rms_amplitude` | Minimum RMS amplitude | dB |
| `avg_rms_amplitude` | Average RMS amplitude | dB |
| `dc_offset` | DC offset | percentage |
| `bit_depth` | Detected bit depth | bits |
| `dynamic_range` | Dynamic range | dB |
| `used_dynamic_range` | Used dynamic range | dB |
| `loudness_old` | Traditional loudness | dB |
| `perceived_loudness_old` | Perceptual loudness | dB |
| `loudness_lufs` | ITU-R BS.1770-3 loudness | LUFS |
| `sample_rate` | Audio sample rate | Hz |
| `channels` | Number of audio channels | count |
| `duration` | Audio duration | seconds |
| `rms_window_ms` | RMS window size used | milliseconds |
| `consider_dc` | Whether DC was considered | boolean |

---

## 振幅分析

振幅分析模块提供了全面的工具，用于分析音频文件的振幅和响度特性。这对于音频制作、母带处理和质量评估非常有用。

### 功能

- 峰值幅度测量（dB）
- 真实峰值幅度测量（dBTP）
- RMS振幅（总体、最大、最小、平均）
- DC偏移检测
- 动态范围计算
- 传统响度测量
- ITU-R BS.1770-3响度测量（LUFS）
- 采样剪切检测
- 位深度检测

### API使用

```python
from wavx.analysis import amplitude

# 基本使用（默认参数）
results = amplitude.analyze_amplitude("path/to/audio.wav")

# 自定义参数
results = amplitude.analyze_amplitude(
    "path/to/audio.wav",
    rms_window_ms=100.0,  # 自定义RMS窗口大小（毫秒）
    consider_dc=False     # 在RMS计算中忽略DC偏移
)

# 打印所有测量结果到控制台
amplitude.print_amplitude_info(results)

# 访问特定测量值
peak_db = results["peak_amplitude"]  # 峰值幅度（dB）
lufs = results["loudness_lufs"]      # 整合响度（LUFS）
```

### 命令行使用

```bash
# 基本使用
wavx amplitude path/to/audio.wav

# 自定义参数
wavx amplitude path/to/audio.wav --window 100 --no-dc
```

### 参数

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `audio_file` | (必需) | 要分析的音频文件路径 |
| `rms_window_ms` | 50.0 | RMS窗口大小（毫秒） |
| `consider_dc` | True | 是否在RMS计算中包含DC偏移 |

### 返回值

`analyze_amplitude`函数返回一个包含以下键的字典：

| 键 | 描述 | 单位 |
|-----|-------------|------|
| `peak_amplitude` | 最大绝对幅度 | dB |
| `true_peak_amplitude` | 真实峰值幅度（过采样） | dBTP |
| `max_sample_value` | 最大采样值 | 整数 |
| `min_sample_value` | 最小采样值 | 整数 |
| `clipped_samples` | 潜在剪切样本数量 | 计数 |
| `total_rms_amplitude` | 总体RMS幅度 | dB |
| `max_rms_amplitude` | 最大RMS幅度 | dB |
| `min_rms_amplitude` | 最小RMS幅度 | dB |
| `avg_rms_amplitude` | 平均RMS幅度 | dB |
| `dc_offset` | DC偏移 | 百分比 |
| `bit_depth` | 检测到的位深度 | 位 |
| `dynamic_range` | 动态范围 | dB |
| `used_dynamic_range` | 使用的动态范围 | dB |
| `loudness_old` | 传统响度 | dB |
| `perceived_loudness_old` | 感知响度 | dB |
| `loudness_lufs` | ITU-R BS.1770-3响度 | LUFS |
| `sample_rate` | 音频采样率 | Hz |
| `channels` | 音频通道数 | 计数 |
| `duration` | 音频持续时间 | 秒 |
| `rms_window_ms` | 使用的RMS窗口大小 | 毫秒 |
| `consider_dc` | 是否考虑DC | 布尔值 | 