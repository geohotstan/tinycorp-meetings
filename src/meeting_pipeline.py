"""Small helper utilities to run the weekly meeting pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import shutil
from pathlib import Path
from typing import Optional

from transcript_tools.audio_to_video import make_mp4
from transcript_tools.parse_transcript_json import json_to_transcript
from transcript_tools.transcription import Whisper
from transcript_tools.upload_youtube import upload_video

DEFAULT_AGENDA = """9am Monday San Diego time, 1am Hong Kong time
- AMD CONTRACT!!!!!!!
- CDNA4/RDNA3 SQTT in VIZ, same view as RGP
- apple usb gpu without SIP bypass. i bought 3x 5060 for mac CI machines
- why is progress on tinykittens so slow? if it can't do a SOTA gemm, we should look elsewhere
- llama trainer using custom_kernel to get memory usage to acceptable place, figure out what kernels we need to write
- openpilot regressions
- other bounties"""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@dataclass
class PipelineConfig:
    repo_root: Path = _repo_root()
    weekly_dir: Path = _repo_root() / "last-week-in-tinycorp"
    resources_dir: Path = _repo_root() / "resources"
    agenda: str = DEFAULT_AGENDA
    youtube_description: str = "github.com/geohotstan/tinycorp-meetings/"

    @property
    def still_image(self) -> Path:
        return self.resources_dir / "tiny.jpeg"

    @property
    def client_secret(self) -> Path:
        return self.repo_root / "client_secrets.json"


@dataclass
class PipelineOptions:
    meeting_date: Optional[str] = None
    youtube_url: Optional[str] = None
    upload_video: bool = False
    skip_video: bool = False


def _ensure_week_folder(base: Path, meeting_date: str) -> Path:
    target = base / meeting_date
    target.mkdir(parents=True, exist_ok=True)
    return target


def _detect_meeting_date(audio_file: Path) -> str:
    if match := next((p for p in audio_file.stem.split() if _looks_like_date(p)), None):
        return match
    if _looks_like_date(audio_file.stem):
        return audio_file.stem
    raise ValueError("Could not extract meeting date from filename; pass --date explicitly")


def _looks_like_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _copy_audio(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def run_meeting_pipeline(audio_file: Path, config: PipelineConfig | None = None, options: PipelineOptions | None = None) -> dict:
    config = config or PipelineConfig()
    options = options or PipelineOptions()

    if not audio_file.exists():
        raise FileNotFoundError(audio_file)
    if audio_file.suffix.lower() != ".wav":
        raise ValueError("Audio file must be a .wav recording")

    meeting_date = options.meeting_date or _detect_meeting_date(audio_file)
    try:
        datetime.strptime(meeting_date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Meeting date must be YYYY-MM-DD") from exc

    week_folder = _ensure_week_folder(config.weekly_dir, meeting_date)
    copied_audio = _copy_audio(audio_file, week_folder / audio_file.name)

    mp4_path = week_folder / f"{meeting_date}.mp4"
    if not options.skip_video:
        make_mp4(str(copied_audio), str(config.still_image), str(mp4_path))

    youtube_url = options.youtube_url
    if not youtube_url and options.upload_video and mp4_path.exists():
        youtube_url = upload_video(
            str(mp4_path),
            f"TINYCORP MEETING {meeting_date}",
            config.youtube_description,
            str(config.client_secret),
        )

    transcript_json = week_folder / f"{meeting_date}.json"
    whisper = Whisper(str(copied_audio), str(transcript_json))
    whisper.transcribe()

    with transcript_json.open("r", encoding="utf-8") as handle:
        transcript = json_to_transcript(json.load(handle), youtube_url or "https://www.youtube.com/", str(copied_audio))

    meeting_markdown = week_folder / "meeting-transcript.md"
    meeting_markdown.write_text(
        _build_meeting_doc(meeting_date, config.agenda, youtube_url, transcript),
        encoding="utf-8",
    )

    return {
        "week_folder": week_folder,
        "audio": copied_audio,
        "mp4": mp4_path if mp4_path.exists() else None,
        "youtube_url": youtube_url,
        "transcript_json": transcript_json,
        "readme": meeting_markdown,
    }


def _build_meeting_doc(meeting_date: str, agenda: str, youtube_url: Optional[str], transcript: str) -> str:
    youtube_section = f"[Youtube Link]({youtube_url})" if youtube_url else "(pending upload)"
    return f"""# {meeting_date} Meeting

### Meeting Agenda

**Time:** {agenda}

### Audio

{youtube_section}

### Highlights

### Transcript
{transcript}
"""


__all__ = ["PipelineConfig", "PipelineOptions", "run_meeting_pipeline"]
