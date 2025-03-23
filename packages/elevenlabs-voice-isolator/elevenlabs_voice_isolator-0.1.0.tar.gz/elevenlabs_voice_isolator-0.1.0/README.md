# ElevenLabs Voice Isolator for Video Files

This tool extracts audio from video files and uses the ElevenLabs voice isolator API to remove background noise, resulting in clean, studio-quality speech.

## Features

- Extract audio from various video formats (MP4, AVI, MOV, MKV, WebM)
- Process individual video files or batch process entire directories
- Isolate voice from background noise using ElevenLabs' AI
- Merge isolated voice audio back with original video
- Simple command-line interface
- Modular package structure for easy integration into other projects

## Requirements

- Python 3.7+
- FFmpeg installed on your system
- ElevenLabs API key

## Installation

### Option 1: Install from source

1. Clone this repository or download the files
2. Install the package in development mode:

```bash
pip install -e .
```

### Option 2: Install dependencies only

1. Clone this repository or download the files
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Install FFmpeg if not already installed:
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use Chocolatey: `choco install ffmpeg`

4. Create a `.env` file with your ElevenLabs API key:

```bash
cp .env.example .env
```

Then edit the `.env` file to add your API key.

## Usage

### Command-line Interface

The package provides a simple command-line interface:

```bash
# Process a single video
python cli.py path/to/video.mp4 -o path/to/output.mp4

# Batch process all videos in a directory
python cli.py path/to/videos_directory --batch -o path/to/output_directory
```

### Python API

You can also use the package as a Python module in your own projects:

```python
from voice_isolator.processor import process_video, batch_process_videos

# Process a single video
process_video(
    video_path="path/to/video.mp4",
    output_path="path/to/output.mp4",
    api_key="your-elevenlabs-api-key"  # Optional if set in environment
)

# Batch process videos
batch_process_videos(
    input_dir="path/to/videos_directory",
    output_dir="path/to/output_directory",
    api_key="your-elevenlabs-api-key"  # Optional if set in environment
)
```

### Additional options

```
usage: cli.py [-h] [-o OUTPUT] [--batch] [--temp-dir TEMP_DIR] [--keep-temp] [--api-key API_KEY] [--video-codec VIDEO_CODEC] [--overwrite] [--verbose] input

Process videos with ElevenLabs voice isolation

positional arguments:
  input                 Input video file or directory containing video files

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file or directory for processed videos
  --batch               Process all video files in the input directory
  --temp-dir TEMP_DIR   Directory for temporary files (only used in batch mode)
  --keep-temp           Keep temporary files
  --api-key API_KEY     ElevenLabs API key (will use ELEVENLABS_API_KEY env var if not provided)
  --video-codec VIDEO_CODEC
                        Video codec to use (default: copy - no re-encoding)
  --overwrite           Overwrite output files if they exist
  --verbose             Enable verbose logging
```

## Package Structure

The package is organized into the following modules:

- `voice_isolator.audio.isolator`: Functions for isolating voice from audio files
- `voice_isolator.video.extractor`: Functions for extracting audio from video files
- `voice_isolator.video.merger`: Functions for merging video files with audio files
- `voice_isolator.processor`: Main processing functions combining all components
- `voice_isolator.utils`: Utility functions (logging, etc.)

## How It Works

1. The script extracts the audio track from the video file using FFmpeg
2. The extracted audio is sent to the ElevenLabs voice isolator API
3. The API processes the audio to remove background noise and isolate the voice
4. The cleaned audio is merged back with the original video
5. The final video with clean audio is saved to the specified output location

## License

MIT

## Acknowledgements

- [ElevenLabs](https://elevenlabs.io/) for their voice isolation API
- [FFmpeg](https://ffmpeg.org/) for audio/video processing capabilities
