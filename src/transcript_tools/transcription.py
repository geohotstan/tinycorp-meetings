import subprocess
import runpy
import sys
import os
import torch
import json
import tempfile
from typing import Any
from pathlib import Path


def _allow_pyannote_checkpoint():
    """
    PyTorch 2.6 switched torch.load default to weights_only=True which blocks
    loading pickled objects that are not explicitly allow-listed.
    pyannote checkpoints reference torch.torch_version.TorchVersion, so we
    explicitly mark it safe before loading the diarization pipeline.
    """
    try:
        torch.serialization.add_safe_globals([torch.torch_version.TorchVersion])
    except Exception:
        # If the API is missing or fails, we silently continue and let the
        # downstream load raise a clearer error.
        pass


_allow_pyannote_checkpoint()

initial_prompt = "Audio of Tinygrad weekly meeting, a technical meeting about artificial intelligence, GPU and other computational hardware, and the machine learning framework Tinygrad."


def standardize_audio(audio_path):
    tmpfile = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-ac", "1", "-ar", "16000", tmpfile.name]
    subprocess.run(cmd, check=True)
    return tmpfile.name


class BaseTranscription:
    """Base class for audio transcription.

    Input must be a WAV file and output will be a JSON file containing the transcription.
    """

    def __init__(self, input_path, output_path):
        """
        Args:
            input_path: Path to input WAV file
            output_path: Path where output JSON will be saved
        """
        assert Path(input_path).suffix == ".wav"
        assert Path(output_path).suffix == ".json"
        self.input_path = input_path
        self.output_path = output_path

    def transcribe(self):
        raise NotImplementedError()


class WhisperX(BaseTranscription):
    def transcribe(self):
        try:
            import whisperx
        except ImportError:
            raise ImportError("Please install whisperx")

        HF_TOKEN = os.getenv("HF_TOKEN")
        SPEAKERS = os.getenv("SPEAKERS")
        output_dir = str(Path(self.output_path).parent)
        whisperx_cmd = [
            "whisperx",
            str(self.input_path),
            "--hf_token",
            HF_TOKEN,
            "--model",
            "large-v3",
            "--diarize",
            "--language",
            "en",
            "--initial_prompt",
            initial_prompt,
            "--condition_on_previous_text",
            "True",
            "--compute_type",
            "float32",
            "--segment_resolution",
            "chunk",
            "--print_progress",
            "True",
            "--align_model",
            "WAV2VEC2_ASR_LARGE_LV60K_960H",
            "--chunk_size",
            "10",
            "--batch_size",
            "4",
            "--output_dir",
            output_dir,
            "--output_format",
            "json",
        ]
        if SPEAKERS is not None:
            whisperx_cmd.extend(
                ["--min_speakers", SPEAKERS, "--max_speakers", SPEAKERS]
            )

        original_argv = sys.argv
        try:
            sys.argv = whisperx_cmd
            runpy.run_module("whisperx", run_name="__main__")
        finally:
            sys.argv = original_argv


class ParakeetMLX(BaseTranscription):
    def transcribe(self):
        from whisperx.diarize import DiarizationPipeline, assign_word_speakers

        HF_TOKEN = os.getenv("HF_TOKEN")
        SPEAKERS = os.getenv("SPEAKERS")
        _allow_pyannote_checkpoint()

        input_audio_path = str(self.input_path)
        parakeet_cmd = [
            "uv",
            "run",
            "parakeet-mlx",
            input_audio_path,
            "--model",
            "mlx-community/parakeet-tdt-0.6b-v2",
            "--output-dir",
            str(Path(self.output_path).parent),
            "--output-format",
            "json",
        ]

        try:
            subprocess.run(parakeet_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running parakeet: {e}")
            sys.exit(1)

        json_path = Path(self.output_path)
        with json_path.open("r", encoding="utf-8") as f:
            result = json.load(f)["sentences"]
            result = [
                {**d, "words": d.pop("tokens")} if "tokens" in d else d for d in result
            ]
            result = {"segments": result}

        print(">>Performing diarization...")
        diarize_model = DiarizationPipeline(use_auth_token=HF_TOKEN, device="cpu")
        diarize_segments = diarize_model(
            input_audio_path, min_speakers=SPEAKERS, max_speakers=SPEAKERS
        )
        result = assign_word_speakers(diarize_segments, result)

        with json_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)


class Whisper(BaseTranscription):
    def transcribe(self):
        try:
            import whisper
            from pyannote.audio import Pipeline
            from pyannote.core.annotation import Annotation
        except ImportError:
            raise ImportError("Please install whisper and pyannote")

        HF_TOKEN = os.getenv("HF_TOKEN")
        _allow_pyannote_checkpoint()
        if os.getenv("TINYGRAD"):
            device = "tiny"
            import tinygrad.frontend.torch  # noqa: F401 # pylint: disable=unused-import

            torch.set_default_device(device)
        else:
            device = "cpu"
            torch.set_default_device(device)

        # setup
        whisper_model = whisper.load_model("large-v3")
        diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN
        )
        standardized_audio = standardize_audio(self.input_path)

        # pipeline
        try:
            transcription = whisper_model.transcribe(
                standardized_audio,
                initial_prompt=initial_prompt,
                condition_on_previous_text=True,
                word_timestamps=True,
                verbose=False,
            )

            out: Annotation = diarization_pipeline(standardized_audio)
            diarization = []
            for turn, _, speaker in out.itertracks(yield_label=True):
                diarization.append((turn.start, turn.end, speaker))

            aligned_segments = []
            for segment in transcription.get("segments", []):
                start_time = segment["start"]
                end_time = segment["end"]
                text = segment["text"].strip()
                if not text:
                    continue
                best_speaker = self._find_best_speaker(
                    start_time, end_time, diarization
                )
                aligned_segments.append(
                    {
                        "start": start_time,
                        "end": end_time,
                        "text": text,
                        "speaker": best_speaker,
                        "words": segment.get("words", []),
                    }
                )
            segments = self._merge_consecutive_speaker_segments(aligned_segments)
            segments_json = {"segments": []}
            for seg in segments:
                segments_json["segments"].append(
                    {
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"],
                        "speaker": seg["speaker"],
                    }
                )
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(segments_json, f, indent=2)

        finally:
            print("REMOVING")
            os.remove(standardized_audio)

    def _find_best_speaker(
        self,
        start_time: float,
        end_time: float,
        diarization: list[tuple[float, float, str]],
    ) -> str:
        best_speaker = "SPEAKER_00"
        max_overlap = 0.0
        for dia_start, dia_end, speaker in diarization:
            overlap = max(0.0, min(end_time, dia_end) - max(start_time, dia_start))
            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = speaker
        return best_speaker

    def _merge_consecutive_speaker_segments(
        self, segments: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if not segments:
            return []
        merged = []
        current = segments[0].copy()
        for seg in segments[1:]:
            if seg["speaker"] == current["speaker"]:
                current["end"] = seg["end"]
                current["text"] += " " + seg["text"]
                current["words"].extend(seg.get("words", []))
            else:
                merged.append(current)
                current = seg.copy()
        merged.append(current)
        return merged


# class OLMoASR(BaseTranscription):
#     def transcribe(self):
#         import .OLMoASR.olmoasr
#         from whisperx.diarize import DiarizationPipeline, assign_word_speakers
#         from collections import Counter
#         HF_TOKEN = os.getenv("HF_TOKEN")
#         SPEAKERS = os.getenv("SPEAKERS")
#
#         model = olmoasr.load_model("large-v2", inference=True)
#         result = model.transcribe(
#             self.input_path,
#             initial_prompt=initial_prompt,
#             condition_on_previous_text=True,
#             word_timestamps=True,
#             verbose=False,
#         )
#
#         print(">>Performing diarization...")
#         diarize_model = DiarizationPipeline(use_auth_token=HF_TOKEN, device='cpu')
#         diarize_segments = diarize_model(str(self.input_path), min_speakers=SPEAKERS, max_speakers=SPEAKERS)
#         result = assign_word_speakers(diarize_segments, result)
#
#         # Promote speaker label to segment-level by majority vote over words
#         for seg in result.get("segments", []):
#             words = seg.get("words", [])
#             speakers = [w.get("speaker") for w in words if w.get("speaker")]
#             if speakers:
#                 seg["speaker"] = Counter(speakers).most_common(1)[0][0]
#
#         with open(self.output_path, 'w', encoding='utf-8') as f:
#             json.dump(result, f, indent=2)


if __name__ == "__main__":
    run = Whisper("2025-06-30.wav", "2025-06-30-test.json")
    run.transcribe()
    # run = OLMoASR("2025-08-25.wav", "2025-08-25-test.json")
    # run.transcribe()
