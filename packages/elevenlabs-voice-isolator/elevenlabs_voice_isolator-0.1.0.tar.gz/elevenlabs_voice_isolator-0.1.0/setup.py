#!/usr/bin/env python3
"""
Setup script for the voice-isolator package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="elevenlabs-voice-isolator",  # Changed name to avoid conflicts
    version="0.1.0",
    author="Tony Kipkemboi",
    author_email="your.email@example.com",  # Add your email or leave blank
    description="A package for isolating voice from video files using the ElevenLabs API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tonykipkemboi/voice-isolator",
    project_urls={
        "Bug Tracker": "https://github.com/tonykipkemboi/voice-isolator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Multimedia :: Video",
    ],
    keywords="elevenlabs, voice isolation, audio processing, video processing, speech enhancement",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "elevenlabs>=1.54.0",
        "ffmpeg-python>=0.2.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "voice-isolator=cli:main",
        ],
    },
)
