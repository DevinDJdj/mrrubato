#pip install pystray Pillow mss PyQt5
#pip install pynput

#pip install qrcode
#pip install mido python-rtmidi
#pip install pywin32


#standard libraries
import logging
import os
import time
import sys
import threading
import multiprocessing
import subprocess
from huggingface_hub import login
import psutil

from datetime import datetime

from queue import Queue

#Screen capture, QR code generation
import mss
import qrcode
from pynput import keyboard, mouse

import glob

#MIDI libraries
import mido

import random


import torch

#UI components
import pystray
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QImage
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread
import PyQt5.QtCore as QtCore
import win32gui
import win32process
import win32api
import win32con

import winsound

#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
import config 
import mykeys

import tts
#from kokoro import KPipeline
#from IPython.display import display, Audio
#import soundfile as sf

#pip install playsound
from playsound3 import playsound
from pydub import AudioSegment
from pydub.playback import play

#import simpleaudio as sa
import pygame
import edge_tts

import extensions.trey.qdrantz as qdrantz
import news as news #get news articles

from fastembed import (
                SparseTextEmbedding,
                TextEmbedding,
                ImageEmbedding,
                LateInteractionMultimodalEmbedding,
                LateInteractionTextEmbedding,
            )


import extensions.trey.playwrighty as playwrighty
import extensions.trey.synth as synth

import languages.helpers.transcriber as transcriber

import pytesseract


logger = logging.getLogger(__name__)
global mywindow
global active_window
global qapp
global midiout
global midiin
global midi_thread
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

def is_process_running(process_name):
    """
    Check if a process with a given name is currently running.
    """
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() == process_name.lower():
            return True
    return False


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

def pause_obs_capture():
    checkobs = is_process_running("obs64.exe")

    if (checkobs):
        logger.info('OBS process detected, pausing capture.')
        #send pause hotkey to OBS
        send_hotkey('8')
        print("Pause Recording " + str(time.time()))

def stop_obs_capture():
    checkobs = is_process_running("obs64.exe")

    if (checkobs):
        logger.info('OBS process detected, stopping capture.')
        #send stop hotkey to OBS
        send_hotkey('z')
        print("Stop Recording " + str(time.time()))
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

    else:
        obsp = subprocess.Popen("C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe", start_new_session=True, cwd="C:\\Program Files\\obs-studio\\bin\\64bit")
        logger.info('Starting OBS process.')
        time.sleep(10) #wait for OBS to start        
        logger.info('OBS process started, starting capture.')
        #send start hotkey to OBS
        send_hotkey('a')
        print("Start Recording " + str(time.time()))


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
    mouse_listener = mouse.Listener(on_click=on_click)
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

def copy_latest_file():
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
    return latest_file


def quit_me(restart=False):
    global mk
    logger.info('Stopping MIDI thread')

    mk.savemidi() #save current midi file
    stop_midi(True) #kill the midi thread

    logger.info('Closing OBS capture if running')
    stop_obs_capture()
    time.sleep(5) #wait for OBS to close
    #save latest file to transcripts..
    copy_latest_file()
    logger.info('Quitting application')
    qapp.quit()
    #some cleanup still necessary?  
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


def gen_audio(ldmap, stop_event=None):
    """Generate audio from text using the speech pipeline."""
    from extensions.trey.speech import generate_audio
    logger.info('Starting audio generation thread')
    print('Generating audio for link density map')
    print(ldmap)
    for idx, l in enumerate(ldmap):
        if (stop_event is not None and stop_event.is_set()):
            logger.info('Audio generation stop event set, stopping audio generation')
            print('Audio generation stop event set, stopping audio generation')
            break
        print(f'Generating audio for line {idx}: {l["text"]}')
        if (len(l['text']) > 5):
            generate_audio(l['text'], fname=l['audio'], fast=True)

def build_map(lines, links):

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
        link_density_map.append({"offset": total_read, "text": l, "length": len(l), "mavglength": mavglength, "numlinks": numlinks, "audio": f"./temp/{idx}.wav", "density": numlinks/(len(l)+1)})
        total_read += len(l) + 1  #include newline

        

    return link_density_map

def remove_temp_audio(dir):
    #remove temp files first.  
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error removing file {file_path}: {e}")




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
    return voices


def play_sound_process(sound_file):
    playsound(sound_file)


def stopsound(currentsound):
    if (currentsound is not None and currentsound.is_alive()):
        #stop current sound if we are skipping.  
        #this is a bit aggressive but should work for now.  
        currentsound.stop()

def play_in_background(text, links=[], offset=0, stop_event=None, skip_event=None, q=None, q2=None, q3=None, lang='en'):

    skipmenu = True
    currentsound = None
    sound_file = f"{random.randint(0, 100)}.mp3"
    if lang is None or lang == '':
        #detect language if long enough?          
        lang = 'en'
    try:
        VOICES = get_voices(lang)
    except:
        VOICES = []
    if (len(VOICES) == 0):        
        VOICES = ["en-US-AriaNeural", "en-US-CoraNeural", "en-US-ElizabethNeural", "en-US-AshleyNeural", "en-US-AvaNeural", "en-US-BrandonNeural", "en-US-BrianNeural", "en-US-EmmaNeural", "en-US-EricNeural"]
#    VOICE = "en-US-AriaNeural"
    #for now random.  
    rnd = int(time.time()) % len(VOICES)
    VOICE = VOICES[rnd]
    LINKVOICE = VOICES[(rnd+1) % len(VOICES)]

    SIMVOICE = ["en-US-CoraNeural", "en-US-ElizabethNeural"]
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

    remove_temp_audio("./temp/")

    if (offset == 0):
        #pre-read detect good starting point.
        link_density_map = build_map(lines, links)
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
        link_density_map = build_map(lines, links)

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
    while (link_loc < len(links) and 'offset' in links[link_loc] and links[link_loc]['offset'] == -1):
        link_loc += 1
        #skip all links with no offset


    #init_qdrantz(link_density_map, topic="websearch")
    print('Start Reading:')

    idx = -1
    while (idx < len(lines)-1):
#    for idx in range(len(lines)):
        idx = idx + 1
        l = lines[idx]
        combined = "" #line to hold combined short lines and read together. 
        combined_counter = 0 
        if (len(l) > 2 and l[0:2] == '$$'):
            #ENV info, read..
            print(f'{l}')
            sound_file = f"./temp/overview.mp3"
            lesc = lines[0] if (len(lines[0]) < 200) else lines[0][:200]
            print(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{lesc}\" --rate=\"-10%\" > NUL 2>&1")
            suc = os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{lesc}\" --rate=\"-10%\" > NUL 2>&1")
            if (suc != 0):
                print(f'Error generating audio fallback to tts.speak')
                tts.speak(lesc, VOICE, sound_file)
#            playsoundprocess = multiprocessing.Process(target=play_sound_process, args=(sound_file,))
#            playsoundprocess.start()
            playsound(sound_file, block=False) # Ensure this thread blocks for its sound
            #try other mechanism.. stopsound..

        if (stop_event.is_set()):
            logger.info('Audio stop event set, stopping playback')
            print('Audio stop event set, stopping playback')
            mp_stop.set() #stop audio generation as well
            break
        if (skip_event.is_set()):
            logger.info('Audio skip event set, skipping this line')
            print('Audio skip event set, skipping next several lines')
            lines_to_skip = q.get()
            print('Skipping lines command received: ' + str(lines_to_skip))
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
        if (skip > 0):
            if (idx + skip >= len(lines)):
                skip = len(lines) - idx - 2
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
        print(f'Total Lines: {len(lines)}')
        print(f'Current IDX: {idx}')
        print(f'Skipping: {skip}')
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

        if (len(l) > 5):
            try:
    #            communicate = edge_tts.Communicate(text, VOICE)
    #            await communicate.save(sound_file)
                #play the line type info first
                play_l(link_density_map[idx], idx/len(lines))
                vol = 0.7
                rate = 150
                if (idx < 2): #adjust for informational lines..
                    vol = 1.0
                    rate = 120

                if (os.path.exists(sound_file)):
                    print(f'Playing pre-generated audio: {sound_file}')
                    currentsound = playsound(sound_file, block=False) # Ensure this thread blocks for its sound
                else:
                    print(f'Generating and playing audio: {l}')
                    sound_file = f"./temp/{idx}.mp3"
                    subtitle_file = f"./temp/{idx}.srt"
                    lesc = l.replace('"', '\\"')

#                    suc = os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{lesc}\" --write-subtitles \"{subtitle_file} --rate=\"-10%\" > NUL 2>&1")
                    suc = os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{lesc}\" --rate=\"-10%\" > NUL 2>&1")
                    if (suc != 0):
                        print(f'Error generating audio fallback to tts.speak')
                        tts.speak(lesc, VOICE, sound_file, vol, rate)

#                    sound_file = f"./temp/{idx}.wav"
                    #fast not working.. edge-tts much better quality than speechbrain tts.
#                    cmd = f"python ./extensions/trey/speech.py --text \"{l}\" --fname \"{sound_file}\""
#                    os.system(cmd)
                    currentsound = playsound(sound_file, block=False) # Ensure this thread blocks for its sound
#                time.sleep(0.5) #short pause between lines
            except Exception as e:
                logger.error(f'Error in TTS playback: {e}')
                logger.error(f'{l}')
                print(f'Error in TTS playback: {e}')
                total_read += len(l) + 1 #include newline
                continue


        if random.randint(0,100) < 5:
            print(f'Total read: {total_read}')
            logger.info(f'Total read: {total_read}')
        waited = 0
        ttotal = total_read


        time.sleep(0.01*len(l)) #wait for initial TTS to start playing.
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
                        tts.speak(links[link_loc]['text'], LINKVOICE, sound_file, 1.0, 200) #quieter slower for links
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
                ev = q.get()
                if (ev == -1001): #pause event.. for speaking..
                    while(skip_event.is_set()):
                        time.sleep(0.5)
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
            time.sleep(0.6-0.3*linksspoken) #simulate reading time. 12 chars per second..
            if (ttotal > total_read+len(l)+1):
                i = len(l)+1 #break out of loop if we have read past the line, to avoid long waits on long lines.
                continue
            #shouldnt have to be too exact.  
        print(f'Total waited: {waited}')

        total_read += len(l) + 1 #include newline

        r = None
        if (len(l) > 50): #only do similar for longer lines
            r = get_similar(idx, link_density_map) #do a vector search for similar items.
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
                            sound_file = f"./temp/sim{rid}.mp3"
                            lesc = siml.replace('"', '\\"')
                            os.system(f"edge-tts --voice \"{voice}\" --write-media \"{sound_file}\" --text \"Similar: {lesc}\" --rate=\"+20%\" --volume=-40% > NUL 2>&1")
                            playsound(sound_file, block=False) # Ensure this thread blocks for its sound

                        except Exception as e:
                            logger.error(f'!!Error in TTS playback of similar item: {e}')
                            logger.error(f'!!{siml}')
                            print(f'!!Error in TTS playback of similar item: {e}')
                            
                            continue
                    if (q3 is not None):
                        q3.put(link_density_map[rid]['offset']) #send back the offset of the similar item.

        if (q2 is not None):
            q2.put(total_read)

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


def delay_stop_event(stop_event, delay):
    """Set the stop event after a delay."""
    time.sleep(delay)
    stop_event.set()


def speak(text, links = [], alt_text=[], offset=0, lang='en', cacheno=-1):
    global audio_stop_events
    global audio_location_queue
    global audio_skip_events
    global audio_skip_queue
    """Speak the given text using the speech pipeline."""
#    print(f'Speaking: {text}')

    
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
    audio_thread = threading.Thread(target=play_in_background, args=(f'{text}',links, offset, audio_stop_event, audio_skip_event, q, q2, q3, lang))
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

def draw_overlay(delay=10, opacity=0.4): #default hide in 10 seconds
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

    mywindow.updateLabels(windows) #gives info for all windows
    mywindow.setWindowOpacity(opacity)
    mywindow.activateWindow() # Bring to front
    draw_screen_box()

    #hiding in 3 seconds
    logger.info(f'Hiding window after {delay} seconds')
    t = threading.Timer(delay, _hide, args=["Hello from Timer!"])
    t.start()  # Start the timer in a new thread

    start_mouse_listener()  # Start the mouse listener



def draw_screen_box(bbox=None):
    """Draws a box around the screen."""
    mywindow.highlighton = True
    #get geometry of the highlight rectangle.  
    if (bbox is not None): #xxyy
        mywindow.highlightrect = {'x': bbox[0], 'y': bbox[2], 'width': bbox[1]-bbox[0], 'height': bbox[3]-bbox[2]}
    else:
        geometry = mywindow.geometry()
        mywindow.highlightrect = {'x': geometry.x()+100, 'y': geometry.y()+100, 'width': geometry.width()-100, 'height': geometry.height()-100}
    mywindow.update()  # Trigger a repaint to show the box
    logger.info('Screen box drawn')


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

def _hide(data):
    """Function to hide the window after a delay."""
#    global speech_pipe
#    logger.info('Initializing speech pipeline')
#    speech_pipe = KPipeline(lang_code='a')
    logger.info('Hiding mywindow after delay')
    mywindow.hideme()
    mk.set_startx(mywindow.startx)
    mk.set_geo(mywindow.geo)

    #get average color and screen
    get_window_details()



class Communicate(QtCore.QObject):
    mySignal = QtCore.pyqtSignal(int)



#thread to get QR data from window and add text info to trey cache.  

import cv2
from qreader import QReader
import numpy as np

# Step 1: Create a worker class
class QRInWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def qimage_to_cv2(self, qimage):
        """Converts a QImage into an OpenCV image (numpy array)."""
        # Ensure the QImage is in a format that allows direct byte access (e.g., RGBA8888 or RGB888)
        # OpenCV expects BGR format, so conversion might be needed later depending on the source
        if qimage.format() != QImage.Format_RGB888:
            # Convert to a standard 8-bit RGB format. Format_ARGB32 is common
            qimage = qimage.convertToFormat(QImage.Format_ARGB32)

        width = qimage.width()
        height = qimage.height()
        
        # Get a pointer to the raw bytes
        ptr = qimage.bits()
        # Set the size of the pointer to the total number of bytes
        ptr.setsize(qimage.byteCount())
        
        # Create a NumPy array from the raw data
        # The shape will be (height, width, channels)
        # The data is copied in this step
        arr = np.array(ptr).reshape(height, width, -1) # Use -1 to infer the number of channels

        # If the QImage was in ARGB32 format, the array will be in BGRA order (due to Qt's internal representation on many systems)
        # OpenCV uses BGR, so if you need to perform typical OpenCV operations, convert the color space
        if qimage.format() == QImage.Format_ARGB32:
            # Convert from BGRA to BGR
            arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
        elif qimage.format() == QImage.Format_RGB888:
            # Convert from RGB to BGR (OpenCV's default color order)
            arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        # Handle other formats as needed (e.g., grayscale)
        elif qimage.format() == QImage.Format_Grayscale8:
            # No color conversion needed for grayscale, it's a 2D array
            arr = arr.reshape(height, width)

        return arr

    def read_qr_code(self, img):
        
        #qreader too slow, use nano model for speed.
        #income as QImage
        img = self.qimage_to_cv2(img)
        #calc width, get upper right quadrant for now just read here.  
        x_start = int(img.shape[1] / 2)
        x_end = img.shape[1]
        y_start = 0
        y_end = int(img.shape[0] / 2)
        cropped_img = img[y_start:y_end, x_start:x_end, :]
#        print(f'Cropped image shape: {cropped_img.shape}')
        cropped_image = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_BGR2RGB)
        decoded_texts = self.qreader.detect_and_decode(image=cropped_image)
        if decoded_texts:
            for text in decoded_texts:
                print(f"QR In Code data: {text}")
                logger.info(f"QR In Code data: {text}")
            return decoded_texts
        else:
#            print("No QR In code detected.")
            return []
        
    def __init__(self, my_queue, parent=None):
        super(QRInWorker, self).__init__(parent)
        self.my_queue = my_queue # Store parameter in the worker instance
        self.all_qr = [] #store all qr data seen.
        self.qreader = QReader(model_size='n')  # Initialize the QR code reader with a nano model

    def find_recent_qr(self, qrin, timeframe=5):
        """Find QR data seen in the last timeframe seconds."""
        current_time = time.time()
        recent_qr = self.all_qr[-5:] #last 5 entries
        for qr in recent_qr:
            if ('data' not in qr or 'timestamp' not in qr):
                continue #not valid data
            if (qr['data'] == qrin and (current_time - qr['timestamp']) < timeframe):
                return True
        return False
    
    def run(self):
        """Long-running task to find QR data from window."""
        previmg = None
        while (True):
            #get QR data from window
            #this has between 2-10 second delay in read_qr_code.  
#            print(time.time())
            screens = qapp.screens()
            #assume last window
            qimage = screens[-1].grabWindow(0).toImage()
            #skip if same as previous image.
            if (qimage == previmg):
                time.sleep(0.5)
                continue #skip same image
            previmg = qimage
#            print(qimage.width(), qimage.height())
            qrdata = self.read_qr_code(qimage)
#            print(time.time())

            for qd in qrdata:
                logger.info(f'QRInWorker found QR data: {qd}')
                if (isinstance(qd, str) == False):
                    continue
                if (qd.find('<<meta>>') == -1): #for now dont accept meta data, simple way to not read self for now.
                    continue #not our data.
                if not self.find_recent_qr(qd): #skip anything we just saw.  
                    self.my_queue.put(qd)
                    self.all_qr.append({'data': qd, 'timestamp': time.time()})
                    self.progress.emit(qd) #can pass param here as well.  

            time.sleep(0.2) #run each 0.2 seconds
            print(time.time())
        self.finished.emit()


# Step 1: Create a worker class
class QRWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, my_queue, parent=None):
        super(QRWorker, self).__init__(parent)
        self.my_queue = my_queue # Store parameter in the worker instance

    def run(self):
        """Long-running task."""
        while (self.my_queue is not None):
            while (not self.my_queue.empty()):
                #incoming data from mykeys..
                qrdata = self.my_queue.get() #get current link number.  
                logger.info(f'Worker processing QR data: {qrdata[0:50]}')
                self.progress.emit(qrdata) #can pass param here as well.  
                time.sleep(0.2) #allow for QR data to be processed by any reader.  
            time.sleep(0.1) #wait before checking again
        self.finished.emit()

class MyWindow(QMainWindow):


    def reportProgressIn(self, qrdata):
        logger.info(f"QR In: {qrdata}")
        cmds = self.parseQRData(qrdata)
        for idx, cmd in enumerate(cmds):
            currentcmd = cmd['cmd']
            vars = cmd['vars']
            logger.info(f'Parsed QR command: {currentcmd} with vars: {vars}')
            self.qr_in.append({'cmd': currentcmd, 'vars': vars, 'timestamp': time.time()})
            #process incoming commands as needed.
            #for now just log them.

    def reportProgress(self, qrdata):
#        logger.info(f"QR Out: {qrdata}")
        self.showQR(qrdata) #refresh QR display
        cmds = self.parseQRData(qrdata)
        pwords = []
        for idx, cmd in enumerate(cmds):
            if (cmd['type'] == '> '):
                currentcmd = cmd['cmd']
                vars = cmd['vars']
                logger.info(f'Parsed QR command: {currentcmd} with vars: {vars}')
                self.qr_out.append({'cmd': currentcmd, 'vars': vars, 'timestamp': time.time()})
                self.executeQRCommand(currentcmd, vars)
            if (cmd['type'] == '~~'):
                word = cmd['word']
                keys = cmd['keys']
                pwords.append({'word': word, 'keys': keys})
#                logger.info(f'Parsed QR word: {word} with keys: {keys}')
                #process as needed.
                #add to list of words to display..

        print(f'~~: {len(pwords)}')
#        self.updateWords(pwords)

    def executeQRCommand(self, command, vars):
        #use transcriber here??
        """Execute a QR command based on the parsed data."""
        logger.info(f'Executing QR command: {command} with vars: {vars}')
        if (command == "Screen Toggle"):
            if (self.isVisible()):
                #remove stale info?  
                self.hide()                
                #pause OBS capture.
                pause_obs_capture()
            else:
                self.setWindowOpacity(float(vars.get('OPACITY', 0.4)))
                self.show()
                #start OBS capture..
                start_obs_capture()
        elif (command =="Screenshot Feedback_"):
            bbox = vars.get('BBOX', None)
            if (bbox is not None):
                self.draw_screen_box(vars.get('BBOX', self.geometry().getRect()))

            #send back the OCR text as feedback.
            #just add to file assuming we 
            #probably dont need this..
            if (vars.get('OCR', 'False') == 'True'):
                ocrtext, fname = self.save_screenshot(vars.get('KLANG', 'video'), vars.get('TRANSCRIPT', ''), vars.get('BBOX', None), True) #always OCR
                vars['OCRTEXT'] = ocrtext
                vars['FNAME'] = fname
                self.ocrtext = ocrtext
            written = self.transcriber.write(vars.get('KLANG', 'video'), command, vars)
            self.set_feedback(written, vars)
        elif (command == "Screenshot Feedback"):
            #right now we are just calling screenshot..
            #get OCR, and transcribe.  This is delayed because of the transcription time..
            ocrtext, fname = self.save_screenshot(vars.get('KLANG', 'video'), '', vars.get('BBOX', None), True) #always OCR
            vars['OCRTEXT'] = ocrtext
            vars['FNAME'] = fname
            self.ocrtext = ocrtext
            written = self.transcriber.write(vars.get('KLANG', 'video'), command, vars)
            self.set_feedback(written, vars)

        elif (command == "_Click Link"):
            self.show()
            #simulate click at link location if given.
        elif (command == "Screenshot"):
            print("Taking Screenshot")
            print(vars['BBOX'])
            self.draw_screen_box(vars.get('BBOX', self.geometry().getRect()))
            ocrtext, fname = self.save_screenshot(vars.get('KLANG', 'hotkeys'), vars.get('FNAME', ''), vars.get('BBOX', self.geometry().getRect()), True) #always OCR?
            vars['OCRTEXT'] = ocrtext
            vars['FNAME'] = fname
            self.ocrtext = ocrtext
            written = self.transcriber.write(vars.get('KLANG', 'video'), command, vars)
            self.set_feedback(written, vars)

            #send to QR In queue for processing by mykeys.  


        elif (command == "Screenshot_"):
            self.draw_screen_box(vars.get('BBOX', None))

        #add more commands as needed.
    def parseQRData(self, qrdata):
        """Parse the QR data and extract relevant information."""
        # For simplicity, just return the data as is.
        lines = qrdata.split('\n')
        currentcmd = ""
        vars = {}
        ret = []
        tempidx = 0
        lang = 'hotkeys'
        for idx, line in enumerate(lines):
#            logger.info(f'QR Data Line: {line}')
            type = line[:2] #first 2 chars is type
            if (len(line) > 3 and line[0] == '<' and line[1] == '<' and line[-2] == '>' and line[-1] == '>'):
                #lang command
                lang = line[2:-2]
            if (type == '> '):
                #command line internal command
                currentcmd = line[2:]
            if (type == '$$'):
                #special trey data line
                if (len(line) == 2):
                    #execute command
                    if (currentcmd != ""):
                        type = '> '
                    vars['KLANG'] = lang
                    ret.append({'type': type, 'lang': lang, 'cmd': currentcmd, 'vars': vars, 'timestamp': time.time()})
#                    logger.info(f'Adding QR {type}: {currentcmd}')
                    currentcmd = ""
                    vars = {}

                else:
                    parts = line[2:].split('=')
                    if (len(parts) == 2):
                        key = parts[0]
                        value = parts[1]
                        vars[key] = value
            if (type == '~~'):
                #end of command
                w = line[2:].split('|')
                vars['KLANG'] = lang
                if (len(w) == 2):
                    word = w[0]
                    keys = w[1].split(',')
                    ret.append({'type': type, 'lang': lang, 'index': tempidx, 'word': word, 'keys': keys, 'timestamp': time.time()})
                    tempidx += 1
#                    logger.info(f'Adding QR {type}: {word}')
                if (len(w) == 3):
                    idx = w[0]
                    word = w[1]
                    keys = w[2].split(',')
                    ret.append({'type': type, 'lang': lang, 'index': idx, 'word': word, 'keys': keys, 'timestamp': time.time()})

                
        return ret
    
    # Snip...
    def runQRThread(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = QRWorker(self.queue)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

    def runQRInThread(self):
        # Step 2: Create a QThread object
        self.inthread = QThread()
        # Step 3: Create a worker object
        self.inworker = QRInWorker(self.inqueue)
        # Step 4: Move worker to the thread
        self.inworker.moveToThread(self.inthread)
        # Step 5: Connect signals and slots
        self.inthread.started.connect(self.inworker.run)
        self.inworker.finished.connect(self.inthread.quit)
        self.inworker.finished.connect(self.inworker.deleteLater)
        self.inthread.finished.connect(self.inthread.deleteLater)
        self.inworker.progress.connect(self.reportProgressIn)
        # Step 6: Start the thread
        self.inthread.start()



    import pyrebase

    def set_feedback(self, feedback, vars = {}, rerun=False):
        try:
            db = self.firebase.database()

            data = {"feedback": feedback}
            date_str = time.strftime("%Y%m%d")
            time_str = time.strftime("%H%M%S")
            db.child("channels").child(self.myuser['localId']).child("feedback").child(date_str).child(time_str).child(self.myuser['localId']).set(data, self.myuser['idToken'])
        except Exception as e:
            #if fail
            if (rerun):
                return
            auth = self.firebase.auth()
            user = auth.refresh(self.myuser['refreshToken'])
            self.myuser = user
            self.set_feedback(feedback, vars, True)

    def start_record(self):
        try:
            db = self.firebase.database()

            data = {"status": "recording", "timestamp": time.time()}
            #get date YYYYMMDD
            date_str = time.strftime("%Y%m%d")
            time_str = time.strftime("%H%M%S")
            mydata = db.child("channels").child(self.myuser['localId']).shallow().get(self.myuser['idToken'])
            print(mydata.val())
            db.child("channels").child(self.myuser['localId']).update(data, self.myuser['idToken'])
            data = {"feedback": "test"}
            print(data)
            db.child("channels").child(self.myuser['localId']).child("feedback").child(date_str).child(time_str).child(self.myuser['localId']).set(data, self.myuser['idToken'])
        except Exception as e:
            #if fail
            auth = self.firebase.auth()
            user = auth.refresh(self.myuser['refreshToken'])
            self.myuser = user


    def login(self):
        auth = self.firebase.auth()
        email = self.cfg["trey"]["user"]
        password = self.cfg["trey"]["pwd"]
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            # Extract the UID (localId) from the user object
            self.myuser = user
#            uid2 = user['userId']
            print(f"Successfully signed in. User UID: {self.myuser['localId']} {self.myuser['idToken']}")
            logger.info(f'Firebase login successful for {email}, UID: {self.myuser['localId']}')
            self.start_record()
        except Exception as e:
            logger.error(f'Firebase login failed: {e}')
            print(f'Firebase login failed: {e}')


    def init_fb(self):
        databaseURL = self.cfg["firebase"]["fbconfig"]["databaseURL"]
            # Init firebase with your credentials
        import pyrebase
        self.firebase = pyrebase.initialize_app({'apiKey': self.cfg["firebase"]["fbconfig"]["apiKey"], 'authDomain': self.cfg["firebase"]["fbconfig"]["authDomain"], 'databaseURL':databaseURL, 'storageBucket': self.cfg["firebase"]["fbconfig"]["storageBucket"]})    
        self.login()

    def __init__(self, q=None, inq=None, cfg=None):
        super().__init__()
        self.highlightrect = {'x': 100, 'y': 100, 'width': 200, 'height': 200}
        self.highlighton = False
        self.startx = 0
        self.queue = q
        self.inqueue = inq
        self.cfg = cfg
        self.myuser = None
        self.geo = None
        self.qr_in = []
        self.qr_out = []
        self.ocrtext = ""
        self.windowlabels = {} #list of window details by pid
        self.windowcounter = 0
        self.screenshots = [] #list of screenshots per monitor
        self.transcriber = transcriber.transcriber(self)
        if (self.cfg is not None and 'firebase' in self.cfg):
            self.init_fb()
        # set the title

        self.setWindowOpacity(0.2) 
        #Qt.WA_TransparentForMouseEvents | Qt.WindowTransparentForInput to make click-through
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WA_TransparentForMouseEvents | Qt.WindowTransparentForInput)
        screens = qapp.screens()
        logger.info('Listing available screens')
        primary_screen = qapp.primaryScreen()
        if len(screens) == 1:
            logger.info('Only one screen detected, add a second monitor to use trey overlay.')
        for i, s in enumerate(screens):
            logger.info(f'Screen {i}: {s.name()} - Size: {s.size()}')
            if (s.name() != primary_screen.name()):
                # This is a secondary screen
                logger.info(f'Screen {i} is secondary')
                geometry = s.geometry()
                # set the geometry of window
                # setting  the geometry of window
                #add window to second monitor if available
                self.setGeometry(geometry.x(), geometry.y(), geometry.width(), geometry.height())
                self.startx = geometry.x()
                self.geo = geometry

                print(f'Setting window to second monitor at {geometry.x()},{geometry.y()} size {geometry.width()}x{geometry.height()}')
                self.setWindowTitle("Trey - " + s.name())

#        self.setGeometry(60, 60, 600, 400)
        for i in range(100):
            self.windowlabels[str(i)] = QLabel(f'Label {i}', self)
        # creating a label widget
        self.label_1 = QLabel("transparent ", self)
        # moving position
        self.label_1.move(self.geo.width() - 300, 100)
        self.label_1.setStyleSheet("background-color: rgba(255, 255, 255, 1);color: red;")
        self.label_1.adjustSize()
        self.label_1.setWordWrap(True)

        self.label_2 = QLabel(self)
        #move to bottom right corner
        self.label_2.setStyleSheet("background-color: rgba(255, 255, 255, 1);")
        #not sure best size.  
        self.label_2.move(self.width() - 500, self.height() - 400)

        # show all the widgets
        self.show()
        self.showQR("Starting Trey Overlay")
        #hide after a few seconds
        #workaround, something wrong with the PyQt if we hide this immediately
        t = threading.Timer(3, _hide, args=["Hello from Timer!"])
        t.start()  # Start the timer in a new thread
        logger.info('Window created')
        self.runQRThread() #
        self.runQRInThread() #start thread to detect incoming QR data from other apps or locations..

        #start internal thread to check the queue for updates.  
        #and update the window when there is new data.  

    def save_screenshot(self, lang='hotkeys', fname='', bbox=None, ocr=False):
        """Save a screenshot of the current window."""
        screen = qapp.primaryScreen()
        screens = qapp.screens()
        logger.info('saving screenshot')
        screenshot = None
        for i, s in enumerate(screens):

            screenshot = s.grabWindow( 0 ) # 0 is the main window, you can specify another window id if needed


        self.screenshots.append(screenshot)
        logger.info('Capturing Screen')

        now = datetime.now()
        if (fname == ''):
            fname = f'{now.strftime("%Y%m%d_%H%M%S")}.png'
        folder = f'../transcripts/{lang}/' 
        if not os.path.exists(folder):
            os.makedirs(folder)
        geometry = self.geometry()

        screenshot.save(folder + fname, 'png')
        logger.info(f'Screenshot saved as {folder + fname}')
        ocrtext = ""
        if (ocr):
            #do OCR on screenshot
            img = Image.open(folder + fname)
            #get bbox area
            if (bbox is not None):
                bbox = bbox.split(',')
                bbox = [int(b) for b in bbox]
                img = img.crop((bbox[0]-self.geo.x(), bbox[2]-self.geo.y(), bbox[1]-self.geo.x(), bbox[3]-self.geo.y()))
                logger.info(f'Cropping image to bbox: {bbox}')

            ocrtext = pytesseract.image_to_string(img)

        return ocrtext, folder + fname
        
    def draw_screen_box(self, bbox=""):
        """Draws a box around the screen."""
        self.highlighton = True
        #get geometry of the highlight rectangle.  
        if (bbox !=""): #xxyy
            bbox = bbox.split(',')
            bbox = [int(b) for b in bbox]
            self.highlightrect = {'x': bbox[0], 'y': bbox[2], 'width': bbox[1]-bbox[0], 'height': bbox[3]-bbox[2]}
        else:
            geometry = self.geometry()
            self.highlightrect = {'x': geometry.x()+100, 'y': geometry.y()+100, 'width': geometry.width()-100, 'height': geometry.height()-100}
        self.update()  # Trigger a repaint to show the box
        logger.info('Screen box drawn')
        
    def hideme(self):
        """Method to close the window."""
        self.hide()
        logger.info('Window hidden')


    def showQR(self, data, struct={}):
        """Method to show a QR code."""
#        logger.info('Showing QR code')
        #adjust readable text first..
        self.label_1.setText(data)
        self.label_1.adjustSize()
        self.label_1.update()
        qrdata = data
        #if we need to truncate
        print(f'QR data length: {len(qrdata)}')
        print(qrdata[0:100] + "...\n")
        if (len(qrdata) > 1500):
            qrdata = qrdata[0:1500] #truncate to 1500 bytes max for QR code.
            qrdata += "\n...\n$$\n"
        qr_image = create_qr_code(qrdata)
#        qr_image = Image.open("qrcode.png")
#        qr_image.show()
        pixmap = QPixmap('qrcode.png')
        self.label_2.setPixmap(pixmap)
        self.label_2.adjustSize()

        logger.info('QR code displayed')

    def findLabel(self, pid):
        if (pid in self.windowlabels):
            return self.windowlabels[pid]
        elif (self.windowcounter < 100):
            label = self.windowlabels[str(self.windowcounter)]
            self.windowlabels[pid] = label
            self.windowcounter += 1
            return label
        
    def updateWords(self, pwords):
        y = 100
        for idx, pw in enumerate(pwords):
            word = pw['word']
            keys = pw['keys']
            label = self.findLabel(f'word{idx}')
            if (label is not None):
                label.setText(f'Word: {word}\nKeys: {",".join(keys)}\n')
                label.setStyleSheet("background-color: rgba(255, 255, 255, 1);color: black;")
                label.move(self.geo.width() - 500, y)
                label.adjustSize()
                label.update()
                y += label.height() + 10

    def updateLabels(self, allwindows):
        for pid, w in allwindows.items():
            label = self.findLabel(pid)
            #title, rect, other
            if (label is not None):
                label.setText(f'PID: {pid}\nTitle: {w["title"]}\nRect: {w["rect"]}\n')
                textcolor = "black"
                if (len(self.screenshots) > 0):
                    #get average color of window area
                    textcolor = get_text_color(w['rect'], self.screenshots[-1])
                    if (textcolor == "white"):
                        label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);color: white;")
                    else:
                        label.setStyleSheet("background-color: rgba(255, 255, 255, 1);color: black;")
                #label.setWordWrap(True)
                label.move(w['rect'][0]-self.startx, w['rect'][1])
                #label.resize(w['rect'][2]-w['rect'][0], w['rect'][3]-w['rect'][1])
                label.adjustSize()
                label.update()

    def paintEvent(self, event):
        if (self.highlighton):
            painter = QPainter(self) # Create a QPainter instance, passing 'self' (the widget) as the paint device.
            pen = QPen(Qt.red, 5, Qt.SolidLine)
            painter.setPen(pen)
            rect = self.highlightrect
            painter.drawRect(rect['x']-self.geo.x(), rect['y']-self.geo.y(), rect['width'], rect['height'])
#            painter.drawRect(100, 100, 200, 200)
        #    painter.drawRect(geometry.x()+100, geometry.y()+100, geometry.width()-100, geometry.height()-100)
    #        painter.setFont(painter.font()) # Use default font or set a custom one
    #        painter.drawText(50, 200, "Hello QPainter!")
            painter.end()
        
        # You can also draw text, ellipses, images, etc.

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

def skip_lines(n, cacheno=-1):
    #called from hotkeys to skip n lines of audio.
    #eventually match up audio_skip_events with playwrighty cache numbers so we can skip in specific readers if needed.
    global audio_skip_events
    print(f'Skipping {n*3} lines of audio')
    if (cacheno >=0 and cacheno < len(audio_skip_events)):
        print(f'Skipping lines in audio thread {cacheno}')
        audio_skip_queue[cacheno].put(int(n*3))
        audio_skip_events[cacheno].set()
        return
    for i, audio_skip_event in enumerate(audio_skip_events):
        print(f'Skipping lines in audio thread {i}')
        audio_skip_queue[i].put(int(n*3))
        audio_skip_event.set()

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
        midi_kill_event.set()
        midi_stop_event.set()  # Signal the MIDI thread to stop
        midi_thread.join()  # Wait for the MIDI thread to finish
        time.sleep(10)  # Give some time for the thread to exit
    else:
        midi_stop_event.set()  # Signal the MIDI thread to stop

    midiin.close()  # Close the MIDI input port
#    midiout.close()  # Close the MIDI output port


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
#    c = Communicate()
#    c.mySignal.connect(updateQR)

    with midiin as inport:
        while (not midi_stop_event.is_set()):
            while (qrin_queue is not None and not qrin_queue.empty()):
                qrdata = qrin_queue.get()
                mk.add_qrin(qrdata)
                logger.info(f'MIDI Received QR input data: {qrdata}')
                
            #get all q2 output messages.  
            mk.set_audio_location()

            for msg in inport.iter_pending():
                if msg.type == 'note_on' or msg.type == 'note_off':
                    print(msg)
                    logger.info(f'Received MIDI message: {msg}')
                    if hasattr(msg, 'note'):
                        note = msg.note
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


def init_inputs():
    global midiout, midiin
    inputs, outputs = get_midi_ports()
    logger.info(f'Available MIDI inputs: {inputs}')
    logger.info(f'Available MIDI outputs: {outputs}')
#    midiout = mido.open_output(outputs[1]) #open first output for now.  
    midiin = mido.open_input(inputs[0]) #open first input for now.

def run_midi(stop_event, kill_event, qr_queue=None, qrin_queue=None, audio_location_queue=None):
    global midiout, midiin
    global mk
    mk = mykeys.MyKeys(config.cfg, qapp, mywindow.startx, stop_event)
    logger.info('Starting MIDI input/output')
    init_inputs()
    
    #Portable Grand-1 2
    #should really have some config selection here.  
    mk.start_feedback() #play feedback if enabled.  This takes some time apparently to start thread.  
    cont = keyboard.Controller()    

    while (not kill_event.is_set()):
        handle_keys(qr_queue, qrin_queue)
        init_inputs() #re-init inputs in case something changed.
        time.sleep(0.1)  # Small delay to prevent high CPU usage
        stop_event.clear()  # Clear the event for the next iteration
        mk.start_feedback() #restart feedback if needed.

    logger.info('MIDI thread completed, unloading MK')
    mk.unload()
    logger.info('MIDI thread ended')





def restart_trey():
    on_quit_action()
    os.execl(sys.executable, sys.executable, *sys.argv)
    return 0

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
    logging.basicConfig(filename='trey.log', 
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    logger.info('Started')
    logger.info('Setting up hotkey listener')
    hotkey_listener = setup_hotkey_listener()
    logger.info('Hotkey listener set up')

    logger.info('Creating Qapplication object')
    # Create the application object
    qapp = QApplication(sys.argv)
    logger.info('Creating application window')
    # Create the main application window
    global qr_queue, qrin_queue
    qr_queue = Queue()
    qrin_queue = Queue()
    mywindow = MyWindow(qr_queue, qrin_queue, config.cfg)

    logger.info('Running icon')
    #icon.run()
    icon.run_detached()


    # Create a Thread object to listedn for MIDI messages
    # Create an event
    start_midi()



    logger.info('Executing application')

    sys.exit(qapp.exec_())
    #hiding window as we only want it on hotkey
    #window.hide()





if __name__ == "__main__":
    main()
