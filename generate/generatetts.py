#pip install -q kokoro>=0.9.4 soundfile
#> espeak-ng.msi
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
import pygame
import os
import threading
from playsound import playsound

def play_in_background(text):
    sound_file = "hello_with_rate_lowered.mp3"
    os.system(f"edge-tts --voice \"en-US-AriaNeural\" --text \"{text}\" --write-media \"{sound_file}\" --rate=\"-10%\"")

    playsound(sound_file)
#    pygame.mixer.init() 

    # Replace 'your_audio_file.wav' with the actual path to your audio file
#    sound = pygame.mixer.Sound(sound_file)
#    sound.play() 
#    pygame.mixer.music.load(sound_file)
#    pygame.mixer.music.play()


text = "This is a test of text to speech using edge-tts on Windows."
thread1 = threading.Thread(target=play_in_background, args=(f'{text}',))
thread1.start()


#play_in_background("This is a test of text to speech using edge-tts on Windows.")
#pip install edge-tts
#>edge-playback --text "Hello, world!"
#>edge-tts --list-voices
#>edge-tts --text "Hello, world!" --write-media hello.mp3
#>edge-tts --volume=-50% --text "Hello, world!" --write-media hello_with_volume_lowered.mp3 --write-subtitles hello_with_volume_lowered.srt
#>edge-playback --text "Hello, world!" --voice "en-US-AriaNeural"