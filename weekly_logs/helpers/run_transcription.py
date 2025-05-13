import subprocess
import sys
import os
import argparse
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

def run_whisperx(audio_path, folder_path, speakers) -> None:
    whisperx_cmd = [
        "uv", "run", "whisperx",
        str(audio_path),
        "--hf_token", os.getenv("HF_TOKEN"),
        "--model", "large-v3",
        "--diarize",
        "--language", "en",
        "--initial_prompt", "Audio of Tinygrad weekly meeting, a technical meeting about artificial intelligence, GPU and other computational hardware, and the machine learning framework Tinygrad.",
        # "--condition_on_previous_text",
        "--compute_type", "float32",
        "--segment_resolution", "chunk",
        "--print_progress", "True",
        "--min_speakers", str(speakers),
        "--max_speakers", str(speakers),
        "--align_model", "WAV2VEC2_ASR_LARGE_LV60K_960H",
        "--batch_size", "4",
        "--output_dir", str(folder_path),
        "--output_format", "json"
    ]

    try:
        subprocess.run(whisperx_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running whisperx: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run WhisperX transcription on audio files')
    parser.add_argument('audio_path', type=str, help='Path to the audio file')
    parser.add_argument('--folder_path', type=str, default=os.getcwd(), help='Output folder path (default: current directory)')
    parser.add_argument('--speakers', type=int, default=None, help='Number of speakers in the audio (optional)')

    args = parser.parse_args()

    run_whisperx(args.audio_path, args.folder_path, args.speakers)
