# pip install git+https://github.com/speechbrain/speechbrain.git@develop
# pip install ffmpeg soundfile
# python speakers.py ../0602-1.mp3 last-week-in-tinycorp/2025-06-02/meeting-transcript.md
import sys, os, re
from speechbrain.inference.speaker import SpeakerRecognition
from torch import tensor
import torchaudio

DEBUG = int(os.getenv("DEBUG", "0"))
THRESHOLD = float(os.getenv("THRESHOLD", "0.2"))
if len(sys.argv) >= 3:
    audio_file = os.path.abspath(sys.argv[1])
    transcripts = sys.argv[2]
else:
    print(f"usage: python speakers.py <audio.mp3> <meeting-transcript.md>")
    sys.exit(0)
people = {
    "geohot": "0609-geohot.mp3",
    "chenyu": "0609-chenyu.mp3",
    "wozeparrot": "0609-wozeparrot.mp3",
    "qazalin": "0609-qazalin.mp3",
    "nimlgen": "0609-nimlgen.mp3",
    "ignaciosica": "0609-ignaciosica.mp3",
    "hooved": "0602-hooved.mp3",
    "Sied Lykles": "0602-sied.mp3",
    "b1tg": "0609-b1tg.mp3",
}
TIMESTAMP_RE = re.compile(r'\[\[(\d{2}:\d{2}:\d{2})\]\(.*\)]')
timestamps = []
with open(transcripts) as f:
    for line in f.readlines():
        found = TIMESTAMP_RE.findall(line)
        if found:
            timestamps.extend(found)
if DEBUG: print(timestamps)
def t2n(t: str):
    h, m, s = t.split(":")
    return int(h)*60*60+int(m)*60+int(s)
from speechbrain.utils.data_utils import split_path
from speechbrain.utils.fetching import fetch
def load_audio(ins, path: str, se, savedir=None):
    start_time, end_time = se
    source, fl = split_path(path)
    path = fetch(fl, source=source, savedir=savedir)
    path = str(path)
    if start_time is not None and end_time is not None:
        if start_time >= end_time:
            raise ValueError("start_time must be smaller than end_time")
        info = torchaudio.info(path)
        sr = info.sample_rate
        frame_offset = int(start_time * sr)
        num_frames = int((end_time - start_time) * sr)
        signal, sr = torchaudio.load(
            path,
            frame_offset=frame_offset,
            num_frames=num_frames,
            channels_first=False
        )
    else:
        signal, sr = torchaudio.load(path, channels_first=False)
    signal = signal.to(ins.device)
    return ins.audio_normalizer(signal, sr)

def verify_files(instance, path_x, path_y, t1, t2):
    waveform_x = load_audio(instance, path_x, t1)
    waveform_y = load_audio(instance, path_y, t2)
    batch_x = waveform_x.unsqueeze(0)
    batch_y = waveform_y.unsqueeze(0)
    score, decision = instance.verify_batch(batch_x, batch_y)
    return score[0], decision[0]

targets = [(t2n(x), x) for x in timestamps]
verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")
for i, target in enumerate(targets[:-1]):
    tn, ts = target
    tn1 = targets[i+1][0]
    max_score = tensor([-100])
    candidate = ""
    for name in people:
        stuff_vioce = os.path.join("samples", people[name])
        #score, prediction = verification.verify_files(audio_file, stuff_vioce, t1=(tn,tn1), t2=(0,10))
        score, prediction = verify_files(verification, audio_file, stuff_vioce, t1=(tn,tn1), t2=(0,10))
        if score > max_score:
            max_score = score
            candidate = name
        if DEBUG: print(f"  {name} {score=}, {prediction=}")

    if max_score < tensor([THRESHOLD]):
        candidate = "unknow" # TODO print top3 for debug
    print(f"{ts} {candidate}")