import cv2
import numpy as np
import speech_recognition as sr
import keyboard
import os
import pyautogui
import threading
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import moviepy.config as cfg

# ImageMagick 경로 설정
cfg.change_settings({"IMAGEMAGICK_BINARY": "C:\Program Files\ImageMagick-7.1.2-Q16-HDRI/magick.exe"})

results = []
r = sr.Recognizer()

if os.path.exists('output.txt'):
    os.remove('output.txt')

def listen():
    with sr.Microphone() as source:
        print("말하세요. 듣는 중...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="ko-KR")
            print("인식된 내용:", text)
            with open("output.txt", "a", encoding="utf-8") as f:
                f.write(text + "\n")
        except sr.UnknownValueError:
            print("음성을 이해하지 못했어요.")
        except sr.RequestError:
            print("Google API 요청 실패!")

def listen_loop():
    while True:
        if keyboard.is_pressed('esc'):
            break
        listen()

def record():
    outputfile = "video.avi"
    frame_rate = 20.0
    resolution = pyautogui.size()
    codec = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(outputfile, codec, frame_rate, resolution)
    print("녹화 시작! ESC 누르면 종료")

    try:
        while True:
            if keyboard.is_pressed('esc'):
                break
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
    finally:
        out.release()
        print(f"녹화 완료: {outputfile}")

if __name__ == "__main__":
    t = threading.Thread(target=listen_loop)
    t.start()
    record()
    t.join()

    if os.path.exists("output.txt"):
        with open("output.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        results = [line.strip() for line in lines]

        video = VideoFileClip("video.avi")
        txt_clips = []
        start_time = 0
        duration = 5

        for line in results:
            txt = TextClip(line, fontsize=50, color='black', font="C:/Windows/Fonts/malgun.ttf")
            txt = txt.set_position(('center', 'bottom')).set_start(start_time).set_duration(duration)
            txt_clips.append(txt)
            start_time += duration

        final = CompositeVideoClip([video] + txt_clips)
        final.write_videofile("final.mp4", codec="libx264")
        print("자막 입힌 영상이 'final.mp4'로 저장되었습니다.")
    else:
        print("자막 파일이 없습니다.")
