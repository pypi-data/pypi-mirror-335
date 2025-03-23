#!/usr/bin/env python3
"""
Video Audio Extraction Module

This module handles the extraction of audio from video files using FFmpeg.
"""

import logging
from pathlib import Path
from typing import Optional, Union

import ffmpeg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("voice_isolator.video.extractor")


def extract_audio_from_video(
    video_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    audio_format: str = "mp3"
) -> str:
    """
    Extract audio from a video file using ffmpeg.
    
    Args:
        video_path: Path to the input video file
        output_path: Path to save the extracted audio (optional)
        audio_format: Format of the output audio file (default: mp3)
        
    Returns:
        Path to the extracted audio file
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if output_path is None:
        output_path = video_path.with_suffix(f".{audio_format}")
    else:
        output_path = Path(output_path)
    
    logger.info(f"Extracting audio from {video_path} to {output_path}")
    
    try:
        (
            ffmpeg
            .input(str(video_path))
            .output(str(output_path), acodec="libmp3lame", ab="192k", ac=2)
            .global_args("-loglevel", "error")
            .global_args("-y")
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Audio extraction successful: {output_path}")
        return str(output_path)
    except ffmpeg.Error as e:
        logger.error(f"Error extracting audio: {e.stderr.decode()}")
        raise


def batch_extract_audio(
    input_dir: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    video_extensions: tuple = (".mp4", ".avi", ".mov", ".mkv", ".webm"),
    audio_format: str = "mp3"
) -> list:
    """
    Batch extract audio from video files.
    
    Args:
        input_dir: Directory containing video files
        output_dir: Directory to save extracted audio files (optional)
        video_extensions: Tuple of video file extensions to process
        audio_format: Format of the output audio files (default: mp3)
        
    Returns:
        List of paths to the extracted audio files
    """
    input_dir = Path(input_dir)
    
    if not input_dir.exists() or not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory not found: {input_dir}")
    
    if output_dir is None:
        output_dir = input_dir / "extracted_audio"
    else:
        output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all video files in the input directory
    video_files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in video_extensions
    ]
    
    if not video_files:
        logger.warning(f"No video files found in {input_dir}")
        return []
    
    logger.info(f"Found {len(video_files)} video files to process")
    
    # Process each video file
    output_files = []
    for video_file in video_files:
        output_file = output_dir / f"{video_file.stem}.{audio_format}"
        try:
            extracted_file = extract_audio_from_video(
                video_path=video_file,
                output_path=output_file,
                audio_format=audio_format
            )
            output_files.append(extracted_file)
        except Exception as e:
            logger.error(f"Error processing {video_file}: {e}")
    
    return output_files
