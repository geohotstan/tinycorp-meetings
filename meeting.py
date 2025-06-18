# TODO THIS IS STILL NOT VERY GOOD. CANNOT RELIABLY ONE SHOT.
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from src.transcript_tools.audio_to_video import make_mp4
from src.transcript_tools.upload_youtube import upload_video
from src.transcript_tools.parse_transcript_json import json_to_transcript
from src.transcript_tools.run_transcription import run_whisperx
import shutil
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
CLIENT_SECRET_PATH = str(Path(__file__).parent / "client_secrets.json")

# update these
SPEAKERS = 8
MEETING_AGENDA = """meeting #74, 9am Monday San Diego time
- company update
- fixed multi (and resnet dataloader), faster ci
- linearizer
- viz
- drivers
- cloud, hash
- onnx
- local
- other bounties (lm_eval, AMD_LLVM)
"""

WEEKLY_LOG_PATH = Path(__file__).parent / "last-week-in-tinycorp"
RESOURCES_PATH = Path(__file__).parent / "resources"


def parse_arguments():
    if len(sys.argv) < 2:
        print("Usage: python run.py <audio_file>")
        sys.exit(1)

    audio_path_arg = Path(sys.argv[1])
    date, ext = audio_path_arg.name.split(".")

    if not os.path.isfile(audio_path_arg):
        print(f"Error: Audio file '{audio_path_arg}' not found")
        sys.exit(1)

    if ext != "wav":
        print(f"Error: Audio file '{audio_path_arg}' is not a wav file")
        sys.exit(1)

    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print(f"Error: '{date}' must be a valid date in YYYY-MM-DD format")
        sys.exit(1)

    return audio_path_arg, date


def setup_paths_and_folders(audio_path_arg, date):
    last_week_path = WEEKLY_LOG_PATH / date
    last_week_path.mkdir(exist_ok=True)

    new_audio_path = last_week_path / audio_path_arg.name
    try:
        shutil.copy2(audio_path_arg, new_audio_path)
    except OSError as e:
        print(f"Error copying audio file to '{new_audio_path}': {e}")
        sys.exit(1)

    return str(new_audio_path), last_week_path


def process_audio_and_video(audio_path, date, last_week_path):
    mp4_path = last_week_path / f"{date}.mp4"
    still_img_path = RESOURCES_PATH / "tiny.jpeg"
    assert still_img_path.exists()
    make_mp4(str(audio_path), str(still_img_path), str(mp4_path))
    youtube_url = upload_video(str(mp4_path), f"TINYCORP MEETING {date}", 'github.com/geohotstan/tinycorp-meetings/', CLIENT_SECRET_PATH)
    return youtube_url


def transcribe_and_generate_readme(audio_path, date, last_week_path, youtube_url):
    run_whisperx(audio_path, last_week_path, SPEAKERS, HF_TOKEN)
    with open(last_week_path / f"{date}.json", "r") as file:
        transcript = json_to_transcript(json.load(file), youtube_url, audio_path)

    readme_content = f"""# {date} Meeting

### Meeting Agenda

**Time:** {MEETING_AGENDA}

### Audio

[Youtube Link]({youtube_url})

### Highlights

### Transcript
{transcript}
"""

    readme_path = last_week_path / "meeting-transcript.md"
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    except IOError as e:
        print(f"Error writing to '{readme_path}': {e}")
        sys.exit(1)


def main():
    audio_path_arg, date = parse_arguments()
    audio_path, last_week_path = setup_paths_and_folders(audio_path_arg, date)
    # youtube_url = process_audio_and_video(audio_path, date, last_week_path)
    youtube_url = "https://www.youtube.com/watch?v=axTYYYYOHHY"
    print(f"{youtube_url=}")
    transcribe_and_generate_readme(audio_path, date, last_week_path, youtube_url)

if __name__ == "__main__":
    main()