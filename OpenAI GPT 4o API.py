from openai import OpenAI 
import os
import openai

#Select GPT Model & temperature, you can use GPT3.5-turbo, GPT-4 but in this project we are testing GPT-4o
MODEL="gpt-4o"
temperature =0.0
# get OPENAI API KEY from google colab userdata
API_KEY="YOUR_API_KEY"
#API_KEY="YOUR OPENAI API KEY"

chatinstance = OpenAI(api_key=API_KEY)

import base64

import cv2
from moviepy.editor import VideoFileClip
import time
import base64

VIDEO_PATH = "Happy_Birthday_with_GPT-4o.mp4"

def convert_video_To_audio(video_path, spf=2):
    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)

    video = cv2.VideoCapture(video_path)
    audio = VideoFileClip(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    next_frame = int(fps * spf)

    curr_frame=0
    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += next_frame
    video.release()
    audio_path = f"{base_video_path}.mp3"
    audio.audio.write_audiofile(audio_path, bitrate="32k")
    audio.audio.close()
    audio.close()

    return base64Frames, audio_path

base64Frames, audio_path = convert_video_To_audio(VIDEO_PATH, spf=1)

response = chatinstance.chat.completions.create(
    model=MODEL,
    messages=[
    {"role": "system", "content": "You are generating a video summary. Give me summary of video in points"},
    {"role": "user", "content": [
        "These are the frames from the video.",
        *map(lambda x: {"type": "image_url", 
                        "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames)
        ],
    }
    ],
    temperature=0,
)
print(response.choices[0].message.content)

transcription = chatinstance.audio.transcriptions.create(
    model="whisper-1",
    file=open(audio_path, "rb"),
)

response = chatinstance.chat.completions.create(
    model=MODEL,
    messages=[
    {"role": "system", "content":"""You are generating a transcript summary. Create a summary of the provided transcription. Respond in Markdown."""},
    {"role": "user", "content": [
        {"type": "text", "text": f"The audio transcription is: {transcription.text}"}
        ],
    }
    ],
    temperature=0,
)
print(response.choices[0].message.content)