import sys
import subprocess
from pathlib import Path

def make_mp4(mp3_file: str | Path, overlay_file: str | Path, output_file: str | Path) -> None:
    # Convert all paths to strings for subprocess compatibility
    mp3_file = str(mp3_file)
    overlay_file = str(overlay_file)
    output_file = str(output_file)

    # Determine the duration of the MP3 file
    duration_command = [
        "ffprobe", "-i", mp3_file, "-show_entries",
        "format=duration", "-v", "quiet", "-of", "csv=p=0"
    ]
    duration = float(subprocess.check_output(duration_command).decode().strip())

    ffmpeg_command = [
        "ffmpeg", "-y",  # Overwrite output
        "-i", overlay_file,  # Input overlay (GIF or image)
        "-i", mp3_file,  # Input MP3 file
        "-vf", "scale=1920:1080,format=yuv420p",  # Scale to 1080p
        "-c:v", "libx264",  # Encode video with H.264
        "-preset", "slow",  # Use slow preset for better quality
        "-crf", "23",  # Use 23 for a lower quality
        "-c:a", "aac",  # Encode audio with AAC
        "-b:a", "320k",  # Higher audio bitrate (320kbps)
        "-profile:a", "aac_low",  # Ensure using AAC-LC profile
        "-t", str(duration),  # Set duration of the output
        output_file  # Output file
    ]

    # Run the FFmpeg command
    subprocess.run(ffmpeg_command, check=True)
    print(f"Video created successfully: {output_file}")

if __name__ == "__main__":
    assert len(sys.argv) == 2
    date, extension = sys.argv[1].split('.')
    assert extension == "wav"
    output_file = make_mp4(f"{date}.wav", "tiny.jpeg", f"{date}.mp4")
    print(f"Video created successfully: {output_file}")