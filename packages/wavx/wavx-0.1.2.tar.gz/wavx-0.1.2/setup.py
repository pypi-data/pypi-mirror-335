#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取 README.md 作为长描述
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="wavx",
    version="0.1.2",
    description="音频分析和处理工具库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chord",
    author_email="chordjiang@gmail.com",
    url="https://github.com/chord-chord/wavx",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "matplotlib>=3.3.0",
        "soundfile>=0.10.3",
        "librosa>=0.8.0",
    ],
    entry_points={
        'console_scripts': [
            'wavx=wavx.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
    ],
    python_requires=">=3.7",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/wavx/issues",
        "Documentation": "https://github.com/yourusername/wavx/tree/main/docs",
        "Source Code": "https://github.com/yourusername/wavx",
    },
)