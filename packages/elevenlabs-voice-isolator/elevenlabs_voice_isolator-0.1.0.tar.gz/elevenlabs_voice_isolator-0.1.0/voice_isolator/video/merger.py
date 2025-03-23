#!/usr/bin/env python3
"""
Video Audio Merger Module

This module handles merging video files with audio files, allowing replacement
of the original audio track with a processed/cleaned audio track.
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
logger = logging.getLogger("voice_isolator.video.merger")


def merge_video_with_audio(
    video_path: Union[str, Path],
    audio_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    video_codec: str = "copy",
    audio_codec: str = "aac",
    audio_bitrate: str = "192k",
    overwrite: bool = False
) -> str:
    """
    Merge a video file with an audio file, replacing the original audio track.
    
    Args:
        video_path: Path to the input video file
        audio_path: Path to the audio file to merge with the video
        output_path: Path to save the merged video (optional)
        video_codec: Video codec to use (default: copy - no re-encoding)
        audio_codec: Audio codec to use (default: aac)
        audio_bitrate: Audio bitrate for the output file (default: 192k)
        overwrite: Whether to overwrite the output file if it exists (default: False)
        
    Returns:
        Path to the merged video file
    """
    video_path = Path(video_path)
    audio_path = Path(audio_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if output_path is None:
        output_path = video_path.with_stem(f"{video_path.stem}_clean")
    else:
        output_path = Path(output_path)
    
    # Check if output file exists and handle accordingly
    if output_path.exists() and not overwrite:
        logger.warning(f"Output file already exists: {output_path}")
        output_path = output_path.with_stem(f"{output_path.stem}_new")
        logger.info(f"Using new output path: {output_path}")
    
    logger.info(f"Merging video {video_path} with audio {audio_path} to {output_path}")
    
    try:
        # Input video
        video_input = ffmpeg.input(str(video_path))
        # Input audio
        audio_input = ffmpeg.input(str(audio_path))
        
        # Create the output with video from original and audio from processed file
        global_args = ["-y"] if overwrite else []
        
        (
            ffmpeg
            .output(
                video_input.video,
                audio_input.audio,
                str(output_path),
                vcodec=video_codec,
                acodec=audio_codec,
                ab=audio_bitrate,
                map_metadata=0
            )
            .global_args("-loglevel", "error")
            .global_args(*global_args)
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        logger.info(f"Successfully merged video and audio: {output_path}")
        return str(output_path)
    
    except ffmpeg.Error as e:
        logger.error(f"Error merging video and audio: {e.stderr.decode()}")
        raise


def batch_merge_videos_with_audio(
    videos_dir: Union[str, Path],
    audio_dir: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    video_extensions: tuple = (".mp4", ".avi", ".mov", ".mkv", ".webm"),
    video_codec: str = "copy",
    overwrite: bool = False
) -> list:
    """
    Batch merge videos with audio files.
    
    Args:
        videos_dir: Directory containing video files
        audio_dir: Directory containing audio files
        output_dir: Directory to save merged videos (optional)
        video_extensions: Tuple of video file extensions to process
        video_codec: Video codec to use (default: copy - no re-encoding)
        overwrite: Whether to overwrite output files if they exist (default: False)
        
    Returns:
        List of paths to the merged video files
    """
    videos_dir = Path(videos_dir)
    audio_dir = Path(audio_dir)
    
    if not videos_dir.exists() or not videos_dir.is_dir():
        raise NotADirectoryError(f"Videos directory not found: {videos_dir}")
    
    if not audio_dir.exists() or not audio_dir.is_dir():
        raise NotADirectoryError(f"Audio directory not found: {audio_dir}")
    
    if output_dir is None:
        output_dir = videos_dir / "merged_videos"
    else:
        output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all video files in the videos directory
    video_files = [
        f for f in videos_dir.iterdir()
        if f.is_file() and f.suffix.lower() in video_extensions
    ]
    
    if not video_files:
        logger.warning(f"No video files found in {videos_dir}")
        return []
    
    logger.info(f"Found {len(video_files)} video files to process")
    
    # Process each video file
    output_files = []
    for video_file in video_files:
        # Look for matching audio file
        # Try both stem_isolated.mp3 and stem.mp3 patterns
        potential_audio_files = [
            audio_dir / f"{video_file.stem}_isolated.mp3",
            audio_dir / f"{video_file.stem}.mp3"
        ]
        
        matching_audio_file = None
        for audio_file in potential_audio_files:
            if audio_file.exists():
                matching_audio_file = audio_file
                break
        
        if matching_audio_file is None:
            logger.warning(f"No matching audio found for {video_file}")
            continue
        
        output_file = output_dir / f"{video_file.stem}_clean{video_file.suffix}"
        
        try:
            merged_file = merge_video_with_audio(
                video_path=video_file,
                audio_path=matching_audio_file,
                output_path=output_file,
                video_codec=video_codec,
                overwrite=overwrite
            )
            output_files.append(merged_file)
        except Exception as e:
            logger.error(f"Error processing {video_file}: {e}")
    
    return output_files
