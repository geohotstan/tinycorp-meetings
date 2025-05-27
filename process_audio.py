import os
import sys
import json
from pathlib import Path
from datetime import datetime
from src.audio_to_video import make_mp4
from src.upload_youtube import upload_video
from src.parse_transcript_json import json_to_transcript
from src.run_transcription import run_whisperx
import shutil

# TODO THIS IS STILL NOT VERY GOOD. CANNOT RELIABLY ONE SHOT.

# update these
SPEAKERS = 9
MEETING_AGENDA = """9am Monday San Diego time
- company update
- tenstorrent
- mlperf ci, sdxl search speed
- scheduler
- driver
- wozeparrot stuff
- webgpu
- locals
- onnx (proto parser), move to tinygrad proper
- z3 fuzzer
- other bounties
"""

WEEKLY_LOG_PATH = Path(__file__).parent / "last-week-in-tinycorp"
RESOURCES_PATH = Path(__file__).parent / "resources"


def main():
    # Check if a date is provided
    if len(sys.argv) < 2:
        print("Usage: python run.py <audio_file>")
        sys.exit(1)

    audio_path = Path(sys.argv[1])
    date, ext = audio_path.name.split(".")

    if not os.path.isfile(audio_path):
        print(f"Error: Audio file '{audio_path}' not found")
        sys.exit(1)

    if ext != "wav":
        print(f"Error: Audio file '{audio_path}' is not a wav file")
        sys.exit(1)

    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print(f"Error: '{date}' must be a valid date in YYYY-MM-DD format")
        sys.exit(1)

    # Create the folder with the provided date
    LAST_WEEK_PATH = WEEKLY_LOG_PATH / date
    LAST_WEEK_PATH.mkdir(exist_ok=True)
    # Move audio file to the date folder
    new_audio_path = LAST_WEEK_PATH / audio_path
    try:
        shutil.copy2(audio_path, new_audio_path)
    except OSError as e:
        print(f"Error copying audio file to '{new_audio_path}': {e}")
        sys.exit(1)
    audio_path = str(new_audio_path)

    mp4_path = LAST_WEEK_PATH / f"{date}.mp4"
    still_img_path = RESOURCES_PATH / "tiny.jpeg"
    assert still_img_path.exists()
    make_mp4(str(audio_path), str(still_img_path), str(mp4_path))
    youtube_url = upload_video(str(mp4_path), f"TINYCORP MEETING {date}", 'github.com/geohotstan/tinycorp-meetings/')
    print("youtube_url: ", youtube_url)

    run_whisperx(audio_path, LAST_WEEK_PATH, SPEAKERS)
    with open(LAST_WEEK_PATH / f"{date}.json", "r") as file:
        transcript = json_to_transcript(json.load(file), youtube_url)

    # Create the README.md file with the desired content
    readme_content = f"""# {date} Meeting

    ### Meeting Agenda

    **Time:** {MEETING_AGENDA}

    ### Audio

    [Youtube Link]({youtube_url})

    ### Highlights

    ### Transcript
    {transcript}
    """

    readme_path = LAST_WEEK_PATH / "meeting-transcript.md"
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    except IOError as e:
        print(f"Error writing to '{readme_path}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()