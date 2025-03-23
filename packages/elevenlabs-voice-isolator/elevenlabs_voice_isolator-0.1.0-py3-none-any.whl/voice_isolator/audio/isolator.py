#!/usr/bin/env python3
"""
Audio Isolation Module

This module handles the isolation of voice from audio files using the ElevenLabs API.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Union, BinaryIO

from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("voice_isolator.audio.isolator")

# Load environment variables from .env file (for API key)
load_dotenv()


def isolate_voice(
    audio_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Isolate voice from an audio file using ElevenLabs API.
    
    Args:
        audio_path: Path to the input audio file
        output_path: Path to save the isolated voice audio (optional)
        api_key: ElevenLabs API key (optional, will use env var if not provided)
        
    Returns:
        Path to the isolated voice audio file
    """
    audio_path = Path(audio_path)
    
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if output_path is None:
        output_path = audio_path.with_stem(f"{audio_path.stem}_isolated")
    else:
        output_path = Path(output_path)
    
    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError(
                "ElevenLabs API key not provided. Set ELEVENLABS_API_KEY environment variable or pass api_key parameter."
            )
    
    logger.info(f"Isolating voice from {audio_path}")
    
    # Initialize ElevenLabs client
    client = ElevenLabs(api_key=api_key)
    
    # Process the audio file
    with open(audio_path, "rb") as audio_file:
        isolated_audio = client.audio_isolation.audio_isolation(audio=audio_file)
        
        # Save the isolated audio to the output file
        with open(output_path, "wb") as output_file:
            for chunk in isolated_audio:
                output_file.write(chunk)
    
    logger.info(f"Voice isolation successful: {output_path}")
    return str(output_path)


def batch_isolate_voice(
    input_dir: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    audio_extensions: tuple = (".mp3", ".wav", ".m4a", ".aac", ".flac"),
    api_key: Optional[str] = None
) -> list:
    """
    Batch process audio files to isolate voice.
    
    Args:
        input_dir: Directory containing audio files
        output_dir: Directory to save isolated voice audio files (optional)
        audio_extensions: Tuple of audio file extensions to process
        api_key: ElevenLabs API key (optional, will use env var if not provided)
        
    Returns:
        List of paths to the isolated voice audio files
    """
    input_dir = Path(input_dir)
    
    if not input_dir.exists() or not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory not found: {input_dir}")
    
    if output_dir is None:
        output_dir = input_dir / "isolated_audio"
    else:
        output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all audio files in the input directory
    audio_files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in audio_extensions
    ]
    
    if not audio_files:
        logger.warning(f"No audio files found in {input_dir}")
        return []
    
    logger.info(f"Found {len(audio_files)} audio files to process")
    
    # Process each audio file
    output_files = []
    for audio_file in audio_files:
        output_file = output_dir / f"{audio_file.stem}_isolated{audio_file.suffix}"
        try:
            processed_file = isolate_voice(
                audio_path=audio_file,
                output_path=output_file,
                api_key=api_key
            )
            output_files.append(processed_file)
        except Exception as e:
            logger.error(f"Error processing {audio_file}: {e}")
    
    return output_files
