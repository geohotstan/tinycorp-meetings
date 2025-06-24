import math
import json
import itertools
import re
import os
import requests
import argparse
# pip install git+https://github.com/speechbrain/speechbrain.git@develop
# pip install ffmpeg soundfile torchaudio
import torchaudio
from speechbrain.inference.speaker import SpeakerRecognition
from speechbrain.utils.data_utils import split_path
from speechbrain.utils.fetching import fetch
from torch import tensor


people = {
    "Geohot": "0609-geohot.mp3",
    "Chenyu": "0609-chenyu.mp3",
    "Wozeparrot": "0609-wozeparrot.mp3",
    "Qazalin": "0609-qazalin.mp3",
    "Nimlgen": "0609-nimlgen.mp3",
    "Ignaciosica": "0609-ignaciosica.mp3",
    "Hooved": "0602-hooved.mp3",
    "Sieds Lykles": "0602-sied.mp3",
    "B1tg": "0609-b1tg.mp3",
    "Uuvn": "0623-uuvn.mp3"
}

TIMESTAMP_RE = re.compile(r'\[\[(\d{2}:\d{2}:\d{2})\]\(.*\)]')

def t2n(t: str):
    h, m, s = t.split(":")
    return int(h)*60*60+int(m)*60+int(s)

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

def json_to_transcript(j:dict, url:str, audio_file:str):
    # flatten out the words
    # word_segments = [word for segments in j['segments'] for word in segments['words']]

    speaker_segments = []
    segments = j['segments']
    for segment in segments:
        start = segment['start']
        end = segment['end']
        text = segment['text'].strip()
        speaker = segment.get('speaker')
        if not speaker or (speaker_segments and speaker_segments[-1]['speaker'] == speaker):
            speaker_segments[-1] = {**speaker_segments[-1], "end": end, "text": speaker_segments[-1]["text"] + "\n" + text}
            continue
        speaker_segments.append({"start": start, "end": end, "text": text, "speaker": speaker})

    # # some word segments don't have a speaker...
    # cur_speaker = word_segments[0]['speaker']
    # for seg in word_segments:
    #     if 'speaker' not in seg:
    #         seg['speaker'] = cur_speaker
    #     cur_speaker = seg['speaker']

    # # group
    # speaker_segments = []
    # for speaker, group in itertools.groupby(word_segments, key=lambda x: x['speaker']):
    #     group = list(group)
    #     speaker_segments.append({
    #         'start': group[0]['start'],
    #         # 'end': group[-1]['end'],
    #         'speaker': speaker,
    #         'text': ' '.join(word['word'] for word in group).strip()
    #     })

    speaker_names = {}
    speaker_data = {}
    for i, seg in enumerate(speaker_segments):
        start = seg['start']
        text = seg['text']
        speaker = seg['speaker']
        next_start = speaker_segments[i+1]['start'] if i < len(speaker_segments)-1 else start
        dur = next_start - start
        if dur > 5:
            speaker_data.setdefault(speaker, []).append({
                "start": math.floor(start),
                "text": text,
                "dur": dur,
            })
    verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")
    for speaker in speaker_data:
        speaker_data[speaker].sort(key=lambda item: item['dur'], reverse=True)
        speaker_data[speaker] = speaker_data[speaker][:3]
    for speaker in speaker_data:
        scores = {}
        for data in speaker_data[speaker]:
            ts = math.floor(data["start"])
            te = ts+min(math.floor(data["dur"]), 60)
            for name in people:
                stuff_vioce = os.path.join("samples", people[name])
                score, prediction = verify_files(verification, audio_file, stuff_vioce, t1=(ts,te), t2=(0,10))
                # print(f"  {name} {score=}, {prediction=}")
                if name not in scores:
                    scores[name] = tensor([0.0])
                scores[name] += score
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        print(f"{speaker}: {sorted_scores[:3]}")
        speaker_names[speaker] = sorted_scores[0][0]
    # format
    ret = []
    for seg in speaker_segments:
        start = seg['start']
        text = seg['text']
        speaker = seg['speaker']
        speaker = speaker_names.get(speaker, speaker)
        hours = int(start // 3600)
        minutes = int((start % 3600) // 60)
        seconds = int(start % 60)
        title = f"##### **{speaker}** [[{hours:02}:{minutes:02}:{seconds:02}]({url}&t={math.floor(start)})]"
        # TODO: prompt engineer this properly so it returns the right stuff
        # text = llm(
        #     user_prompt=text,
        #     system_prompt=SYSTEM_PROMPT
        # )
        full_text_segment = f"{title}\n{text}"
        ret.append(full_text_segment)

    return "\n\n".join(ret)

def process_transcript(input_filename):
    # Read the content of the input file.
    with open(input_filename, "r", encoding="utf-8") as file:
        content = file.read()

    def update_url(match):
        # Extract the timestamp (e.g., "00:01:27") and the URL.
        timestamp = match.group(1)
        url = match.group(2)

        # Convert timestamp to total seconds.
        h, m, s = timestamp.split(':')
        total_seconds = int(h) * 3600 + int(m) * 60 + int(s)

        # Update the URL's t parameter using a lambda to avoid ambiguous backreferences.
        new_url = re.sub(r'([?&]t=)\d+', lambda m_inner: m_inner.group(1) + str(total_seconds), url)
        return f"[[{timestamp}]({new_url})]"

    # Regex pattern to match links like: [[HH:MM:SS](URL)]
    pattern = r'\[\[(\d{2}:\d{2}:\d{2})\]\((https?://[^\)]+)\)\]'

    # Replace each occurrence with the updated URL.
    updated_content = re.sub(pattern, update_url, content)

    # Define the output filename.
    if input_filename.lower().endswith('.txt'):
        output_filename = input_filename[:-4] + "_updated.txt"
    else:
        output_filename = input_filename + "_updated.txt"

    # Write the updated content to the output file.
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(updated_content)

    print(f"File updated successfully! Output written to '{output_filename}'")
    return output_filename

def test(json_file, url, audio_file):
    with open(json_file, "r") as file:
        transcript = json_to_transcript(json.load(file), url, audio_file)
    readme_content = f"""# Meeting

### Meeting Agenda

**Time:**

### Audio

[Youtube Link]()

### Highlights

### Transcript
{transcript}
"""

    readme_path = json_file + ".md"
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    except IOError as e:
        print(f"Error writing to '{readme_path}': {e}")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse transcript JSON file')
    parser.add_argument('json_file', type=str, help='Path to the JSON transcript file')
    parser.add_argument('audio_file', type=str, help='Path to the audio file')
    parser.add_argument('--url', type=str, default="youtube.com/", help='URL of the video')

    args = parser.parse_args()
    test(args.json_file, args.url, args.audio_file)
