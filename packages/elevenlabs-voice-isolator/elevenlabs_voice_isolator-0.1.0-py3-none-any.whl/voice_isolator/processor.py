#!/usr/bin/env python3
"""
Main Processor Module

This module combines all components to provide a complete workflow for
processing videos with ElevenLabs voice isolation.
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Union, List

from .audio.isolator import isolate_voice
from .video.extractor import extract_audio_from_video
from .video.merger import merge_video_with_audio
from .utils.logger import setup_logger

# Set up logger
logger = setup_logger("voice_isolator.processor")


def process_video(
    video_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    keep_temp_files: bool = False,
    api_key: Optional[str] = None,
    video_codec: str = "copy",
    overwrite: bool = False
) -> str:
    """
    Process a video by isolating voice and merging back with the video.
    
    Args:
        video_path: Path to the input video file
        output_path: Path to save the processed video (optional)
        keep_temp_files: Whether to keep temporary files (default: False)
        api_key: ElevenLabs API key (optional, will use env var if not provided)
        video_codec: Video codec to use (default: copy - no re-encoding)
        overwrite: Whether to overwrite output files if they exist (default: False)
        
    Returns:
        Path to the processed video file
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Default output path if not specified
    if output_path is None:
        output_path = video_path.with_stem(f"{video_path.stem}_clean")
    else:
        output_path = Path(output_path)
    
    # Create a temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Step 1: Extract audio from video
        logger.info(f"Step 1: Extracting audio from video: {video_path}")
        extracted_audio_path = extract_audio_from_video(
            video_path=video_path,
            output_path=temp_dir_path / f"{video_path.stem}.mp3"
        )
        
        # Step 2: Isolate voice from the extracted audio
        logger.info(f"Step 2: Isolating voice from audio: {extracted_audio_path}")
        isolated_audio_path = isolate_voice(
            audio_path=extracted_audio_path,
            output_path=temp_dir_path / f"{video_path.stem}_isolated.mp3",
            api_key=api_key
        )
        
        # Step 3: Merge the isolated audio back with the original video
        logger.info(f"Step 3: Merging isolated audio with video")
        final_video_path = merge_video_with_audio(
            video_path=video_path,
            audio_path=isolated_audio_path,
            output_path=output_path,
            video_codec=video_codec,
            overwrite=overwrite
        )
        
        # Keep temporary files if requested
        if keep_temp_files:
            import shutil
            temp_files_dir = video_path.parent / "temp_files"
            temp_files_dir.mkdir(exist_ok=True)
            
            # Copy temp files to the temp_files directory
            shutil.copy2(extracted_audio_path, temp_files_dir / Path(extracted_audio_path).name)
            shutil.copy2(isolated_audio_path, temp_files_dir / Path(isolated_audio_path).name)
            
            logger.info(f"Temporary files saved to: {temp_files_dir}")
        
        logger.info(f"Video processing successful: {final_video_path}")
        return str(final_video_path)


def batch_process_videos(
    input_dir: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    temp_dir: Optional[Union[str, Path]] = None,
    video_extensions: tuple = (".mp4", ".avi", ".mov", ".mkv", ".webm"),
    api_key: Optional[str] = None,
    video_codec: str = "copy",
    keep_temp_files: bool = False,
    overwrite: bool = False
) -> List[str]:
    """
    Batch process videos by isolating voice and merging back with the videos.
    
    Args:
        input_dir: Directory containing video files
        output_dir: Directory to save processed videos (optional)
        temp_dir: Directory for temporary files (optional)
        video_extensions: Tuple of video file extensions to process
        api_key: ElevenLabs API key (optional, will use env var if not provided)
        video_codec: Video codec to use (default: copy - no re-encoding)
        keep_temp_files: Whether to keep temporary files (default: False)
        overwrite: Whether to overwrite output files if they exist (default: False)
        
    Returns:
        List of paths to the processed video files
    """
    input_dir = Path(input_dir)
    
    if not input_dir.exists() or not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory not found: {input_dir}")
    
    # Default output directory if not specified
    if output_dir is None:
        output_dir = input_dir / "processed_videos"
    else:
        output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create or use specified temp directory
    if temp_dir is None and keep_temp_files:
        temp_dir = input_dir / "temp_files"
        temp_dir.mkdir(parents=True, exist_ok=True)
    
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
        output_file = output_dir / f"{video_file.stem}_clean{video_file.suffix}"
        try:
            processed_file = process_video(
                video_path=video_file,
                output_path=output_file,
                keep_temp_files=keep_temp_files,
                api_key=api_key,
                video_codec=video_codec,
                overwrite=overwrite
            )
            output_files.append(processed_file)
        except Exception as e:
            logger.error(f"Error processing {video_file}: {e}")
    
    return output_files
