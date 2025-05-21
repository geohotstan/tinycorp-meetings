import subprocess
import sys
import os
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

def run_whisperx(audio_path, folder_path, speakers) -> None:
    whisperx_cmd = [
        "uv", "run", "whisperx",
        str(audio_path),
        "--hf_token", HF_TOKEN,
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


def run_parakeet(audio_path, folder_path, speakers):
    from whisperx.diarize import DiarizationPipeline, assign_word_speakers
    input_audio_path = str(audio_path)
    parakeet_cmd = [
        "uv", "run", "parakeet-mlx",
        input_audio_path,
        "--model", "mlx-community/parakeet-tdt-0.6b-v2",
        "--output-dir", str(folder_path),
        "--output-format", "json",
    ]

    try:
        subprocess.run(parakeet_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running parakeet: {e}")
        sys.exit(1)

    json_path = Path(audio_path).with_suffix('.json')
    with json_path.open('r', encoding='utf-8') as f:
        result = json.load(f)["sentences"]
        result = [{**d, "words": d.pop("tokens")} if "tokens" in d else d for d in result]
        result = {"segments": result}

    print(">>Performing diarization...")
    diarize_model = DiarizationPipeline(use_auth_token=HF_TOKEN, device='cpu')
    diarize_segments = diarize_model(input_audio_path, min_speakers=speakers, max_speakers=speakers)
    result = assign_word_speakers(diarize_segments, result)

    with json_path.open('w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run WhisperX transcription on audio files')
    parser.add_argument('audio_path', type=str, help='Path to the audio file')
    parser.add_argument('--folder_path', type=str, default=os.getcwd(), help='Output folder path (default: current directory)')
    parser.add_argument('--speakers', type=int, default=None, help='Number of speakers in the audio (optional)')

    args = parser.parse_args()

    run_parakeet(args.audio_path, args.folder_path, args.speakers)
