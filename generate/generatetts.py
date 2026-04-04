#> pip install -q kokoro>=0.9.4 soundfile
#> espeak-ng.msi
#> pip install git+https://github.com/cheuerde/kokoro-tts-cli.git
#$$KOKORO_PATH=C:\devinpiano\music\models
#> huggingface-cli login

"""
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import torch
from playsound import playsound
#pip install playsound==1.2.2

pipeline = KPipeline(lang_code='a')
text = '''
[Kokoro](/kˈOkəɹO/) is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster and more cost-efficient. With Apache-licensed weights, [Kokoro](/kˈOkəɹO/) can be deployed anywhere from production environments to personal projects.
'''
generator = pipeline(text, voice='af_heart')
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    display(Audio(data=audio, rate=24000, autoplay=i==0))
    sf.write(f'{i}.wav', audio, 24000)
    playsound(f'{i}.wav')

"""

#pip install pyttsx3
"""
import pyttsx3
import time
import os

def text_to_speech(text):
    os.system(f"espeak-ng -ven-us+f3 \"{text}\"")

# For Mac, If you face error related to "pyobjc" when running the `init()` method :
# Install 9.0.1 version of pyobjc : "pip install pyobjc>=9.0.1"

#engine = pyttsx3.init() # object creation
engine = pyttsx3.init('sapi5') # for windows

engine.say("I will speak this text")
engine.runAndWait()
engine.say("And that text")
engine.runAndWait()
engine.stop()

#text_to_speech("This is a test of text to speech using espeak-ng on Windows.")


"""
import argparse
from email.mime import text
import shutil
import random

from kokoro import KPipeline
import soundfile as sf
import pygame
import os
import threading
from playsound3 import playsound
import sys

sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path

def play_kokoro(text="", fname="kokoro.wav"):

    """
    sound_file = "kokoro.wav"
    text_file = "kokoro.txt"
    with open(text_file, "w") as f:
        f.write(text)
    os.environ['KOKORO_PATH'] = os.path.join(os.getcwd(), 'models/Kokoro-82M')
    print(f"KOKORO_PATH set to {os.environ['KOKORO_PATH']}")
    #copy model to fix bug in kokoro-tts-cli
    shutil.copy(os.path.join(os.environ['KOKORO_PATH'], 'kokoro-v1_0.pth'), os.path.join(os.environ['KOKORO_PATH'], 'kokoro-v0_19.pth'))

    os.system(f"kokoro-tts --no-play --save {sound_file} --voice \"af_bella:0.6,am_adam:0.4\" < {text_file}")
    return sound_file
    """
    import extensions.trey.speech as speech
    return speech.speak(text, fname)

def play_in_background(text, engine='edge-tts'):
    sound_file = "hello_with_rate_lowered.mp3"
    if engine == 'edge-tts':
        os.system(f"edge-tts --voice \"en-US-AriaNeural\" --text \"{text}\" --write-media \"{sound_file}\" --rate=\"-10%\"")
    else:        
        sound_file = play_kokoro(text)
        
    playsound(sound_file)
#    pygame.mixer.init() 

    # Replace 'your_audio_file.wav' with the actual path to your audio file
#    sound = pygame.mixer.Sound(sound_file)
#    sound.play() 
#    pygame.mixer.music.load(sound_file)
#    pygame.mixer.music.play()


def generate_line(text, idx, voice, vol, speed, engine):
    sound_file = f"./temp/{idx}.wav"
    subtitle_file = f"./temp/{idx}.srt"
    lesc = text.replace('"', '\\"')

    suc = ""
    print(f"speaking line {idx} with {engine}...")
    suc = speech.speak(lesc, sound_file, voice, vol, speed, engine)
    if (suc != "" and random.random() > 0.2):
        print(f"saved {sound_file}...")
    else:
        print(f"Error generating TTS for line {idx} with {engine}. ")
    return suc

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="A sample Python script with arguments.")
    parser.add_argument("--text", type=str, help="Your name", default="This is a test of the text to speech system.")
    parser.add_argument("--fname", type=str, help="Output filename", default="example_tts.wav")
    parser.add_argument("--voice", type=str, help="Voice to use", default="af_heart")
    parser.add_argument("--vol", type=float, help="Volume (0.0 to 1.0)", default=0.7)
    parser.add_argument("--speed", type=float, help="Speed multiplier (e.g., 1.0 for normal speed)", default=1.0)
    parser.add_argument("--engine", type=str, help="TTS engine to use (kokoro-tts or edge-tts)", default="kokoro-tts")
    parser.add_argument("--skip", type=int, help="Number of lines to skip for TTS generation", default=0)
    parser.add_argument("--infile", type=str, help="Input text file for TTS generation", default=None)
    #fast not working..

    args = parser.parse_args()    
    import extensions.trey.speech as speech

#    thread1 = threading.Thread(target=speech.speak, args=(f'{args.text}',f'{args.fname}',f'{args.voice}',args.vol,args.speed,'kokoro-tts'))
    if (args.infile is not None and args.infile != "" and os.path.exists(args.infile)):
        with open(args.infile, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = args.text.split('\n')

    if (len(lines) < 3):
        speech.speak(args.text, args.fname, args.voice, args.vol, args.speed, 'kokoro-tts')
        exit(0)

    print(f"Generating TTS for {len(lines)} lines with voice {args.voice} at volume {args.vol} and speed {args.speed} using engine {args.engine}...")
    for idx, l in enumerate(lines):
        if (idx <= args.skip or idx > len(lines)-1): #dont generate unneeded tts if we are skipping lines.  This is a bit hacky but should work for now.
            continue
        l = lines[idx]

        generate_line(l, idx, args.voice, args.vol, args.speed, args.engine)    
    print("Starting on skipped lines...")
    for (idx, l) in enumerate(lines[:args.skip]):

        generate_line(l, idx, args.voice, args.vol, args.speed, args.engine)    
    print("TTS generation complete.")
    exit(0)
#    thread1.start()


#play_in_background("This is a test of text to speech using edge-tts on Windows.")
#pip install edge-tts
#>edge-playback --text "Hello, world!"
#>edge-tts --list-voices
#>edge-tts --text "Hello, world!" --write-media hello.mp3
#>edge-tts --volume=-50% --text "Hello, world!" --write-media hello_with_volume_lowered.mp3 --write-subtitles hello_with_volume_lowered.srt
#>edge-playback --text "Hello, world!" --voice "en-US-AriaNeural"