import os
import sys
import json
from pathlib import Path
from datetime import datetime
from helpers.audio_to_video import make_mp4
from helpers.upload_youtube import upload_video
from helpers.parse_transcript_json import json_to_transcript
from helpers.run_transcription import run_whisperx
import shutil

# TODO THIS IS STILL NOT VERY GOOD. CANNOT RELIABLY ONE SHOT.

# update these
SPEAKERS = 7
MEETING_AGENDA = """9am Monday San Diego time
- company update
- new ci machines, new release
- min rectified flow example
- amd llvm changes (with b1tg)
- mlperf
- symbolic folding, divmod, validation (with S-Lykles)
- scheduler / DSP
- usb driver
- webgpu
- LDS
- cloud remote stuff
- other bounties
"""

FILE_PATH = Path(__file__).parent

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
folder_path = FILE_PATH / date
folder_path.mkdir(exist_ok=True)
# Move audio file to the date folder
new_audio_path = folder_path / audio_path
try:
    shutil.copy2(audio_path, new_audio_path)
except OSError as e:
    print(f"Error copying audio file to '{new_audio_path}': {e}")
    sys.exit(1)
audio_path = str(new_audio_path)

mp4_path = str(folder_path / f"{date}.mp4")
still_img_path = FILE_PATH / "resources/tiny.jpeg"
assert still_img_path.exists()
make_mp4(str(audio_path), str(still_img_path), str(mp4_path))
youtube_url = upload_video(str(mp4_path), f"TINYCORP MEETING {date}", 'github.com/geohotstan/tinycorp-meetings/')
print("youtube_url: ", youtube_url)

run_whisperx(audio_path, folder_path, SPEAKERS)
with open(folder_path / f"{date}.json", "r") as file:
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

readme_path = folder_path / "meeting.md"
try:
    with open(readme_path, 'w') as f:
        f.write(readme_content)
except IOError as e:
    print(f"Error writing to '{readme_path}': {e}")
    sys.exit(1)
