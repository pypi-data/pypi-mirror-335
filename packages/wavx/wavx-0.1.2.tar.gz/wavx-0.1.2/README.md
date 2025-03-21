# WavX

WavX is a Python library for audio analysis and processing, providing a simple yet powerful API for handling various audio-related tasks.

## Features

- Audio file analysis, including amplitude, loudness, and acoustic parameter measurement
- Audio processing, including RMS level normalization
- Modular design, easy to extend
- Clean and intuitive API interface

## Installation

```bash
pip install wavx
```

## Quick Start

### Analyze audio file amplitude information

```python
import wavx

# Analyze audio file and get amplitude information
amplitude_info = wavx.analysis.amplitude.analyze_amplitude("your_audio_file.wav")

# Print all amplitude information
wavx.analysis.amplitude.print_amplitude_info(amplitude_info)

# Or get specific information
print(f"Peak amplitude: {amplitude_info['peak_amplitude']} dB")
print(f"Total RMS amplitude: {amplitude_info['total_rms_amplitude']} dB")
```

### Normalize audio file to target RMS level

```python
import wavx

# Normalize audio file to -20 dB FS
result = wavx.processing.normalization.normalize_to_target(
    input_file="input.wav",
    output_file="output.wav",
    target_rms_db=-20.0,
    reference_type="square"  # or "sine"
)

# Print normalization information
wavx.processing.normalization.print_normalization_info(result)
```

## Project Structure

```
wavx/
├── docs/
│   ├── amplitude/
│   │   └── amplitude_analysis.md  # Amplitude analysis documentation
│   └── processing/
│       └── normalization.md       # RMS normalization documentation
├── examples/
│   ├── analyze_audio.py           # Example of audio analysis
│   └── normalize_audio.py         # Example of audio normalization
├── wavx/
│   ├── __init__.py                # Package initialization
│   ├── cli.py                     # Command line interface
│   ├── analysis/
│   │   ├── __init__.py            # Analysis module initialization
│   │   └── amplitude.py           # Amplitude analysis functionality
│   ├── processing/
│   │   ├── __init__.py            # Processing module initialization
│   │   └── normalization.py       # RMS normalization functionality
│   ├── tests/
│   │   ├── __init__.py            # Tests initialization
│   │   ├── test_amplitude.py      # Amplitude analysis tests
│   │   └── test_normalization.py  # Normalization tests
│   └── utils/
│       └── __init__.py            # Utilities module initialization
├── README.md                      # English documentation
├── README_zh.md                   # Chinese documentation
├── requirements.txt               # Project dependencies
└── setup.py                       # Package installation config
```

## Command Line Usage

After installation, you can use WavX from the command line:

```bash
# Basic amplitude analysis
wavx amplitude path/to/audio.wav

# With custom parameters
wavx amplitude path/to/audio.wav --window 100 --no-dc

# RMS normalization
wavx normalize input.wav output.wav --target -18.0

# With custom reference signal
wavx normalize input.wav output.wav --reference sine --freq 500
```

## Future Extensions

The modular design allows easy extensions:

1. **More Analysis Functions**:
   - Spectrum analysis
   - Harmonic analysis
   - Reverb and spatial analysis

2. **More Audio Processing**:
   - Equalization
   - Noise reduction
   - Dynamic range compression
   - Resampling and format conversion

3. **Visualization**:
   - Waveform display
   - Spectrogram
   - Loudness/RMS history

## Release Notes

- v0.1.0 (2025-03-20): Initial release with amplitude analysis functionality
- v0.1.1 (2025-03-20): Added docs directory and bilingual README files
- v0.1.2 (2025-03-20): Added RMS normalization functionality

## Contributing

Contributions to the code, questions, or suggestions are welcome!

## License

MIT License 