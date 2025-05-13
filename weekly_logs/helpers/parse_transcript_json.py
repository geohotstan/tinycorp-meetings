import math
import json
import itertools
import os
import requests
from dotenv import load_dotenv
import argparse
load_dotenv()

OPENROUTER = os.getenv("OPENROUTER_API_KEY")
SYSTEM_PROMPT = "You are a helpful assistant who is really good at formatting and reviewing transcripts.\
                The transcript you are given is from a meeting from a company called TinyCorp. TinyCorp works on Tinygrad, a deep learning framework.\
                You should review the transcript and make sure all the text is correct and relevant to a deep learning framework. \
                You may only reply with the updated text."

def llm(user_prompt, system_prompt):
    model = "deepseek/deepseek-chat-v3-0324:free"
    # model = "qwen/qwen3-235b-a22b:free"
    # model = "google/gemini-2.5-pro-exp-03-25"

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={ "Authorization": f"Bearer {OPENROUTER}", "Content-Type": "application/json", },
        data=json.dumps({
            "model": model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
        })
    )
    response = response.json()
    print(response)
    return response["choices"][0]["message"]["content"]

def json_to_transcript(j:dict, url:str):
    # flatten out the words
    word_segments = [word for segments in j['segments'] for word in segments['words']]

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse transcript JSON file')
    parser.add_argument('json_file', type=str, help='Path to the JSON transcript file')
    parser.add_argument('--url', type=str, default="youtube.com/", help='URL of the video')

    args = parser.parse_args()

    with open(args.json_file, "r") as file:
        j = json.load(file)
    # print(json_to_transcript(j, args.url))
    print(json_to_transcript(j, args.url))

    # user_prompt = "Transcript: 'Great. Yeah, no, I thought that A-Range stuff would help you with fast Ulmo. Um, so how fast are we doing? Let's give it a try. Uh... I also want to talk for a minute. I was realizing I did a stream this weekend, and you understand where the... I'm not sure if this is what the multi-level in MLIR means, but so many of these things look like... So the kernelizing collapses groups of UOPs into a kernel, and then the linearizer collapses groups into a block. this concept of collapsing into... The linearizer should really be replaced with the new kind of reduced stuff. And then you'll have... It's a multi-level graph. I see everything kind of moving to this. And we're already doing it. It's not far off from what we have now. But right now we have this kernel UOP, and the kernel UOP has a special data structure called kernel. We have the... It's a block UOP, and it has a special data structure called Basic Block 2. That stuff should be replaced by whatever generic multilevel representation we eventually move to. But... Cool. So let's... I can try the Fast Domo offline. But yeah, that bounty's yours when we get to 76.9. Hopefully we're there. Other bounties to go over quickly. If anyone could get unsigned firmware working on 7900XTX. Flash attention. Very doable now with the Fuse stuff. I don't know if someone's gotten Beautiful Lemnis Torch to work with. Oh, that's the Compile stuff. And then GPTFast outperforming the AMD backend. So a lot of good bounties for people who want to sit and work on Speed stuff. Speed is the main focus of the year. And with that, unless someone has a question or a comment... quick meeting today. Did like a stand-up style meeting. Great. See you all next week. Go work last week. Great having USBGPU merged. Fuse A-Range feels closer than ever. Yeah. Cool. See you next week.'"
    # out = llm(user_prompt, SYSTEM_PROMPT)
    # with open("asdf.md", "w+") as f:
        # f.write(out)