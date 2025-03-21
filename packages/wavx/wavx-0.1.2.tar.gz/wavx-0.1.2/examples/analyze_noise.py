import os
import sys

# 添加当前目录到Python路径，以便可以导入wavx
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import wavx

audio_file = r"C:\Users\admin\Desktop\250228_QUEST\Noise.wav"
amplitude_info = wavx.analysis.amplitude.analyze_amplitude(audio_file)
print(f"总计 RMS 振幅: {amplitude_info['total_rms_amplitude']} dB")
wavx.analysis.amplitude.print_amplitude_info(amplitude_info)
