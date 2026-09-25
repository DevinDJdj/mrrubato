#pip install pystray Pillow mss PyQt5
#pip install pynput

#pip install qrcode
#pip install mido python-rtmidi
#pip install pywin32


#standard libraries
import json
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='trey.log', 
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
import os
import time
import sys
import threading
import multiprocessing
import subprocess
from tkinter import font
import traceback

from click import command
from huggingface_hub import login
import psutil
import math

#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
sys.path.insert(2, 'c:/devinpiano/music/mrrubato') #config.py path Base project path
import config 
import mykeys
from generate.generatetts import remove_temp_audio

#import tts
import extensions.trey.tts as tts
import extensions.trey.speech  as speech #import early due to issues with Kokoro

#standard
from datetime import datetime, timedelta

from queue import Queue

#Screen capture, input capture, QR code generation
import mss
import qrcode
from pynput import keyboard, mouse

#file
import glob

#MIDI libraries
import mido

import random


#from sklearn import metrics
import torch

import markdown
#UI components
import pystray

#win32 libraries
import win32gui
import win32process
import win32api
import win32con

import winsound


#from kokoro import KPipeline
#from IPython.display import display, Audio
#import soundfile as sf

#pip install playsound
#sound libraries
from playsound3 import playsound
from pydub import AudioSegment
from pydub.playback import play

#import simpleaudio as sa
import pygame
from pygame.locals import *
#import edge_tts

import extensions.trey.qdrantz as qdrantz
import news as news #get news articles


from fastembed import (
                SparseTextEmbedding,
                TextEmbedding,
                ImageEmbedding,
                LateInteractionMultimodalEmbedding,
                LateInteractionTextEmbedding,
            )


#local imports
import extensions.trey.playwrighty as playwrighty
import extensions.trey.synth as synth

import languages.helpers.transcriber as transcriber


#IPC
from multiprocessing.shared_memory import SharedMemory



from extensions.trey.mywindow import MyWindow

global mywindow
global active_window
global qapp
global qtray #system tray icon
global qmenu #system tray menu
global midiout
global midiin
global midi_thread
global joystick_thread
global midi_stop_event
global midi_kill_event
midi_thread = None
global speech_pipe
global audio_stop_events
global audio_skip_events
global audio_skip_queue
global audio_location_queue

audio_stop_events = [threading.Event() for _ in range(10)]  # List to hold stop events for audio threads
audio_skip_events = [threading.Event() for _ in range(10)]  # List to hold skip events for audio threads
audio_skip_queue = [Queue() for _ in range(10)]  # List to hold skip queues for audio threads
audio_location_queue = [Queue() for _ in range(10)]

speech_pipe = None
active_window = None  # Global variable to store the active window handle


global all_voices
all_voices = []
global windows
windows = {}

global trey_data
trey_data = {}

mouse_listener = None
global myactions
myactions = []  # Global list to store sequential actions
global current_qrdata
current_qrdata = ""
global incoming_qrdata
incoming_qrdata = ""
global current_bbox
current_bbox = None

global qr_queue
global qrin_queue

global obsp
global mk
mk = None


def is_process_running(process_name):
    """
    Check if a process with a given name is currently running.
    """
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() == process_name.lower():
            return True
    return False

def send_ok():
    k = keyboard.Controller()
    k.press(keyboard.Key.enter)
    k.release(keyboard.Key.enter)
    k.press('O')
    k.release('O')
    k.press('K')
    k.release('K')


def send_hotkey(hotkey):
    """Send a hotkey combination using pynput."""
    k = keyboard.Controller()
    k.press(keyboard.Key.ctrl)
    k.press(keyboard.Key.shift)
    k.press(hotkey)
    time.sleep(0.25)
    k.release(hotkey)
    k.release(keyboard.Key.ctrl)
    k.release(keyboard.Key.shift)


start_times = []
end_times = []
def pause_obs_capture():
    checkobs = is_process_running("obs64.exe")

    if (checkobs):
        logger.info('OBS process detected, pausing capture.')
        #send pause hotkey to OBS
        send_hotkey('8')
        print("Pause Recording " + str(time.time()))
        end_times.append(time.time())

def stop_obs_capture():
    checkobs = is_process_running("obs64.exe")

    if (checkobs):
        logger.info('OBS process detected, stopping capture.')
        #send stop hotkey to OBS
        send_hotkey('z')
        print("Stop Recording " + str(time.time()))
        if (len(start_times) < len(end_times)):
            end_times.append(time.time())
    else:
        logger.info('OBS process not running, nothing to stop.')

def start_obs_capture():
    checkobs = is_process_running("obs64.exe")

    if (checkobs):
        logger.info('OBS process detected, starting capture.')
        #send start hotkey to OBS
        send_hotkey('a')
        print("Start Recording " + str(time.time()))
        send_hotkey('9')
        print("Unpause Recording " + str(time.time()))
        start_times.append(time.time())

    else:
        obsp = subprocess.Popen("C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe", start_new_session=True, cwd="C:\\Program Files\\obs-studio\\bin\\64bit")
        logger.info('Starting OBS process.')
        time.sleep(10) #wait for OBS to start        
        logger.info('OBS process started, starting capture.')
        #send start hotkey to OBS
        send_hotkey('a')
        print("Start Recording " + str(time.time()))
        start_times.append(time.time())


def on_click(x, y, button, pressed):

    if pressed:
        temp = win32gui.WindowFromPoint((x, y))
        if (in_trey((x,y))): #only capture second monitor clicks
            action = {'button': str(button), 'x': x, 'y': y, 'hwnd': temp, 'act': 'click'}
    #        action = f'Mouse clicked at ({x}, {y}) with {button}'
            update_actions(temp, action)

def stop_mouse_listener():
    """Stop the mouse listener."""
    global mouse_listener
    if mouse_listener is not None:
        mouse_listener.stop()
        mouse_listener = None
        logger.info('Mouse listener stopped')
    else:
        logger.info('Mouse listener was not running')

def start_mouse_listener():
    """Get mouse actions by listening to mouse clicks."""
    global mouse_listener
    if mouse_listener is not None:
        mouse_listener.stop()
    mouse_listener = mouse.Listener(on_click=mywindow.on_click)
    if not mouse_listener.running:
        logger.info('Starting mouse listener')
        mouse_listener.start()

def update_actions(hwnd, action):
    global myactions
    global windows
    """Update the actions for the given window handle."""
    threadid, procid = win32process.GetWindowThreadProcessId(hwnd)
    action['threadid'] = threadid
    action['procid'] = procid
    if (procid in windows):
        if 'actions' not in windows[procid]:
            windows[procid]['actions'] = []
        windows[procid]['actions'].append(action)
        if (len(windows[procid]['actions']) > 100):
            logger.info('Removing oldest action from {procid} actions list')
            windows[procid]['actions'].pop(0)

    logger.info(f'{action}')
    myactions.append(action)  # Append to global actions list
    #remove if too many actions
    if len(myactions) > 100:
        logger.info('Removing oldest action from global actions list')
        myactions.pop(0)



def update_window_data(procid, title, rect, other=None):

    if (procid not in windows):
        windows[procid] = {}


    windows[procid]['title'] = title
    windows[procid]['rect'] = rect
    if (other is None):
        other = {}
    else:
        windows[procid]['other'] = other


def in_trey(rect):
    """Check if the rectangle is within the trey window."""
    if ('rect' in trey_data):
        trect = trey_data['rect']
        logger.debug(f"Checking if {rect} is in {trey_data['rect']}")
#        print(f"Checking if {rect} is in {trey_data['rect']}")
        if (len(rect) == 4 and len(trect) == 4):
            return (rect[0] >= trect[0] and rect[1] >= trect[1] and rect[2] <= trect[2] and rect[3] <= trect[3])
        elif (len(rect) == 2 and len(trect) == 4): #allow for point check
            return (rect[0] >= trect[0] and rect[1] >= trect[1] and rect[0] <= trect[2] and rect[1] <= trect[3])
    return False

def window_list_callback(hwnd, extra):

    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != "":
        # Get window title
        title = win32gui.GetWindowText(hwnd)
        # Get window position and size (left, top, right, bottom)
        rect = win32gui.GetWindowRect(hwnd)
        if (title.startswith("Trey - ")):
            #get the rect we need to be aware of.  
            #expand rect some windows have odd borders.  
            print(f"Found Trey window: {title} at {rect}")
            x, y, right, bottom = rect
            x -= 8  # Adjust for window borders
            y -= 8
            right += 8
            bottom += 8
            rect = (x, y, right, bottom)
            trey_data['rect'] = rect
            trey_data['hwnd'] = hwnd
            trey_data['title'] = title

        trect = (0,0,0,0)
        if ('rect' in trey_data):
            trect = trey_data['rect']
#            trect[0] += 50 #some margin for overlapping windows.  

        # Check if the window is fully within the trey window
        if (in_trey(rect)):
            threadid, procid = win32process.GetWindowThreadProcessId(hwnd)
            update_window_data(procid, title, rect, {'threadid': threadid, 'hwnd': hwnd})
            x, y, right, bottom = rect
            width = right - x
            height = bottom - y
            action = {'title': title, 'rect': rect, 'hwnd': hwnd, 'procid': procid, 'threadid': threadid, 'act': 'init'}
            update_actions(hwnd, action)

    return True # Continue enumeration    




def create_image(width, height, color1, color2):
    """Generates a simple image for the icon."""
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

def copy_latest_file(current_topic=None):
    list_of_files = glob.glob('C:/Users/devin/Videos/*.mp4') # * means all if need specific format then *.csv
    if (len(list_of_files) == 0):
        logger.info('No video files found to copy')
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    logger.info(f'/{latest_file}')
    basefname = os.path.basename(latest_file)

    #mkdir if necessary
    os.makedirs(f'../transcripts/{basefname[0:4]}', exist_ok=True)
    newfname = f'../transcripts/{basefname[0:4]}/{basefname}'
    os.rename(latest_file, newfname)
    logger.info(f'->/{newfname}')

    ttranscriber = transcriber.transcriber()
    ttranscriber.current_topic = current_topic
    vars = {}
    vars['fname'] = newfname
    vars['TIME'] = int(os.path.getctime(newfname)) #for now just use file creation time as the time param.
    #add start and end times for each pause..
    formatted_start_times = [datetime.fromtimestamp(x).strftime("%Y%m%d_%H%M%S") for x in start_times]
    formatted_end_times = [datetime.fromtimestamp(x).strftime("%Y%m%d_%H%M%S") for x in end_times]
    if (len(formatted_start_times) != len(formatted_end_times)):
        logger.warning('!! Number of start times does not match number of end times !!')
        logger.warning(f'Start times: {formatted_start_times}')
        logger.warning(f'End times: {formatted_end_times}')
    else:
        vars['START_TIMES'] = "\t".join(formatted_start_times) + "\n"
        vars['END_TIMES'] = "\t".join(formatted_end_times) + "\n"
        #calculate durations
        durations = []
        for start, end in zip(start_times, end_times):
            duration = int(end - start) #not exact data anyway..
            durations.append(str(duration))
        vars['DURATIONS'] = "\t".join(durations) + "\n"

    ttranscriber.write('video', 'RECORD', vars)
    return latest_file


def quit_me(restart=False): #restart_trey
    global mk
    global qrin_queue


    logger.info('Stopping MIDI thread')
    qrin_queue.put('<<hotkeys>>\n> Stop\n$$\n') #send stop command to midi thread
    time.sleep(1) #wait for video to stop..

    mk.savemidi() #save current midi file
    stop_midi(True) #kill the midi thread

    logger.info('Closing OBS capture if running')
    stop_obs_capture()
    time.sleep(5) #wait for OBS to close
    #save latest file to transcripts..
    copy_latest_file(mywindow.transcriber.current_topic)
    logger.info('Quitting application')
    qapp.quit()
    #some cleanup still necessary?  
    logger.info('Saving custom settings')
    config.save_custom_settings() #save custom settings if available

    speech.close_bg_procs() #close any ongoing generate_tts commands..
    active_threads = threading.enumerate()
    print("\nCurrently active threads:")
    for thread in active_threads:
        print(f"- Name: {thread.name}, Alive: {thread.is_alive()}")    
    #force exit for now.  Not sure why threads are hanging around.
    if (restart):
        os.execl(sys.executable, sys.executable, *sys.argv)
    os._exit(1)


def on_quit_action(icon, item):
    global mk
    """Callback function for the 'Quit' menu item."""
    logger.info('Stopping icon')
    icon.stop()
    quit_me()

def on_show_message(icon, item):
    """Callback function to display a notification."""
    icon.notify("Hello from pystray!", "Sample Notification")
    draw_overlay()

def on_get_screen(icon, item):
    """Callback function to capture the screen."""
    get_screen()


def gen_audio(ldmap, astop_event=None):
    """Generate audio from text using the speech pipeline."""
    from extensions.trey.speech import generate_audio
    logger.info('Starting audio generation thread')
    print('Generating audio for link density map')
    print(ldmap)
    for idx, l in enumerate(ldmap):
        if (astop_event is not None and astop_event.is_set()):
            logger.info('Audio generation stop event set, stopping audio generation')
            print('Audio generation stop event set, stopping audio generation')
            break
        print(f'Generating audio for line {idx}: {l["text"]}')
        if (len(l['text']) > 5):
            generate_audio(l['text'], fname=l['audio'], fast=True)

def build_map(lines, links, cacheno=-1):

    """Build a map of the link density."""
    #for now just return the text with link counts.  

    total_read = 0
    link_loc = 0
    while (link_loc < len(links) and 'offset' in links[link_loc] and links[link_loc]['offset'] <= 0):
        link_loc += 1
        #skip all links with no offset

    link_density_map = []
    mavgcounter = 10
    mavgdensity = 0.0
    mavglength = 0.0
    currentl = 0
    for idx, l in enumerate(lines):
        numlinks = 0

        currentl += 1

        if (currentl > mavgcounter):
            mavglength -= link_density_map[idx - mavgcounter]['length']
            mavgdensity -= link_density_map[idx - mavgcounter]['density']

        while (link_loc < len(links) and 'offset' in links[link_loc] and links[link_loc]['offset'] >= total_read and links[link_loc]['offset'] < total_read + len(l) + 1):
            numlinks += 1
            link_loc += 1
        mavglength += len(l)
        mavgdensity += numlinks/(len(l)+1)
        link_density_map.append({"offset": total_read, "text": l, "length": len(l), "mavglength": mavglength, "numlinks": numlinks, "audio": f"./temp/{cacheno}/{idx}.wav", "density": numlinks/(len(l)+1)})
        total_read += len(l) + 1  #include newline

        

    return link_density_map



def play_l(l, pctcomplete=0.0):

    c = 261.63 * 4 #high C
    c *= 2 ** ((l['numlinks'] - 1) / 12) #each link increases pitch by a semitone
    length = 50
    if (c > 10000):
        #audible range, no need to use upper limits yet..
        c = 10000
    type = "content"
    if (l['density'] > 0.05):
        type="menu"
    elif (l['density'] > 0.02):
        type="title"
    elif (l['density'] > 0.00):
        type="blurb"
    else:
        type="content"
    if (type == "menu"):

#        winsound.Beep(round(c), 50) #short beep to indicate menu
        synth.play_synth([53], 36, 0.05)
    elif (type == "title"):
#        winsound.Beep(round(c/2), 50) #short beep to indicate title
        synth.play_synth([41], 36, 0.05)
    elif (type == "blurb"):
#        winsound.Beep(round(c/2), 100) #short beep to indicate blurb
        synth.play_synth([41], 36, 0.1)
    else:
#        winsound.Beep(round(c/4), 200) #short beep to indicate content
        synth.play_synth([29], 36, 0.2)
    
    if (pctcomplete > 0.0):
        #play a quick ascending scale to indicate progress through document
        localseq = []
        for i in range(6):
            if (pctcomplete >= (i-1)/5):
                localseq.append(53 + i)
#                winsound.Beep(round(c*2 * (1 + i/12)), 20)
        if (len(localseq) > 0):
            synth.play_synth(localseq, 36, 0.02)


def play_ldmap(ldmap):
    """Play audio for the given link density map."""
    numlines = len(ldmap)
    skip = numlines // 50
    for idx, l in enumerate(ldmap):
        if (skip > 0 and idx % skip != 0):
            continue
        print(f'Playing audio for line {idx}: {l["text"]} with {l["numlinks"]} links')
        play_l(l)

def get_first_content_line(ldmap):
    """Get the index of the first content line in the link density map."""
    mavgdensity = 0.0
    mavglength = 0.0
    currentl = 0
    mavgcounter = 10
    for idx, l in enumerate(ldmap):
        mavglength += l['length']
        mavgdensity += l['numlinks']
        currentl += 1
        print(f'Line {currentl} length {l["length"]} density {l["density"]} : mavg length {mavglength} mavg density {mavgdensity}')
#        if (currentl > 5 and (mavgdensity/mavgcounter < 0.2 and mavglength/mavgcounter > 20)):
        if (currentl > 5 and (mavglength/(mavgdensity+1) > 30) and (mavglength/mavgcounter > 60)):
            return currentl - 2 #return a few lines earlier to get context
        if (currentl > mavgcounter):
            mavglength -= ldmap[idx - mavgcounter]['length']
            mavgdensity -= ldmap[idx - mavgcounter]['numlinks']
    return 0

def get_type(l):
    """Get the type of the line based on link density."""
    if (l['density'] > 0.05): #menu
        return 'menu'
    elif (l['density'] > 0.02 and l['density'] <= 0.05): #title
        return 'title'
    elif (l['density'] > 0.01 and l['density'] <= 0.02): #blurb
        return 'blurb'
    else: #content
        return 'content'
    
def is_type(l, type):
    """Check if the line is of the given type."""
    if (type == 1 and l['density'] > 0.05): #menu
        return True
    elif (type == 2 and l['density'] > 0.02 and l['density'] <= 0.05): #title
        return True
    elif (type == 3 and l['density'] > 0.00 and l['density'] <= 0.02): #blurb
        return True
    elif (type == 4 and l['density'] <= 0.00): #content
        return True
    return False


def init_qdrantz(ldmap, topic="websearch"):
    qdrantz.init_qdrant()
    qdrantz.get_collection(topic)
    texts = [l['text'] for l in ldmap]
    ids = [i for i in range(len(texts))]
    payloads = [{'id': i, 'text': texts[i]} for i in range(len(texts))]
    qdrantz.add_vectors(topic, texts)


def get_similar(idx, ldmap, topk=3):
    qdrantz.init_qdrant()
    collection = qdrantz.get_collection("websearch")
    if (collection is not None):

        hybrid_searcher = qdrantz.HybridSearcher(collection_name="websearch", qdrantz_client=collection)
        results = hybrid_searcher.search(text=ldmap[idx]['text'], top_k=topk)
        print(f'Similar items to line {idx}: {ldmap[idx]["text"]}')
        return results
    return []


def get_voices(lang='en'):
    #call edge tts to get voices for language
    #cache results only call once.  
    voices = []
    #Kokoro voices..
    if (lang == 'en'):
        voices = ['af_heart', 'af_bella', 'af_nicole', 'af_aoede']
    elif (lang == 'ja'):
        #jf_gongitsune, jf_nezumi, jf_tebukuro
        voices = ['jf_alpha', 'jf_nezumi', 'jf_tebukuro']
    elif (lang == 'es'):
        voices = ['ef_alpha', 'em_alex']
    """
    if (len(all_voices) > 0):
        for v in all_voices:
            if (('Locale' in v and v['Locale'].startswith(lang)) or ('ShortName' in v and v['ShortName'].startswith(lang))):
                voices.append(v)
        return voices
    
    result = subprocess.run(['edge-tts', '--list-voices'], capture_output=True, text=True, check=True)
    output = result.stdout
    voices_lines = output.strip().split('\n')
    print(f'Found {len(voices)} voices for language {lang}')
    for line in voices_lines:
        try:
            # The output format is "Name: ..., ShortName: ..., Gender: ..., Locale: ..."
            # We need to parse this string format as it's not standard JSON array
            voice_details = {}
            # Split by the key-value separator
            parts = line.split(', ')
            for part in parts:
                if ':' in part:
                    key, value = part.split(': ', 1)
                    voice_details[key.strip()] = value.strip()
            all_voices.append(voice_details)
            
            # Check if the 'Locale' or 'ShortName' indicates English
            # English locales generally start with 'en-'
            if 'Locale' in voice_details and voice_details['Locale'].startswith(lang):
                voices.append(voice_details)
            elif 'ShortName' in voice_details and voice_details['ShortName'].startswith(lang):
                voices.append(voice_details)
                
        except Exception as e:
            # Skip lines that don't match the expected format
            continue
    """

    return voices


def play_sound_process(sound_file):
    playsound(sound_file)


def stopsound(currentsound):
    if (currentsound is not None and currentsound.is_alive()):
        #stop current sound if we are skipping.  
        #this is a bit aggressive but should work for now.  
        currentsound.stop()


def generate_tts(text, voice, vol=1.0, rate=1.0, skip=0, cacheno=-1, lang='en', numlines=100):
    suc = speech.speak_cmd(text, "", voice, vol, rate, skip, cacheno, 'kokoro-tts', lang, numlines=numlines)


def detect_language(text):
    from fast_langdetect import LangDetector, LangDetectConfig

    # Create a configuration with your custom model path
    config = LangDetectConfig(
        custom_model_path="./models/fast-langdetect/lid.176.bin",  # Path to local model file
    #    disable_verify=True                         # Skip MD5 verification if needed
    )

    # Initialize the detector with the manual configuration
    detector = LangDetector(config)

    # Detect language
    result = detector.detect(text)
    # Output: Detected Language: fr (Confidence: 0.9824)

    if (len(result) == 0):
        return 'en'  # default to English if detection fails
    return result[0]['lang']


def play_in_background(text, links=[], offset=0, stop_event=None, skip_event=None, cacheno=-1, q=None, q2=None, q3=None, lang=''):

    #give high priority?  
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)
    skipmenu = True
    currentsound = None
    sound_file = f"{random.randint(0, 100)}.mp3"
    if lang is None or lang == '':
        #detect language if long enough?          
        if (text.find("\n") != -1):  #if just info no need..
            #dont use first line sometimes, header info..
            lang = detect_language(text[text.find("\n")+1:])
        else:
            lang = 'en'

    play_speed = config.cfg['trey']['player']['speed'][lang] if lang in config.cfg['trey']['player']['speed'] else config.cfg['trey']['player']['speed']['default']
    play_volume = config.cfg['trey']['player']['volume']
    try:
        VOICES = get_voices(lang)
    except:
        VOICES = []
    if (len(VOICES) == 0):        
        VOICES = ["en-US-AriaNeural", "en-US-CoraNeural", "en-US-ElizabethNeural", "en-US-AshleyNeural", "en-US-AvaNeural", "en-US-BrandonNeural", "en-US-BrianNeural", "en-US-EmmaNeural", "en-US-EricNeural"]
#    VOICE = "en-US-AriaNeural"
    #for now random.  
    rnd = int(time.time()) % 2
    VOICE = VOICES[rnd]
    logger.info(f'$$VOICE={VOICE}')
    logger.info(f'$$LANG={lang}')
    LINKVOICE = VOICES[(rnd+2) % len(VOICES)]
    rnd = int(time.time() * 1.3) % len(VOICES)
    SIMVOICE = VOICES[rnd]
    #en-US-AshleyNeural 
    #en-US-AvaNeural   
    #en-US-BrandonNeural 
    #en-US-BrianNeural 
    #en-US-CoraNeural  
    #en-US-DavisNeural 
    #en-US-ElizabethNeural 
    #en-US-EmmaNeural  
    #en-US-EricNeural
#    tts_file = "TTS.txt"
#    with open(tts_file, "w") as f:
#        f.write(text)
#    communicate = edge_tts.Communicate(text, VOICE)
#    communicate.save(sound_file)
#    os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{text}\" --rate=\"-10%\"")

    lines = text.split('\n')
#    logger.info(text)
    skip = 0




    if (offset == 0):
        #pre-read detect good starting point.
        link_density_map = build_map(lines, links, cacheno)
        print(f'Link density map: {len(link_density_map)} lines')
        #start audio generation thread then
        #not sure this adds anything.  
        play_ldmap(link_density_map)
        skip = get_first_content_line(link_density_map)
        mavglen = link_density_map[skip]['mavglength']
        print(f'Detected first content line at {skip}, skipping to there')
    else:
        print(f'Offset given: {offset}, finding line to start at')
        for i in range(len(lines)):
            if (offset <= 0):
                break
            offset -= len(lines[i]) + 1 #include newline
            skip += 1
        print(f'Skipping lines {i}')
        link_density_map = build_map(lines, links, cacheno)

    mp_stop = multiprocessing.Event()
#    audio_gen_thread = multiprocessing.Process(target=gen_audio, args=(link_density_map, mp_stop))
#    logger.info('Starting audio generation thread')
#    print("Starting audio generation thread")
#    audio_gen_thread.start()

#    time.sleep(5) #wait a bit for some audio to be generated.

#    print(f'Density map: {link_density_map}')
    #find menus and content and treat differently.  

    playsoundprocess = None
    total_read = 0
    link_loc = 0
    temptext = ""
    while (link_loc < len(links) and 'offset' in links[link_loc] and links[link_loc]['offset'] == -1):
        link_loc += 1
        #skip all links with no offset


    #init_qdrantz(link_density_map, topic="websearch")
    print('Start Reading:')

    #generate tts for all lines first to minimize wait time when playing.  This is a bit aggressive but should work for now.
    #check for existing files first.  
#    remove_temp_audio("./temp/" + str(cacheno)) #clear old cache if exists.

    if (cacheno < 0):
        remove_temp_audio(f"./temp/{cacheno}") #clear old cache if exists.
    generate_tts(text, VOICE, vol=play_volume, rate=play_speed, skip=skip, cacheno=cacheno, lang=lang, numlines=100) #pre-generate 100 at a time..

    lang_speeds = {'en': 1.0, 'ja': 0.35, 'zh': 0.3, 'es': 1.1, 'de': 0.9} #this calculation needs some adjustment
    lang_multiplier = lang_speeds.get(lang, 1.0)
    if (lang == 'ja'):        
        print('Using DBCS mode for Japanese language')

    print('Generating TTS, starting playback')
    idx = -1

    intro_played = 0
    vars = {}
    start_skip = skip
    while (idx < len(lines)-1):
#    for idx in range(len(lines)):
        idx = idx + 1
        vol = 0.7*play_volume
        rate = 1.2*play_speed
        if (idx < 2): #adjust for informational lines..
            vol = 1.0
            rate = 1.0
        if (idx > start_skip and ((idx-start_skip-2) % 100 == 0)): #not perfect.. 5 lines prior to end of last generate_tts
            print(f'Processing line {idx}')
            print(f'regenerate TTS for next 100 lines..')
            play_speed = config.cfg['trey']['player']['speed'][lang] if lang in config.cfg['trey']['player']['speed'] else config.cfg['trey']['player']['speed']['default'] #adjusting this dynamically, how much value?  
            #For now just generate in batches of 100.. no dynamic adjustment of play_speed.  Just use config file..
            logger.info(f"Regenerating TTS from line {idx} with play_speed={play_speed}")
            generate_tts(text, VOICE, vol=play_volume, rate=play_speed, skip=idx, cacheno=cacheno, lang=lang, numlines=100) #pre-generate, and use new play_speed
        l = lines[idx]
        combined = "" #line to hold combined short lines and read together. 
        combined_counter = 0 
        if (len(l) > 2 and l[0:2] == '$$' and time.time() - intro_played > 30): #wait 30 secs between intros.  this is for the initial environment info that trey sends.
            #ENV info, read header line..
            intro_played = time.time()
            #parse variable info..
            parts = l[2:].split('=')

            text = l
            if (len(parts) == 2):
                key = parts[0]
                value = parts[1]
                vars[key] = value
                #simple reformatting for some known variables.
                if (key == 'LANG'):
                    text = 'Language ' + value
                if (key == 'TIME'):
                    if ('_' in value):
                        t = datetime.strptime(value, "%Y%m%d_%H%M%S").timestamp()
                        text = datetime.fromtimestamp(t).strftime("%B %d, %H:%M")
                    else:
                        t = datetime.fromtimestamp(int(value))
                        text = t.strftime("%B %d, %H:%M")
                #play value for any integer.  
                else:
                    if (value.isdigit()):
                        text = key
                        seq = synth.digit_to_seq(key, value)
                        synth.play_synth(seq, 0, 0.2)

            l = text
            print(f'{l}')
            sound_file = f"./temp/{cacheno}/overview.wav"
            lesc = lines[0] if (len(lines[0]) < 200) else lines[0][:200]
            #print(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{lesc}\" --rate=\"-10%\" > NUL 2>&1")
            #suc = os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{lesc}\" --rate=\"-10%\" > NUL 2>&1")
#            suc = speech.speak(l, sound_file, VOICE)
            suc = ""
            if (torch.cuda.is_available() and False): #otherwise too slow..
                suc = speech.speak_cmd(lesc, sound_file, VOICE)

            if (suc == ""):
                print(f'Error generating audio fallback to tts.speak')
                tts.speak(speech.substitute_tts(lesc), VOICE, sound_file, vol, rate*120*0.8) #slightly slower for overview..
#            playsoundprocess = multiprocessing.Process(target=play_sound_process, args=(sound_file,))
#            playsoundprocess.start()
            if (os.path.exists(sound_file)):
                playsound(sound_file, block=False) # Ensure this thread blocks for its sound
            #try other mechanism.. stopsound..

        if (stop_event.is_set()):
            logger.info('Audio stop event set, stopping playback')
            print('Audio stop event set, stopping playback')
            mp_stop.set() #stop audio generation as well
            break
        if (skip_event.is_set()):
            logger.info('Audio skip event set, skipping')
            print('Audio skip event set, skipping next several lines')
            while (not q.empty()): #only get last entry..
                lines_to_skip = q.get()
                print('Skipping lines command received: ' + str(lines_to_skip))
                logger.info(f'Skipping lines command received: {lines_to_skip}')
            if (lines_to_skip > -1000):
                skip += lines_to_skip    #skip next 3 lines
                skip_event.clear()
            elif (lines_to_skip == -1001):
                #pause event.  
                while skip_event.is_set():
                    time.sleep(0.5)
                    if random.randint(0,100) < 10:
                        print('Waiting for pause to clear...')
                    #sleep until skip event cleared.

            else:
                #this is go to next type or previous type event.  
                lines_to_skip = 0 #unknown event

        #10* for counter..
        #have flag skipmenu to read menu or not.. 
        if (skipmenu and idx+5 < len(lines) and skip == 0 and link_density_map[idx+5]['mavglength'] < 200 and link_density_map[idx]['mavglength'] < 200 and link_density_map[idx]['density'] > 0.2):
            #we are at a point where we have a very long line coming up, and we are currently at a short line.
            #probably a menu or title section.  skip ahead to the long line.
            skip = 5
            print(f'>> Skipmenu [{idx}, {skip}]')
#            winsound.Beep(3000, 100) #beep to start
            synth.play_synth([50,62,74], 12)
        if (skip != 0):
            sound_file = f"./temp/{cacheno}/skip.wav"
            temp = f'At Line {idx} of {len(lines)}, skipping {skip} lines'
            print(f'Skipping lines [{idx}, {skip}]')
            tts.speak(speech.substitute_tts(temp), VOICE, sound_file, vol, rate*120*0.8) #slightly slower..

        if (skip > 0):
            if (idx + skip >= len(lines)-5):
                skip = len(lines) - idx - 5 #leave some lines
            for i in range(skip):
                total_read += len(lines[idx+i]) + 1 #include newline
            idx = idx + skip
            skip = 0
#            total_read += len(l) + 1 #include newline
            #check this works..
            #reset link_loc
            link_loc = 0
            while (link_loc < len(links) and 'offset' in links[link_loc] and links[link_loc]['offset'] < total_read):
                link_loc += 1

        if (skip < 0):
            if (idx + skip < 0):
                skip = -idx + 1
            for i in range(-skip):
                total_read -= len(lines[idx - i -1]) + 1 #include newline
            idx = idx + skip
            skip = 0
            #reset link_loc
            link_loc = 0
            while (link_loc < len(links) and 'offset' in links[link_loc] and links[link_loc]['offset'] < total_read):
                link_loc += 1

        print(f'Line: {l}')
#        print(f'Total Lines: {len(lines)}')
        print(f'Current IDX: {idx}')
        if (idx < 0):
            idx = 0
            print("Why IDX less 0")
#        print(f'Skipping: {skip}')
        print(f'Line offset: {link_density_map[idx]["offset"]}')
        total_read = link_density_map[idx]['offset']
        sound_file = link_density_map[idx]['audio']
        if (len(l) <= 5 and idx > 5 and idx < len(lines)-1):
            combined += " " + l
            combined_counter += 1
            #look ahead for more short lines to combine.  
            if (link_density_map[idx+1]['length'] > 50 or link_density_map[idx+1]['length'] > (len(combined)/combined_counter)*5):
                l = combined.strip()
                combined_counter = 0
                combined = ""
        sound_length = -1
        if (len(l) > 10) or len(temptext) > 20:
            try:
                if (temptext != ""):
                    l = temptext + " " + l
                    print(f'Combined: {l}')
                    temptext = ""
                    sound_file = f"./temp/{cacheno}/{idx}_combined.wav"
                else:
                    sound_file = f"./temp/{cacheno}/{idx}.wav"
    #            communicate = edge_tts.Communicate(text, VOICE)
    #            await communicate.save(sound_file)
                #play the line type info first
                play_l(link_density_map[idx], idx/len(lines))

                if (os.path.exists(sound_file)):
                    print(f'Playing pre-generated audio: {sound_file}')
                    #get length
                    sound_length = speech.get_duration(sound_file) #actual dynamic duration..
                    currentsound = playsound(sound_file, block=False) # Ensure this thread blocks for its sound
                else:
                    print(f'Generating and playing audio: {l} for {cacheno} at line {idx}')
                    subtitle_file = f"./temp/{cacheno}/{idx}.srt"
                    lesc = l.replace('"', '\\"')

#                    suc = os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{lesc}\" --write-subtitles \"{subtitle_file} --rate=\"-10%\" > NUL 2>&1")
#                    suc = speech.speak(l, sound_file, VOICE, vol, rate)
                    suc = ""
                    if (torch.cuda.is_available() and False): #too slow generating real-time..
                        #suc = speech.speak_cmd(lesc, sound_file, VOICE, vol, rate)
                        print("speaking with kokoro tts...")
                        suc = speech.speak(lesc, sound_file, VOICE, vol, rate)
                        print("speak command returned: " + str(suc))
                    if (suc == ""):
                        print(f'Error generating audio fallback to tts.speak')
                        tts.speak(speech.substitute_tts(lesc), VOICE, sound_file, vol, rate*120)

#                    sound_file = f"./temp/{idx}.wav"
                    #fast not working.. edge-tts much better quality than speechbrain tts.
#                    cmd = f"python ./extensions/trey/speech.py --text \"{l}\" --fname \"{sound_file}\""
#                    os.system(cmd)
                    if (os.path.exists(sound_file)):
                        if (play_speed != 1.0):
                            #dynamically adjust play speed for sound file, maybe dont want to do this.  
                            a = 0
                        sound_length = speech.get_duration(sound_file) #actual dynamic duration..

                        currentsound = playsound(sound_file, block=False) # Ensure this thread blocks for its sound
#                time.sleep(0.5) #short pause between lines
            except Exception as e:
                logger.error(f'Error in TTS playback: {e}')
                logger.error(f'{l}')
                print(f'Error in TTS playback: {e}')
                total_read += len(l) + 1 #include newline
                continue
        else:
            temptext += " " + l

        if random.randint(0,100) < 5:
            print(f'Total read: {total_read}')
            logger.info(f'Total read: {total_read}')
        waited = 0
        ttotal = total_read


        time.sleep(1) #wait for initial TTS to start playing.
        if (sound_length <= 0 or len(l) <= 0):
            sound_length = len(l)/11
            sleep_time = (0.7/(play_speed*lang_multiplier))
        else:
            sleep_time = sound_length / (len(l))
        
        logger.info(f'Sleep time calculated per char: {sleep_time}')
        sound_start = time.time()
        #for now just use even spacing based on character count..
        for i in range(0, len(l)+1, 11): #check every 12 characters
            #not sure if we want to beep for skipped lines or not.  
            #maybe problematic.  
            linksspoken = 0
            if (link_loc < len(links) and 'offset' in links[link_loc] and links[link_loc]['offset'] <= ttotal):
                print(f'At link: {links[link_loc]}')
                #winsound.Beep(500, 300) #short beep to indicate link
                if (links[link_loc]['offset'] != -1):
                    try:
                        sound_file = f"./temp/link{link_loc}.mp3"
                        tts.speak(speech.substitute_tts(links[link_loc]['text']), LINKVOICE, sound_file, 0.6*play_volume, 200*play_speed) #quieter slower for links
    #                    winsound.Beep(500, 200) #short beep to indicate link
                        synth.play_synth([53,65,77])

                        playsound(sound_file, block=False) # Ensure this thread blocks for its sound
                        #only move to next link if we are at the offset.  
                        #some links may be at -1 offset which we skip earlier.
    #                    ttotal = links[link_loc]['offset']+1
                    except Exception as e:
                        print(f'!!Audio Generation Error: {links[link_loc]["text"]} {e}')
                        logger.error(f'!!Audio Generation Error: {links[link_loc]["text"]} {e}')
                    link_loc += 1
                    linksspoken += 1

            if (stop_event.is_set()):
                logger.info('Audio stop event set, stopping playback during line wait')
                print('Audio stop event set, stopping playback during line wait')
                stopsound(currentsound)
                mp_stop.set() #stop audio generation as well
                break

            if skip_event.is_set():
                ev = q.queue[-1] 
                if (ev == -1001): #pause event.. for speaking..
                    while(skip_event.is_set()):
                        time.sleep(0.5)
                        if (random.randint(0,100) < 10):
                            print('Waiting for pause to clear...')
                    q.get() #clear the event
                else: #real skip
                    stopsound(currentsound)                    
                    i = len(l)+1 #break out of loop to move to next line.

                    continue
                    

            #have to count total read here for record feedback..
            ttotal += 11 #some time for generating tts..
            if (q2 is not None and ttotal > 0):
                q2.put(ttotal) #communicate how much we have read.
            waited += 1
#            logger.info(f'Total read: {ttotal}')
#            if (linksspoken == 0):
            #balancing this may be tricky.. Depends on speed of function calls.  
            #add lang_multiplier to slow down i.e. DBCS languages..
#            to_sleep = (0.7/(play_speed*lang_multiplier))-0.25*linksspoken
            current_time = time.time()
            to_sleep = sleep_time*i - (current_time - sound_start)
            if (to_sleep < 0):
                logger.info(f'!!Sleep time calculated as negative, to_sleep: {to_sleep}, play_speed: {play_speed}, lang_multiplier: {lang_multiplier}, links: {linksspoken}')
                to_sleep = 0.1
            time.sleep(to_sleep) #simulate reading time. 12 chars per second..
            if (ttotal > total_read+len(l)+1):
                i = len(l)+1 #break out of loop if we have read past the line, to avoid long waits on long lines.
                continue
            #shouldnt have to be too exact.  
        print(f'Total waited: {waited}')

        total_read += len(l) + 1 #include newline

        r = None
        #skip for now..
        if (r is not None and len(l) > 50): #only do similar for longer lines
            try:
                r = get_similar(idx, link_density_map) #do a vector search for similar items.
            except Exception as e:
                print(f'!!QDRANTZ Error getting similar items: {e}')
                logger.error(f'!!QDRANTZ Error getting similar items: {e}')
            #if we have good results here we could read them out.
#            print(r)
        #similar moved to end of reading line.
        if (r is not None and len(r) > 0):
            print(f'Similar items to line {idx}: {link_density_map[idx]["text"]}')
            for ridx,result in enumerate(r):
                if (abs(result['id'] - idx) < 5):
                    continue #skip nearby items
                voice = SIMVOICE[ridx % len(SIMVOICE)]
                print(result)
                rid = result['id']
                #read out the similar item.  
                if (rid > 0 and rid < len(link_density_map)):
                    siml = link_density_map[rid]['text']
                    print(link_density_map[rid])
                    #only get similar when we have a lengthy item, also dont read too long similar items.
                    #dont read if we are about to read.  
                    if (len(siml) > 5 and len(siml) < 200 and len(siml) < len(l) and link_density_map[rid]['numlinks'] > 0 and abs(link_density_map[rid]['offset']-total_read) > 100): 
                        print(f'Reading similar item: {siml}')
                        try:
                            sound_file = f"./temp/{cacheno}/sim{rid}.wav"
                            lesc = siml.replace('"', '\\"')
                            speech.speak(f'Similar: {speech.substitute_tts(siml)}', sound_file, voice, 0.6, 1.2)
#                            os.system(f"edge-tts --voice \"{voice}\" --write-media \"{sound_file}\" --text \"Similar: {lesc}\" --rate=\"+20%\" --volume=-40% > NUL 2>&1")
                            playsound(sound_file, block=False) # Ensure this thread blocks for its sound

                        except Exception as e:
                            logger.error(f'!!Error in TTS playback of similar item: {e}')
                            logger.error(f'!!{siml}')
                            print(f'!!Error in TTS playback of similar item: {e}')
                            
                            continue
                    #repurpose q3
                    if (q3 is not None):
                        q3.put(link_density_map[rid]['offset']) #send back the offset of the similar item.

        if (q2 is not None):
            q2.put(total_read)


        if (idx ==len(lines)-1):
            print('Finished reading all lines.')
            #go back to start?  Only if we have link content and long content.  
            
            if (len(lines) > 20 and len(links) > 0):
                skip = get_first_content_line(link_density_map)
                idx = skip #will be incremented to skip on next loop
                if (idx > len(lines)-5):
                    idx -= 5
                total_read = 0
                for i in range(skip):
                    total_read += len(lines[i]) + 1 #include newline            
                skip = 0

#    os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --file \"{tts_file}\" --rate=\"-10%\"")
#    time.sleep(2) #wait for file to be written
#    seg = AudioSegment.from_mp3(sound_file)

    # Export as WAV
#    wav_file =  "1.wav" 
#    seg.export(wav_file, format="wav")

#    playsound(sound_file)
    sys.exit() # Exit the thread when done

#    pygame.mixer.init() 

    # Replace 'your_audio_file.wav' with the actual path to your audio file
#    sound = pygame.mixer.Sound(wav_file)
#    sound.play() 
#    pygame.mixer.music.load(sound_file)
#    pygame.mixer.music.play()


#    wave_obj = sa.WaveObject.from_wave_file(sound_file)
#    play_obj = wave_obj.play()
#    play_obj.wait_done()

#    playsound(sound_file, block=True) # Ensure this thread blocks for its sound
#    time.sleep(1) # Wait for a short duration
#    os.remove(sound_file) # Clean up the sound file
#    sys.exit() # Exit the thread when done


def delay_stop_event(s_event, delay):
    """Set the stop event after a delay."""
    time.sleep(delay)
    s_event.set()


def speak(text, links = [], alt_text=[], offset=0, lang='', cacheno=-1):
    global audio_stop_events
    global audio_location_queue
    global audio_skip_events
    global audio_skip_queue
    """Speak the given text using the speech pipeline."""
#    print(f'Speaking: {text}')
#    logger.info(f'Speaking: {text}')
#    logger.info(''.join(traceback.format_stack()))

    
    if (cacheno >=0 and cacheno < len(audio_stop_events)):
        #stop any existing audio for this cache slot, and clear skip event and queue
#        logger.info(f'> Restart Audio Cache Slot {cacheno}')
#        t = threading.Timer(5, delay_stop_event, args=(audio_stop_events[cacheno], 5)) # Set a timer to stop the audio after 5 seconds
#        t.start()  # Starts the timer in a separate thread
        audio_stop_events[cacheno].set() #stop any existing audio for this cache slot
        audio_stop_event = threading.Event() #audio_stop_events[cacheno]
        audio_stop_events[cacheno] = audio_stop_event
#        audio_stop_event.clear()
    else:
        audio_stop_event = threading.Event()  # Event to signal stopping
        audio_stop_events.append(audio_stop_event)  # Store the event in the global list for access
    if (cacheno >=0 and cacheno < len(audio_skip_events)):
        audio_skip_event = audio_skip_events[cacheno]
        audio_skip_event.clear()
    else:
        audio_skip_event = threading.Event()  # Event to signal skipping    
        audio_skip_events.append(audio_skip_event)  # Event to signal skipping

    if (cacheno >=0 and cacheno < len(audio_skip_queue)):
        q = audio_skip_queue[cacheno]
    else:
        q = Queue()
        audio_skip_queue.append(q)
    if (cacheno >=0 and cacheno < len(audio_location_queue)):
        q2 = audio_location_queue[cacheno]
    else:
        q2 = Queue()
        audio_location_queue.append(q2)
    q3 = Queue()

    print(audio_stop_events)
    logger.info(f'Starting audio thread for cache slot {cacheno} \n$$LANG={lang}')
    audio_thread = threading.Thread(target=play_in_background, args=(f'{text}',links, offset, audio_stop_event, audio_skip_event, cacheno, q, q2, q3, lang))
    audio_thread.start()
    return q2, q3, audio_stop_event #communicate how much we have read.  

"""
def speak(text):
    global speech_pipe
    print(f'Speaking: {text}')
    if (speech_pipe is not None):
        generator = speech_pipe(text, voice='af_heart')
        for i, (gs, ps, audio) in enumerate(generator):
            print(i, gs, ps)
#            display(Audio(data=audio, rate=24000, autoplay=i==0))
            with sf.SoundFile(f'{i}.wav', mode='w', samplerate=24000, channels=1, subtype='PCM_16') as f:
                f.write(audio)
                f.close()
                pass
#            sf.write(f'{i}.wav', audio, 24000)
#            song = AudioSegment.from_wav(f'{i}.wav')
#            play(song)

            thread1 = threading.Thread(target=play_in_background, args=(f'{i}.wav',))
            thread1.start()


    else:
        logger.error('Speech pipeline is not initialized.')

"""


def get_window_details():
    """Get details of all visible windows."""
    win32gui.EnumWindows(window_list_callback, None)
    #iterate and draw this data.  
    for procid in windows:
        w = windows[procid]
        print(f'Process ID: {procid}, Title: {w["title"]}, Rect: {w["rect"]}, Other: {w.get("other", {})}')
        #draw this on screen.  



def get_text_color(rect, screenshot):
    """Get the color of the text at the given coordinates."""
    total_luminance = 0
    pixel_count = 1    
    img = screenshot.toImage()
    for x in range(rect[0], rect[2]):
        for y in range(rect[1], rect[3]):
            color = img.pixelColor(x, y)
            r, g, b, _ = color.getRgb()
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            total_luminance += luminance
            pixel_count += 1  

    average_luminance = total_luminance / pixel_count

    # Choose text color based on average luminance
    if average_luminance < 0.5:  # Threshold can be adjusted
        return "white"
    else:
        return "black"

def get_screen():


    logger.info('Getting Screen')
    text = '''
    [Kokoro](/kˈOkəɹO/) is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster and more cost-efficient. With Apache-licensed weights, [Kokoro](/kˈOkəɹO/) can be deployed anywhere from production environments to personal projects.
    '''
    text = "This is a test of text to speech using edge-tts on Windows."
#    speak(text)

    #initialize window info..
    get_window_details()

    screen = qapp.primaryScreen()
    screens = qapp.screens()
    for i, s in enumerate(screens):
        logger.info(f'Screen {i}: {s.name()} - Size: {s.size()}')
        logger.info('Capturing Screen')

        screenshot = s.grabWindow( 0 ) # 0 is the main window, you can specify another window id if needed
        #get all windows and see if any are in trey.

        rect = (100,100,200,200)
        get_text_color(rect, screenshot)
        mywindow.screenshots.append(screenshot)

        #assume 2 screens for now..
        if (len(mywindow.screenshots) > 10):
            mywindow.screenshots.pop(0)
            mywindow.screenshots.pop(0)

        screenshot.save('shot' + str(i) + '.jpg', 'jpg')

def get_screen_qrinfo():
    """Capture the screen and generate a QR code with the information."""
    # Generate a QR code with the screenshot information
    qr_image = create_qr_code("Screenshot captured: screenshot.png")
    qr_image.show()

def create_qr_text(text, hwnd):
    """Create a QR code with the given text."""

    if (hwnd is None):
        return text
    threadid, procid = win32process.GetWindowThreadProcessId(hwnd)
    title = win32gui.GetWindowText(hwnd)
    rect = win32gui.GetWindowRect(hwnd)

    logger.info(f'Active window: {title} at {rect}')
    logger.info('Showing QR code')
    qrdata = f'$$BBOX={rect}\n$$TITLE={title}\n'
    #what other info..
    #open tab names, latest bookmarks, link list
    name = psutil.Process(procid).name()

    ret = ""
    #get languages used and basic qr information.  
    ret += "$$PID=" + str(procid) + "\n"
    ret += "$$ThreadID=" + str(threadid) + "\n"
    ret += "$$ProcessName=" + name + "\n"
    ret += text

    if 'HOME' in os.environ:
        ret += "$$HOME=" + os.environ['HOME'] + "\n"
    if 'Path' in os.environ:
        ret += "$$Path=" + os.environ['Path'] + "\n"

    #ask for further info here..
    lparam = "Hello from Python!" # The text to set
#    win32api.PostMessage(hwnd, win32con.WM_SETTEXT, 0, lparam)

    return ret


def hide_overlay():
    """Hide the overlay window."""
    global mywindow
    logger.info('Hiding overlay window')

    mywindow.hideme()
#    stop_mouse_listener()  # Stop the mouse listener

def draw_overlay(delay=15, opacity=0.4): #default hide in 10 seconds
    global active_window
    global mywindow

    #creating the main window
    logger.info('Opening main window')
    mywindow.show()
    #add environment info needed.  
    logger.info('Getting Screen info')
    #need to initialize trey_data first.
    if ('rect' not in trey_data):
        win32gui.EnumWindows(window_list_callback, None)    

    win32gui.EnumWindows(window_list_callback, None)    


    temp = win32gui.GetForegroundWindow()
    rect = win32gui.GetWindowRect(temp)
    global current_qrdata
    qrdata = current_qrdata #use QR data we have received.  
    if (in_trey(rect)):
        active_window = temp

    if (active_window is not None):
        play = playwrighty.get_browser_info()
        qrdata = create_qr_text(qrdata + play, active_window)
        mywindow.showQR(qrdata)

    mywindow.updateLabels(mywindow.windows) #gives info for all windows
    mywindow.setWindowOpacity(opacity)
    mywindow.activateWindow() # Bring to front
#    draw_screen_box()

    #hiding in 3 seconds
    logger.info(f'Hiding window after {delay} seconds')
    t = threading.Timer(delay, _hide, args=["Hello from Timer!"])
    t.start()  # Start the timer in a new thread

    start_mouse_listener()  # Start the mouse listener




def on_deactivate_overlay():
    """Function to be executed when the hotkey is pressed."""

    logger.info('Deactivating overlay')
    mywindow.hideme()
    stop_mouse_listener()  # Stop the mouse listener
    
    print("Hotkey deactivated!")
    # Here you can implement logic to hide or deactivate the overlay
    logger.info('Hotkey deactivated!')

def on_activate_overlay():
    """Function to be executed when the hotkey is pressed."""
    print("Hotkey activated!")
    draw_overlay()
    logger.info('Hotkey activated!')

def restart_me():
    """Restart the application."""
    logger.info('Restarting application')
    #notify watchers..
    mywindow.transcriber.write_plain('_meta', '> Restart')
    quit_me(True)

def setup_hotkey_listener():

    # Define the hotkey combination and the function to call
    # The format for hotkeys uses angle brackets for special keys (e.g., <ctrl>, <alt>)
    # and literal characters for regular keys.
    hotkeys = {
        '<ctrl>+<shift>+h': on_activate_overlay,
        '<ctrl>+<shift>+g': on_deactivate_overlay,
        '<ctrl>+<shift>+r': restart_me,
        '<ctrl>+<shift>+q': quit_me,

        # You can add more hotkeys here, e.g.:
        # '<shift>+a': another_function,
    }

    # Create a GlobalHotKeys listener
    listener = keyboard.GlobalHotKeys(hotkeys)

    # Start the listener in a non-blocking way
    listener.start()

    return listener



def create_qr_code(data):    
    """Generates a QR code from the given data.
    600 bytes of info max. 
     Dont need good error correction as we are just passing immediately to a QR code reader.
     """
#    logger.info('Creating QR code')
    qr = qrcode.QRCode(
        version=15,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=2,
        border=10,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrcode.png")
#    logger.info('QR code created and saved as qrcode.png')
    return img

def _get_window_info(mywindow):


    """Function to get window information after a delay."""
    logger.info('Getting window information after delay')
    mywindow.mk.set_startx(mywindow.startx)
    mywindow.mk.set_geo(mywindow.geo)
    mywindow.mk.set_bbox(mywindow._bbox)
    mywindow.get_window_info()

def _hide(mywindow, data):
    """Function to hide the window after a delay."""
#    global speech_pipe
#    logger.info('Initializing speech pipeline')
#    speech_pipe = KPipeline(lang_code='a')
    logger.info('Hiding mywindow after delay')
    mywindow.hideme()


    #initialize time..
    day = 86400
    tnow = time.time()
    #should get from last three days and scroll each?  
    mywindow.set_time(tnow-day*1, tnow-day*1.5, tnow, day*0.5) #default is 1 day for now..
    mywindow.set_speed(None, 1.0, "_meta")
    mywindow.set_speed(None, 1.0, "video")
    
    #get average color and screen
    #get_window_details()




def stop_audio(cacheno=-1):
    #called from hotkeys to stop all audio threads.
    global audio_stop_events
    print('Stopping all audio threads')
    print(audio_stop_events)
    if (cacheno >=0 and cacheno < len(audio_stop_events)):
        print(f'Stopping audio thread {cacheno}')
        audio_stop_events[cacheno].set()  # Signal the audio thread to stop
        return
    for audio_stop_event in audio_stop_events:
        print('Stopping audio thread')
        audio_stop_event.set()  # Signal the audio thread to stop

def pause_reader(cacheno=-1):
    #called from hotkeys to pause all audio threads.
    global audio_stop_events
    print('Pausing all audio threads')
    if (cacheno >=0 and cacheno < len(audio_skip_events)):
        print(f'Pausing audio thread {cacheno}')
        audio_skip_queue[cacheno].put(-1001) #signal to pause
        audio_skip_events[cacheno].set()
        return
    for i, audio_skip_event in enumerate(audio_skip_events):
        print('Pausing all audio threads')
        audio_skip_queue[i].put(-1001) #signal to pause
        audio_skip_event.set()

def resume_reader(cacheno=-1):
    #called from hotkeys to resume all audio threads.
    global audio_stop_events, audio_skip_events
    print('Resuming all audio threads')
    if (cacheno >=0 and cacheno < len(audio_skip_events)):
        print(f'Resuming audio thread {cacheno}')
        audio_skip_queue[cacheno].put(0) #signal to skip 0 if something wrong with the event thread..
        audio_skip_events[cacheno].clear()
        audio_stop_events[cacheno].clear() #make sure stop event is cleared as well.
        return
    for i, audio_skip_event in enumerate(audio_skip_events):
        print('Resuming all audio threads')
        audio_skip_queue[i].put(0) #signal to skip 0 if something wrong with the event thread..
        audio_skip_events[i].clear()
#        audio_skip_event.clear()
    for audio_stop_event in audio_stop_events:
        audio_stop_event.clear() #make sure stop event is cleared as well.

def skip_lines(n, cacheno=-1, multiplier=3):
    #called from hotkeys to skip n lines of audio.
    #eventually match up audio_skip_events with playwrighty cache numbers so we can skip in specific readers if needed.
    global audio_skip_events
    print(f'Skipping {n*multiplier} lines of audio')
    
    if (cacheno >=0 and cacheno < len(audio_skip_events)):
        print(f'Skipping lines in audio thread {cacheno}')
        audio_skip_queue[cacheno].put(int(n*multiplier))
        audio_skip_events[cacheno].set()
        return
    for i, audio_skip_event in enumerate(audio_skip_events):
        print(f'Skipping lines in audio thread {i}')
        audio_skip_queue[i].put(int(n*multiplier))
        audio_skip_events[i].set()

def select_type(n):
    #called from hotkeys to skip n lines of audio.
    global audio_skip_events
    global current_type
    current_type = n
    print(f'Select Type {n}')

        
def next_type(n):
    #called from hotkeys to skip n lines of audio.
    global audio_skip_events
    global current_type
    print(f'Jump Next {n}')
    for i, audio_skip_event in enumerate(audio_skip_events):
        print('Skipping lines in audio thread')
        if (current_type is not None):
            audio_skip_queue[i].put(-20000*current_type -n) #signal to go to next type
            
            audio_skip_event.set()

def page(n):
    #called from hotkeys to skip n lines of audio.
    #stop audio, or just page down, and start reading from there.  
#    stop_audio()
    
    if (n > 0):
        print(f'Page Down {n}')
        #estimate number of lines to skip and skip the lines.  
        i = 0
        for i in range(n):
            keyboard.Controller().press(keyboard.Key.page_down)
        #really need to get data from screen..
        skip_lines(n*20) #estimate 20 lines per page
        
    else:
        print(f'Page Up {-n}')
        for i in range(-n):
            keyboard.Controller().press(keyboard.Key.page_up)
        skip_lines(-n*20) #estimate 20 lines per page



def stop_midi(kill=False):
    global midi_stop_event
    global midi_kill_event
    global midi_thread
    global midiin, midiout
    logger.info('Stopping MIDI thread')
    if (kill):
        logger.info('Killing MIDI thread')
        try:
            midi_kill_event.set()
            midi_stop_event.set()  # Signal the MIDI thread to stop
            midi_thread.join()  # Wait for the MIDI thread to finish
            time.sleep(10)  # Give some time for the thread to exit
        except Exception as e:
            logger.error(f'Error stopping MIDI thread: {e}')
    else:
        midi_stop_event.set()  # Signal the MIDI thread to stop

    midiin.close()  # Close the MIDI input port
#    midiout.close()  # Close the MIDI output port


def stop_joystick():
    global joystick_thread
    pygame.joystick.quit()
    if (joystick_thread is not None and joystick_thread.is_alive()):
        logger.info('Stopping joystick thread')
        joystick_thread.join()  # Wait for the joystick thread to finish


def joystick_loop(qrin_queue):
    joycount = pygame.joystick.get_count()
    if joycount == 0:
        return

    logger.info(f'{joycount} joystick(s) detected.')
    logger.info('Starting Joystick thread')
    joyaxes = [[] for i in range(joycount)]
    for (i) in range(joycount):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        logger.info(f'Initialized Joystick {i}: {joy.get_name()}')
        axis = joy.get_numaxes()
        joyaxes[i] = [0.0] * axis
        logger.info(f'Joystick {i} has {axis} axes.')
        qrin_queue.put(f'<<joystick>>\n> JOY [{i},{axis}]\n$$\n')
        pygame.event.pump()  # Process event queue to initialize joystick events

    while True:
#        pygame.display.flip()
        time.sleep(0.05) #small delay to prevent high CPU usage, adjust as needed event rate 20 Hz for now
#        print('Checking for joystick events...')
        joycount = pygame.joystick.get_count()
        joyaxes = [[0.0] * joy.get_numaxes() for joy in [pygame.joystick.Joystick(i) for i in range(joycount)]]
        for event in pygame.event.get():
#            logger.info(f'Joystick event: {event}')

            # JOYAXISMOTION    joy, axis, value
            # JOYBALLMOTION    joy, ball, rel
            # JOYHATMOTION     joy, hat, value
            # JOYBUTTONUP      joy, button
            # JOYBUTTONDOWN    joy, button

            if event.type == JOYAXISMOTION: #too many events, just take last value for each axis and send in batch every loop, can adjust as needed.
                joyaxes[event.joy][event.axis] = event.value
                qrin_queue.put(f'<<joystick>>\n> AXIS [{event.joy},{event.axis},{event.value:.2f}]\n$$\n')
            elif event.type == JOYBALLMOTION:
                qrin_queue.put(f'<<joystick>>\n> BALL [{event.joy},{event.ball},{event.rel}]\n$$\n')
            elif event.type == JOYHATMOTION:
                qrin_queue.put(f'<<joystick>>\n> HAT [{event.joy},{event.hat},{event.value}]\n$$\n')
            elif event.type == JOYBUTTONUP:
                qrin_queue.put(f'<<joystick>>\n> BUTTON [{event.joy},{event.button},0]\n$$\n')
            elif event.type == JOYBUTTONDOWN:
                qrin_queue.put(f'<<joystick>>\n> BUTTON [{event.joy},{event.button},1]\n$$\n')

        axisstr = "<<joystick>>\n"
        for i in range(joycount):
            for j in range(len(joyaxes[i])):
                if abs(joyaxes[i][j]) > 0.1: #threshold to prevent noise, adjust as needed
                    axisstr += f'> AXIS [{i},{j},{joyaxes[i][j]:.2f}]\n'
        if (len(axisstr) > len("<<joystick>>\n")):
            qrin_queue.put(axisstr)

def start_joystick():
    global joystick_thread
    global qrin_queue

    pygame.init()
    pygame.event.set_blocked((MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN))

    pygame.joystick.init()
    clock = pygame.time.Clock() # Create a Clock object
#    clock.tick(60) # Limit the loop to run at 60 frames per second (adjust as needed)
    joycount = pygame.joystick.get_count()
    if joycount > 0:
        logger.info(f'{joycount} joystick(s) detected and initialized.')
        joystick_thread = threading.Thread(target=joystick_loop, args=(qrin_queue,))
        joystick_thread.start()
        return True
    else:
        logger.info('No joysticks detected.')
        print("No joysticks were detected.")
        return False

def start_midi():
    global qr_queue
    global qrin_queue

    global midi_stop_event
    global midi_thread
    global midi_kill_event
    if (midi_thread is not None and midi_thread.is_alive()):
        logger.info('MIDI thread already running')
        stop_midi()
        #this calls unload..
        time.sleep(4) #give some time to close down.
    #set playwrighty context to null
    midi_stop_event = threading.Event()
    midi_kill_event = threading.Event()
    midi_thread = threading.Thread(target=run_midi, args=(midi_stop_event,midi_kill_event, qr_queue, qrin_queue))
    midi_thread.start()
    midin, midout = get_midi_ports()
    if (len(midin) > 0):
        logger.info(f'MIDI input ports: {midin}')
        return True
    return False


def get_midi_ports():
    inputs = mido.get_input_names()
    outputs = mido.get_output_names()
    return inputs, outputs


def updateQR(idx):
    global incoming_qrdata
    global current_qrdata
    if (incoming_qrdata != current_qrdata):
        logger.info('MIDI thread updating QR code')
        print('MIDI thread updating QR code')
        current_qrdata = incoming_qrdata
        on_activate_overlay()


def handle_keys(qr_queue=None, qrin_queue=None):
    global midiout, midiin
    global mk
    #[channel] = [note, vertical, rotational, pressure]
    channelsmap = [[-1,-1,-1,-1]]*256 #array for channels
    channelmap = [[-1,-1,-1,-1]]*256 #array for channels
    #channel, value for MPE
#    c = Communicate()
#    c.mySignal.connect(updateQR)

    try:
        with midiin as inport:
    #        qr_queue.put('<<midi>>\n> MIDIStart [0]\n$$\n')
            while (not midi_stop_event.is_set()):
                while (qrin_queue is not None and not qrin_queue.empty()):
                    qrdata = qrin_queue.get()
                    mk.add_qrin(qrdata)
                    logger.info(f'MIDI Received QR input data: {qrdata}')
                    
                #get all q2 output messages.  
                mk.set_audio_location()

                for msg in inport.iter_pending():
                    channel = -1
                    if (msg.type == 'aftertouch'):
                        #print(msg)
                        if (hasattr(msg, 'channel') and hasattr(msg, 'value')):
                            #pressure
                            channel = msg.channel
                            currentval = channelmap[channel]
                            channelmap[channel] = [currentval[0], currentval[1], currentval[2], msg.value]
                    elif (msg.type == 'pitchwheel'):
                        #print(msg)
                        if (hasattr(msg, 'channel') and hasattr(msg, 'pitch')):
                            #rotational
                            channel = msg.channel
                            currentval = channelmap[channel]
                            channelmap[channel] = [currentval[0], currentval[1], msg.pitch, currentval[3]]
                        
                    elif msg.type == 'control_change':
                        #print(msg)
                        if (hasattr(msg, 'channel') and hasattr(msg, 'control') and hasattr(msg, 'value') and msg.control == 74): #MPE standard for timbre control
                            channel = msg.channel
                            currentval = channelmap[channel]
                            #vertical
                            channelmap[channel] = [currentval[0], msg.value, currentval[2], currentval[3]]
                        #use midi joystick control.  
                        #also allow external joystick control..
                    if (channel != -1 and qr_queue is not None):
                        #send update for this channel to QR code, can adjust format as needed.
                        mk.add_qrin(f'<<midi>>\n> Aftertouch [{channelmap[channel][0]},{channelmap[channel][1]},{channelmap[channel][2]},{channelmap[channel][3]}]\n$$\n')
                        #only update sometimes?  For now do all.  

                        if (random.random() < 0.05): #adjust this threshold as needed to balance responsiveness with performance, currently set to update on average every 20 messages.
                            qrdata = mk.get_qr()
                            if (qrdata is not None and qrdata != ""):
                                qr_queue.put(qrdata)
                    
                    if msg.type == 'note_on' or msg.type == 'note_off':
                        print(msg)
                        logger.info(f'Received MIDI message: {msg}')
                        if hasattr(msg, 'note'):
                            note = msg.note
                            if (hasattr(msg, 'channel')):
                                channel = msg.channel
                                if (msg.type == 'note_on' and msg.velocity > 0):
                                    channelmap[channel] = [note, -1, -1, -1]
                                else:
                                    channelmap[channel] = [-1,-1,-1,-1]   

                            if hasattr(msg, 'velocity'):
                                velocity = msg.velocity
                            else:
                                velocity = 0
                            #add key to sequence and check for any actions.  
                            a = mk.key(note, msg, callback=None)
                            #every note adjust the QR code in case something changed.
                            #probably better way to do this..
                            qrdata = mk.get_qr()
                            if (qrdata is not None and qrdata != ""):
                                qr_queue.put(qrdata)
    #                        c.mySignal.emit(0)
                            #update QR code if changed.

    #                        if (a == -1):
                                #error or reset
    #                            winsound.Beep(2000, 500) # Beep at 2000 Hz for 500 ms
                        else:
                            print("Message does not have a note attribute")
                    else:
                        dontprint = 1
    #                    print(msg)
    #                    logger.info(f'Received MIDI message: {msg}')
    except (IOError, EOFError):
        print("MIDI device disconnected safely.")
        #inport.close()
    except Exception as e:
        logger.error(f'Error handling MIDI message: {e}')

def init_inputs():
    global midiout, midiin
    inputs, outputs = get_midi_ports()
    logger.info(f'Available MIDI inputs: {inputs}')
    logger.info(f'Available MIDI outputs: {outputs}')
#    midiout = mido.open_output(outputs[1]) #open first output for now.  
    mypname = config.cfg['keymap']['pianos'][0] if 'pianos' in config.cfg['keymap'] else 'Portable Grand'
    if (inputs is not None and len(inputs) > 0):
        for i, name in enumerate(inputs):
            if (name.startswith(mypname)):
                logger.info(f'Opening MIDI input: {name}')
                midiin = mido.open_input(name)
                break
            else:
                if (i == len(inputs)-1): #if last, set to input
                    logger.warning(f'MIDI input "{mypname}" not found. Opening last available input: {inputs[len(inputs)-1]}')
                    midiin = mido.open_input(inputs[len(inputs)-1]) #open last input for now.

def run_midi(mstop_event, kill_event, qr_queue=None, qrin_queue=None, audio_location_queue=None):
    global midiout, midiin
    global mk
    global mywindow
    mk = mykeys.MyKeys(config.cfg, qapp, mywindow.startx, mstop_event, qr_queue, qrin_queue)
    mywindow.mk = mk
    logger.info('Starting MIDI input/output')
    init_inputs()
    
    #Portable Grand-1 2
    #should really have some config selection here.  
    mk.start_feedback() #play feedback if enabled.  This takes some time apparently to start thread.  
    cont = keyboard.Controller()    

    while (not kill_event.is_set()):
        try:
            handle_keys(qr_queue, qrin_queue)
            init_inputs() #re-init inputs in case something changed.
            time.sleep(0.1)  # Small delay to prevent high CPU usage
            mstop_event.clear()  # Clear the event for the next iteration
            mk.start_feedback() #restart feedback if needed.
        except Exception as e:
            logger.error(f'Error in MIDI loop: {e}')

    logger.info('MIDI thread completed, unloading MK')
    mk.unload()
    logger.info('MIDI thread ended')






from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QDialog, QVBoxLayout, QSystemTrayIcon, QMenu, QAction, QMessageBox

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QImage, QFont, QFontMetrics, QFontDatabase, QIcon, QColor

def create_circle_icon(color: QColor, size: int) -> QIcon:
    """
    Draws a circle onto a QPixmap and returns a QIcon.
    """
    # 1. Create a QPixmap and fill with a transparent color
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 2. Initialize a QPainter on the QPixmap
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing) # For smooth edges
    
    # 3. Draw the shape (a circle)
    painter.setBrush(color)
    painter.setPen(QPen(Qt.GlobalColor.black, 1.25))
    # Draw an ellipse that fills the pixmap's rectangle (makes it a circle if size is square)
    painter.drawEllipse(pixmap.rect().adjusted(1, 1, -1, -1))

    # 4. End the QPainter
    painter.end()

    # 5. Create and return a QIcon
    return QIcon(pixmap)

def show_tray(qapp):
    global qtray
    global qmenu
    # 2. Create the system tray icon
    icon = create_circle_icon(QColor(0, 255, 0), 64) #green circle for now, can adjust color and size as needed.
    qtray = QSystemTrayIcon()
    qtray.setIcon(icon)
    qtray.setVisible(True)


    # 3. Create a context menu
    qmenu = QMenu()

    # Action to quit the application
    quit_action = QAction("Quit")
    quit_action.triggered.connect(qapp.quit)
    qmenu.addAction(quit_action)

    # 4. Add the menu to the tray icon
    qtray.setContextMenu(qmenu)
    qtray.show()
    # Optional: Add a tooltip (hover text)
#    tray.setToolTip("My PyQt5 Tray App")

    # Optional: Show a balloon message on launch (Windows/Linux)
#    tray.showMessage("My PyQt5 Tray App", "Application started in the background", QSystemTrayIcon.Information, 2000)


# 2. Define a function to dynamically change the icon
def change_icon_dynamically(icon):
    lastjoyconn = 100
    lastmidiconn = 100
    while True:
        # Wait a few seconds to demonstrate the change after the icon is visible
        time.sleep(3)
        # Load a new image using Pillow
        midiconn = 1
        joyconn = 1
        joyconn = pygame.joystick.get_count()
        inputs, outputs = get_midi_ports()
        if (len(inputs) > 0):
            midiconn = len(inputs)
#        print(f'MIDI connections: {midiconn}, Joystick connections: {joyconn}')
        #probably could do dynamically, but not worth..
        if (midiconn > lastmidiconn or joyconn > lastjoyconn):
            print('New MIDI or Joystick connections detected, restart to connect??')
#            print(pystray.Icon.HAS_NOTIFICATION)
            #win: System/Notifications
            icon.notify('New Device Connections available\nCTRL+SHIFT+R to restart', title='Trey Connection status')
#            quit_me(True) #restart to get new connections..
        elif (midiconn < lastmidiconn or joyconn < lastjoyconn and lastjoyconn != 100 and lastmidiconn != 100):
            print('MIDI or Joystick connections lost, restart??')
            icon.notify('Device Connections lost\nCTRL+SHIFT+R to restart', title='Trey Connection status')

        if (midiconn >0 and joyconn > 0):
            new_image = Image.new('RGB', (64, 64), color='green') # Replace with your actual image loading
        elif (midiconn > 0):
            new_image = Image.new('RGB', (64, 64), color='blue') # Replace with your actual image loading
        elif (joyconn > 0):
            new_image = Image.new('RGB', (64, 64), color='purple') # Replace with your actual image loading

        # Change the icon attribute directly
        icon.icon = new_image

        lastjoyconn = joyconn
        lastmidiconn = midiconn
    #        icon.title = f"Trey {midiconn} {joyconn}" # Optionally change the title
        


def main():
    global qapp
    global mywindow
    global active_window
    global midiout, midiin
    global speech_pipe
    global qr_pipe

    # Create an icon image
    icon_image = create_image(64, 64, 'blue', 'yellow')

    # Define the menu for the icon
    menu = (
        pystray.MenuItem('Capture Screen', on_get_screen),
        pystray.MenuItem('Show Message', on_show_message),
        pystray.MenuItem('Quit', on_quit_action)
    )

    # Create the pystray Icon instance
    icon = pystray.Icon(
        'my_trey_icon',  # Name of the icon
        icon=icon_image,  # The icon image
        title='Trey',  # Title displayed on hover
        menu=menu  # The menu associated with the icon
    )
    # Run the icon (this call is blocking)
    logger.info('Started')
    logger.info('Setting up hotkey listener')
    hotkey_listener = setup_hotkey_listener()
    logger.info('Hotkey listener set up')

    logger.info('Loading custom settings')
    config.load_custom_settings() #load custom settings if available
    logger.info('Creating Qapplication object')
    # Create the application object
    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)
    logger.info('Creating application window')
    # Create the main application window
    global qr_queue, qrin_queue
    qr_queue = Queue()
    qrin_queue = Queue()

#    show_tray(qapp)

    mywindow = MyWindow(qr_queue, qrin_queue, config.cfg, qapp)

    logger.info('Running icon')
#    icon.run()
    icon.run_detached()



    # Create a Thread object to listedn for MIDI messages
    # Create an event
    midiconn = start_midi()

    #start joystick thread.  
    joyconn = start_joystick()


    dynamic_change_thread = threading.Thread(target=change_icon_dynamically, args=(icon,))
    dynamic_change_thread.start()

    logger.info('Executing application')

    sys.exit(qapp.exec_())
    #hiding window as we only want it on hotkey
    #window.hide()





if __name__ == "__main__":
    main()
