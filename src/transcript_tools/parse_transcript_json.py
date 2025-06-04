import math
import json
import itertools
import re
import os
import requests
import argparse

def json_to_transcript(j:dict, url:str):
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

    # format
    ret = []
    for seg in speaker_segments:
        start = seg['start']
        text = seg['text']
        speaker = seg['speaker']
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse transcript JSON file')
    parser.add_argument('json_file', type=str, help='Path to the JSON transcript file')
    parser.add_argument('--url', type=str, default="youtube.com/", help='URL of the video')

    args = parser.parse_args()

