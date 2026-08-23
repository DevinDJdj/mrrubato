import logging
from pydoc import text
import re
import threading
from pynput import *
from extensions.trey import synth
from languages._meta import _META, _VIDEO
import pytesseract
from PIL import Image
from io import BytesIO
import win32con
import time
import os
from datetime import datetime, timedelta
import extensions.trey.playwrighty as playwrighty
# Import Module
import shutil
import json

from extensions.trey.trey import page, pause_reader, skip_lines
from extensions.trey.trey import skip_lines
import languages.helpers.transcriber as transcriber


from rapidfuzz.process import cdist
from rapidfuzz import fuzz
import numpy as np

from gliner import GLiNER

from collections import Counter

logger = logging.getLogger(__name__)

class hotkeys:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.words = []
    self.transcriber = None
    self.qapp = qapp
    self.startx = startx
    self.func = None
    self.cmd = None
    self.qr = "" #info for QR message
    self.qr_queue = None

    self.geo = None
    self.name = "hotkeys"
    self.keybot = 53 #
    self.keymid = 7 #middle C for bbox calc
    self.mid = 60 #middle C for bbox calc    
    self.keyoffset = 5 #offset within octave mapping
    self.links = []
    self.currentlinks = []
    self.windows = ["" for _ in range(100)] #for now practical limit much lower..
    self.windowslen = 0 #annoying logic here, because of preinitizliation of windows list.  
    self.currentwindowindex = 0
    self.controlstate = {'app': "", 'window': "", 'tab': ""}
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.transcript = ""
    self.suggestions = []
    self.corrections = []
    self.transcripthistory = []
    self.tofind = ""
    self.tofindhistory = []
    self.now = datetime.now()
    self.feedbacknowstr = self.now.strftime("%Y%m%d_%H%M%S")
    self.entities = []
    self.relations = []
    self.graph_thread = None
    self.funcdict = {}
    self.suggestions = []
    self.joystate = {}

  def word(self, sequence=[]):
    """Word lookup."""
    
    cmd = ""
    sl = str(len(sequence))
    if (sl in self.config['languages'][self.name]):
      logger.info(f'Looking up sequence {sequence} in hotkeys')
      logger.info(self.config['languages'][self.name][sl])
      for k,v in self.config['languages'][self.name][sl].items():
        #check global first.  
        if (sequence == v):
          #can compare directly.  if strings, we do ','.join(self.sequence[-i:]) == v
          found = True
          cmd = k
          self.cmd = cmd
    return cmd

  def unload(self):
    #unload language specific data
    #if (playwrighty.mybrowser is not None):
      #this resets playwrighty context.
      #how do we keep context?  
      #playwrighty.close_browser()

    return 0
  
  def load(self, transcriber=None, qr_queue = None):
    #load language specific data
     #config overrides load_data by default.  
    if (transcriber is not None):
      self.transcriber = transcriber
    if (qr_queue is not None):
      self.qr_queue = qr_queue
    if hasattr(self, 'load_data'):
      self.load_data()
    else:
      logger.info(f'!! <{self.__class__.__name__}> No Data')
      print(f'!! <{self.__class__.__name__}> No Data')  
    playwrighty.load(self.qapp)
    return 0


  def insert_word(self, func, sequence=[], word=""):
    """Insert word into sequence.  Word may be sentence."""

    if (func == "search_web"):
      from mykeys import text2seq
      seq = text2seq(word)
      if (len(sequence) == 1): #default case.  Have to add extra keybot
        #should be using negative index so append to beginning.
        sequence = seq + sequence + [self.keybot] #separator
      else:
        sequence = seq + sequence
      return sequence

  #general transcript loading..  
  def load_transcripts(self):
    #for now..
    allcmds = self.transcriber.read(self.name, None, None) #default 7 days
    logger.info(f'Loaded {len(allcmds)} command transcripts for {self.name}')
    #filter commands for bookmarks.  
    self.load_bookmarks2(allcmds)


    #self.load_bookmarks()

  def load_bookmarks2(self, allcmds):
    totalcmds = len(allcmds)
    numloaded = 0
    last10 = []

    for c in allcmds:
      #print(f'Processing command {c}')
      url = ''
      if (c['cmd'] == 'Add Bookmark'):
        print(f'Found bookmark command {c}')
        if ('URL' not in c['vars'] or 'TOTAL_READ' not in c['vars']):
          continue
        url = c['vars']['URL']
        total_read = int(c['vars']['TOTAL_READ'])
        body_length = int(c['vars']['BODY_LENGTH']) if 'BODY_LENGTH' in c['vars'] else 0
        text = c['vars']['TEXT'] if 'TEXT' in c['vars'] else ""
        video_no = int(c['vars']['VIDEO_NO']) if 'VIDEO_NO' in c['vars'] else 0
        video_pos = int(c['vars']['VIDEO_POS']) if 'VIDEO_POS' in c['vars'] else -1
        print(f'Loaded bookmark {url} at {total_read}')
        logger.info(f'Loaded bookmark {url} at {total_read}')
        playwrighty.add_bookmark(url, total_read, text, video_pos) #call playwrighty add bookmark..
        numloaded += 1

      elif c['cmd'].startswith('Add Bookmark'): #handle alternate old format
        parts = c['cmd'].strip().split('\t')
        if (len(parts) < 2):
          continue
        url = parts[1]
        total_read = int(parts[2])
        body_length = int(parts[3]) if len(parts) > 3 else 0
        text = parts[4] if len(parts) > 4 else ""
        video_pos = int(parts[5]) if len(parts) > 5 else -1
        print(f'Loaded bookmark {url} at {total_read}')
        playwrighty.add_bookmark(url, total_read, text, video_pos) #call playwrighty add bookmark..
        numloaded += 1
            
      if url != "":
        url = playwrighty.get_unique_url(url) #normalize url for bookmark list.
        if (url in last10):
          last10.remove(url)
        last10.append(url)
        if len(last10) > 10:
          last10.pop(0)

    logger.info(f'Last 10 bookmark URLs: {last10}')
    playwrighty.last10 = last10
        
    logger.info(f'Loaded {numloaded} bookmarks from {totalcmds} commands')

  #really should load all data in same iteration..
  def load_bookmarks(self):
    #load bookmarks from file for this date.  
    #maybe playwrighty should handle this?
    #get date as YYYYMMDD
    #for now just open most recent file.
    today = datetime.now().strftime("%Y%m%d")
    logger.info(f'Loading bookmarks')
    #yesterday also    
    yesterday = (datetime.now() - timedelta(1)).strftime("%Y%m%d")
    #list all files in directory
    files = os.listdir('../transcripts/' + self.name)
    sorted_files = sorted(files)
    numloaded = 0
    print(sorted_files)
    for f in sorted_files:
#      if (f.startswith(yesterday) or f.startswith(today)):
        if (f.endswith('.txt')): #dont open wav files..
          print(f'> Read Bookmarks {f}') 
          try:
            with open('../transcripts/' + self.name + '/' + f, encoding='utf-8') as ff:
              lines = ff.readlines()
              for line in lines:
                #add bookmark manually.  
                parts = line.strip().split('\t')
                cmd = parts[0]
                if (cmd == '> Add Bookmark'):
                  url = parts[1]
                  total_read = int(parts[2])
                  body_length = int(parts[3]) if len(parts) > 3 else 0
                  text = parts[4] if len(parts) > 4 else ""

                  print(f'Loaded bookmark {url} at {total_read}')
                  video = parts[5] if len(parts) > 5 else 'False'
                  playwrighty.add_bookmark(url, total_read, text, video) #call playwrighty add bookmark..
                  numloaded += 1
          except Exception as e:
            logger.error(f'!!>Read Bookmarks [{f}]\n !!{e}')

    #list files in 
    logger.info(f'Loaded {numloaded} bookmarks from {len(sorted_files)} files')
    return 0    
  

  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
#        "Start": [53,54], #read from this cache page current point.  
        "Pause": [53,52],
        "Resume": [53,54],
        "Read Screen": [53,50],
#        "Page": [53,57],
      },
      "3": {
        "Stop": [53,55,54],
        "Skip Lines": [53,55,57],
        "Page": [53,55,59], #also read screen
        "Click Link": [53,55,60], #also read screen
        "Find": [53,55,58], #Jump in screen
        "Next": [53,55,56], #go to next location where this text is found..
        "Search Web": [53,55,61], #also read screen
        "Go Back": [53,55,51], 
        "Ask": [53,55,52],
        "Close Tab": [53,56,59],
        "List Tabs": [53,56,61],
        "Select Tab": [53,56,60],
        "Select Window": [53,56,58],
        "Close Window": [53,56,57],

        "Comment": [53,57, 58], #record comment
        "Record Feedback": [53,57,60], 
        "Select Bookmark": [53,58,57], #feedback tells which mark it is.  Or default to set to 0 idx.  
      }, 
      "4": {
        "Add Bookmark": [53,58,60,62], #feedback tells which mark it is.  Or default to set to 0 idx.  
        #manually select 0 idx = [53,58,60,62,53,53,53]
        "List Bookmarks": [53,58,60,63], #no params
      }
    }

    if (self.name in self.config['languages']):
      logger.info(f'Merging existing {self.name} config')
      #need logic to iterate and pick each one.  This is not working right.  
      default.update(self.config['languages'][self.name])
      for sl in self.config['languages'][self.name]:
        #check for each word
        if (sl not in default):
          default[sl] = {}
        if (sl != 'keybot'):
          for k in self.config['languages'][self.name][sl]:              
            default[sl][k] = self.config['languages'][self.name][sl][k]

      if ('keybot' in self.config['languages'][self.name]):
        default['keybot'] = self.config['languages'][self.name]['keybot']
        self.keybot = default['keybot']
      #update all others based on any keybot change.
      for sl in default:
        if (sl != 'keybot'):
          for k in default[sl]:
            #update all sequences by diff.
            seq = default[sl][k]
            #this allows to 0 index or any index if preferred..
            #easier to port relative words from other languages..
            #eventually probably get used to 0-indexing
            innerdiff = self.keybot - seq[0]
            if (len(seq) > 1): #dont update single key sequences. Eventually this shouldnt exist I think..
              for i in range(len(seq)):
                seq[i] += innerdiff

            default[sl][k] = seq
            print(f'Updated {sl} {k} sequence to {seq}')
    else:
      logger.info(f'No existing {self.name} config found, creating new one')

    self.config['languages'][self.name] = default
    self.funcdict = {
      "Stop": "stop_me",
      "Pause": "pause_reader",
      "Resume": "resume_reader",
      "Go Back": "go_back",
      "Start": "start_me",
      "Read Screen": "read_screen",
      "Skip Lines": "skip_lines",
      "Page": "page",
      "Click Link": "click_link",
      "_Click Link": "_click_link",
      "Next": "next",
      "Find": "find",
      "_Find": "_find",
      "_Ask": "_ask",
      "Ask": "ask",
      "Search Web": "search_web",
      "Comment": "comment",
      "Select Type": "select_type",
      "List Tabs": "list_tabs",
      "Select Tab": "select_tab",
      "Select Window": "select_window",
      "Close Tab": "close_tab",
      "_Search Web": "_search_web",
      "Search Web_": "search_web_",
      "Add Bookmark": "add_bookmark",
      "List Bookmarks": "list_bookmarks", 
      "Select Bookmark": "select_bookmark", 
      "Record Feedback": "record_feedback"
    }

    self.helpdict = {
      "Stop": {
"> ": "stop", 
"$$": "$cacheno", 
"&&": "Stop/Pause audio."},
      "Comment": {
"> ": "0=$DUR=5 seconds\n1=$DUR*3 seconds", 
"$$": "$DUR (audio duration), &comment", 
"&&": "Add comment to current book."},
      "Resume": {
"> ": "resume", 
"$$": "$cacheno", 
"&&": "Start/Resume reading."},
      "Go Back": {
"> ": "go back", 
"$$": "None", 
"&&": "Go back to previous page."},
      "Start": {
"> ": "start", 
"$$": "None", 
"&&": "Not implemented."},
      "Read Screen": {
"> ": "read screen", 
"$$": "$cacheno", 
"&&": "0=read browser tab\n1=take screenshot, OCR, read"},
      "Skip Lines": {
"> ": "skip lines", 
"$$": "$N*3", 
"&&": "Skip $N*3 lines"},
      "Page": {
"> ": "page", 
"$$": "$N*20", 
"&&": "Not implemented.  \nSkip $N*20 lines."},
      "Click Link": {"> ": "click link", 
"> ": "click link", 
"$$": "$linkno", 
"&&": "0=current\n1=$linkno"},
      "Ask": {
"> ": "ask",
"$$": "$cacheno, $direction, $strictness, &Query",
"&&": "0=Ask &Query\n1=Ask &Query from $cacheno\n2=Ask &Query from $cacheno in $direction\n3=Ask &Query from $cacheno in $direction with $strictness\nResponse can be quite long, just basic LLM query using long context from page.  "},
      "Find": {
"> ": "find", 
"$$": "&Keyword", 
"&&": "Find in page.."},
      "Search Web": {
"> ": "search web", 
"$$": "$cacheno, $engine, &keyword", 
"&&": "0=Search web for &Keyword\n1=Search web with $engine for &Keyword\n2=Search web using $cacheno with $engine for &Keyword"},
      "List Tabs": {
"> ": "list tabs", 
"$$": "None", 
"&&": "List all open browser tabs."},
      "Close Tab": {
"> ": "close tab", 
"$$": "$Tab", 
"&&": "Close specified browser tab."},
      "Select Tab": {
"> ": "select tab", 
"$$": "$Tab", 
"&&": "Select specified browser tab."},
      "Select Window": {
"> ": "select window", 
"$$": "$Window", 
"&&": "Select specified trey window to foreground."},
      "Add Bookmark": {
"> ": "add bookmark", 
"$$": "None", 
"&&": "Add a bookmark at the current position."},
      "List Bookmarks": {
"> ": "list bookmarks", 
"$$": "None", 
"&&": "List all bookmarks."},
      "Select Bookmark": {
"> ": "select bookmark", 
"$$": "$Bookmark", 
"&&": "Select specified bookmark."},
      "Record Feedback": {
"> ": "record feedback", 
"$$": "$DUR, &Feedback", 
"&&": "Record $DUR seconds of &Feedback for recall and training."}
    }      

    self.load_transcripts()
    return 0  

  
  #act differently based on words in sequence.    
  def act(self, cmd, words=[], sequence=[], doact=True):
    self.words = words

    """ACT based on command and sequence."""
    if (not doact):
      if (len(sequence) == 1 and sequence[-1] == self.keybot):
        return 0
      elif (len(sequence) > 1 and sequence[-2:] == [self.keybot, self.keybot]):
        return 0
      else:
        return 1 #need more keys.

    logger.info("-> "+ cmd + " " + str(sequence))
    #need _ prefix in funcdict.  
    if (len(sequence) == 0 and "_" + cmd in self.funcdict):
      #run prefix command
      logger.info("-_> "+ cmd + " " + str(sequence))
      func = self.funcdict["_" + cmd]
      if hasattr(self, func):
        return getattr(self, func)(sequence)
      
    elif cmd in self.funcdict:
      logger.info("--> "+ cmd + " " + str(sequence))
      func = self.funcdict[cmd]
      #all require keybot at end.

      #this function called every time a key is pressed.


      if hasattr(self, func + "_"):
        #no return here..
        if getattr(self, func + "_")(sequence) > 0:
          #function not yet complete..
          a = 0
        else:
          logger.info(f'--> {func}_')
          if (len(sequence) == 1 and sequence[-1] == self.keybot):
            a = 0 #continue logic and see if we need to end.  
          elif (len(sequence) > 1 and sequence[-2:] == [self.keybot, self.keybot]):
            a = 0 #continue logic and see if we need to end.
          else:
            return -len(sequence)-1 #indicate handled, can look for other words from what position

      if hasattr(self, func):
        if (len(sequence) == 1 and sequence[-1] == self.keybot):
          return getattr(self, func)(sequence[:-1])
        elif (len(sequence) > 1 and sequence[-2:] == [self.keybot, self.keybot]):
          return getattr(self, func)(sequence[:-2])
        else:
          return 1 #need more keys.
      else:
        logger.error(f"Function {func} not found in {self.__class__.__name__}")



      
    else:
      print(f"{self.funcdict}")
      logger.info(f"{self.funcdict}")
      logger.error(f"Command {cmd} not found in function maps")
      print(f"Command {cmd} not found in function maps")
    return -1
  

  def load_state(self):
    #pick latest bookmark.. 
    #not used currently..
    self.select_bookmark()

  def save_state(self):
    #for now just save_bookmark.  eventually save more state here.
    self.add_bookmark()
    
  def set_audio_location(self):
    #set audio location queue for this language.  
    #set to last one only.
    #dont actually need param...
    playwrighty.update_page_offset()

  #state = foreground window + tab state for browser..
  def get_app_state(self):
    #get current state of this language.  For now just return current window and tab.
    
    self.controlstate['window'] = self.windows[self.currentwindowindex] if (self.windowslen > self.currentwindowindex) else ""
    if ('google chrome for testing' in self.controlstate['window']):
      self.controlstate['app'] = "chrome"
    elif ('mrroboto' in self.controlstate['window']):
      self.controlstate['app'] = "mrroboto"
    #dont reset, handle the last state..
#    else:
#      state['app'] = ""
    return self.controlstate
  #vscode
  #playwrighty

  def add_joystate(self, cmd):

    joy = cmd['vars']['SEQ'][0]
    type = cmd['cmd']
    register = cmd['vars']['SEQ'][1]
    value = cmd['vars']['SEQ'][2]
    prev_state = self.joystate.get(type, {}).get(joy, {}).get(register, None)
    if prev_state is not None:
      prev_state = prev_state.copy()

    if type not in self.joystate:
      self.joystate[type] = {}
    if (joy not in self.joystate[type]):
      self.joystate[type][joy] = {}
    if (register not in self.joystate[type][joy]):
      self.joystate[type][joy][register] = {'_': value, '(': time.time(), ')': time.time()}
    else:
      if (prev_state.get('_', None) != value):
        self.joystate[type][joy][register]['_'] = value
        self.joystate[type][joy][register]['('] = time.time()  # Update the timestamp for the last change
        self.joystate[type][joy][register][')'] = time.time()  # Update the timestamp for the last change
      else:
        self.joystate[type][joy][register][')'] = time.time()  # Update the timestamp for the last change
    return prev_state, self.joystate[type][joy][register]

  def handle_joystick(self, cmd):
    #translate joystick commands to actions.  
    #held key actions..
    if ('vars' not in cmd or 'SEQ' not in cmd['vars'] or len(cmd['vars']['SEQ']) < 3):
      logger.error(f'!!Invalid joystick command\n{cmd}')
      return -1
    elif ('cmd' not in cmd or cmd['cmd'] not in ['AXIS', 'BUTTON', 'HAT']):
      logger.error(f'!!Invalid joystick command type {cmd.get("cmd", None)}\n{cmd}')
      return -1
    app_state = self.get_app_state()
    prev_state, current_state = self.add_joystate(cmd)
    logger.info(f'{prev_state} {current_state}')
    if (prev_state is not None and prev_state['_'] == current_state['_']):
      #no change in state, ignore
      #what lag do we want here?  
      if (current_state[')'] - current_state['('] < 2): #ignore changes less than 2 second, give chance for some feedback lag..
        return 1
    else:
      logger.info(f'Joystick state changed from {prev_state} to {current_state}')
      current_state['('] = time.time()  # Update the timestamp for the last change']
      current_state[')'] = time.time()  # Update the timestamp for the last change

    if (app_state['app'] == "mrroboto"):
      a = 0
      if (cmd['cmd'] == 'AXIS'):
        logger.info(f'axis {cmd}') #joy, axis, value
        #all depends on state.  example..
        if ('vars' in cmd and 'SEQ' in cmd['vars'] and len(cmd['vars']['SEQ']) > 2):
          #use first axis for now.  
          if (cmd['vars']['SEQ'][1] == 1):
            if (cmd['vars']['SEQ'][2] < -0.5):
              #up = cursor up
              a = 0
            elif (cmd['vars']['SEQ'][2] > 0.5):
              #down = cursor down
              a = 0
          elif (cmd['vars']['SEQ'][1] == 0):
            if (cmd['vars']['SEQ'][2] > 0.5):
              # right = next tab (hold)
              a = 0
            elif (cmd['vars']['SEQ'][2] < -0.5):
              # left = previous tab (hold)
              a = 0

      elif (cmd['cmd'] == 'BUTTON'):
        #handle joystick buttons.  For now just log it.  
        logger.info(f'Joystick button {cmd}') #joy, button, on/off
        #use for heldwords..
        if ('vars' in cmd and 'SEQ' in cmd['vars'] and len(cmd['vars']['SEQ']) > 2):
          #use first button for now.  
          button_down = cmd['vars']['SEQ'][2]
          match (cmd['vars']['SEQ'][1]):
            case 0: #R1 top right
              if (button_down == 1):
                #button 0 pressed
                a = 0
              if (button_down == 0):
                #button 0 released
                a = 0
            case 1: #R1 bottom right
              if (button_down == 1):
                #button 1 pressed
                a = 0
              elif (button_down == 0):
                #button 1 released
                a = 0
            case 3: #R1 bottom left
              #play/pause button. or 
              if (button_down == 1):
                #button 3 pressed
                a = 0
              elif (button_down == 0):
                #button 3 released
                #skip reader or playing video for held value..?  
                a = 0
            case 4: #R1 top left button
              if (button_down == 1):
                #button 4 pressed
                a = 0
              elif (button_down == 0):
                #hold for window selection
                #button 4 released
                #if < 0.5 seconds,switch to chrome
                a = 0
            case 6: #go
              if (button_down == 1):
                #button 6 pressed = execute current selection..
                a = 0
              elif (button_down == 0):
                #button 6 released
                a = 0
            case 7: #back
              if (button_down == 1):
                #button 7 pressed = go back
                a = 0
              elif (button_down == 0):
                #button 7 released
                a = 0
        #7 = back
        #6 = execute?  
        #0 = 
        #show which heldword will be triggered immediately.  
        #use 1 second delay?  
      elif (cmd['cmd'] == 'HAT' or cmd['cmd'] == 'BALL'):
        #handle joystick axes, time control?  
        # For now just log it.  
        logger.info(f'Joystick ball/hat {cmd}') #joy, ball/hat, value
        #play or pause..

    elif (app_state['app'] == "chrome"):
      a = 0
      if (cmd['cmd'] == 'AXIS'):
        logger.info(f'axis {cmd}') #joy, axis, value
        #all depends on state.  example..
        if ('vars' in cmd and 'SEQ' in cmd['vars'] and len(cmd['vars']['SEQ']) > 2):
          #use first axis for now.  
          if (cmd['vars']['SEQ'][1] == 1):
            if (cmd['vars']['SEQ'][2] < -0.5):
              #up = scroll up
#              playwrighty.get_ppage().mouse.wheel(0, -100) #scroll up
              try:
#                logger.info(playwrighty.get_ppage().title())
                playwrighty.get_ppage(-1, False).evaluate("() => window.scrollBy(0, -100)")
              except Exception as e:
                logger.error(f'Error scrolling up: {e}')
              a = 0
            elif (cmd['vars']['SEQ'][2] > 0.5):
              #down = scroll down
#              playwrighty.get_ppage().mouse.wheel(0, 100) #scroll down
              try:
#                logger.info(playwrighty.get_ppage().title())
                playwrighty.get_ppage(-1, False).evaluate("() => window.scrollBy(0, 100)")
              except Exception as e:
                logger.error(f'Error scrolling down: {e}')
              a = 0
          elif (cmd['vars']['SEQ'][1] == 0):
            current = playwrighty.current_cache
            if (cmd['vars']['SEQ'][2] > 0.5):
              # right = next tab              
              #just use our control..
              self.select_tab([self.mid+1])
#              playwrighty.get_ppage().keyboard.press("Control+Tab") #next tab
              a = 0
            elif (cmd['vars']['SEQ'][2] < -0.5):
              # left = previous tab
              self.select_tab([self.mid-1])
#              playwrighty.get_ppage().keyboard.press("Control+Shift+Tab") #previous tab
              a = 0

      elif (cmd['cmd'] == 'BUTTON'):
        #handle joystick buttons.  For now just log it.  
        logger.info(f'Joystick button {cmd}') #joy, button, on/off
        #use for heldwords..
        if ('vars' in cmd and 'SEQ' in cmd['vars'] and len(cmd['vars']['SEQ']) > 2):
          #use first button for now.  
          button_down = cmd['vars']['SEQ'][2]
          match (cmd['vars']['SEQ'][1]):
            case 0: #R1 top right
              if (button_down == 1):
                #button 0 pressed = ask
                #_ask
                self._ask()
                a = 0
              if (button_down == 0):
                #ask
                self.ask() #ask current page for query
                #button 0 released
                a = 0
            case 1: #R1 bottom right
              if (button_down == 1):
                #skip to current location
                a = 0
              elif (button_down == 0):
                #button 1 released
                a = 0
            case 3: #R1 bottom left
              #play/pause button. or 
              if (button_down == 1):
                #button 3 pressed
                a = 0
              elif (button_down == 0):
                #button 3 released
                #skip reader or playing video for held value..?  
                a = 0
            case 4: #R1 top left button
              if (button_down == 1):
                #button 4 pressed
                a = 0
              elif (button_down == 0):
                #hold for window selection
                #button 4 released
                #if < 0.5 seconds,switch to mrroboto
                a = 0
            case 6: #go
              if (button_down == 1):
                #button 6 pressed = click link                
                self.click_link() #click current link
                a = 0
              elif (button_down == 0):
                #button 6 released
                a = 0
            case 7: #back
              if (button_down == 1):
                #button 7 pressed = go back
                self.go_back() #go back in browser
                a = 0
              elif (button_down == 0):
                #button 7 released
                a = 0
        #7 = back
        #6 = execute?  
        #0 = 
        #show which heldword will be triggered immediately.  
        #use 1 second delay?  
      elif (cmd['cmd'] == 'HAT' or cmd['cmd'] == 'BALL'):
        #handle joystick axes, time control?  
        # For now just log it.  
        logger.info(f'Joystick ball/hat {cmd}') #joy, ball/hat, value
        #play or pause..




  def qr_in(self, cmds):
    #handle incoming QR data. 
    #used for internal comms as well.. should change queue for that..
    for c in cmds:
      if (c['lang'] == 'joystick'):
        logger.info(f'Joystick {c}')
        #handle joystick/midi input.  For now just log it.  
        self.handle_joystick(c)
      elif (c['lang'] == 'midi'):
#        logger.info(f'MIDI QR {c}')
        a = 0
      else:
        if (c['type'] == '> ' and c['cmd'] == 'Add Bookmark'):
          #open the page.  
          url = c['vars']['URL'] if 'URL' in c['vars'] else ""
          total_read = int(c['vars']['TOTAL_READ']) if 'TOTAL_READ' in c['vars'] else 0
          body_length = int(c['vars']['BODY_LENGTH']) if 'BODY_LENGTH' in c['vars'] else 0
          text = c['vars']['TEXT'] if 'TEXT' in c['vars'] else ""
          if (url != ""):
            logger.info(f'#{url}\n{total_read}')
            playwrighty.open_browser() #in case not open already..
            playwrighty.add_bookmark(url, total_read, text) #call playwrighty add bookmark..
            playwrighty.read_page(url, -1) #cacheno -1 means load new page if not already open.  
        if (c['type'] == '> ' and c['cmd'] == 'Send Windows'):
          logger.info(f'Send Windows {c}')
          for i, v in c['vars'].items():
            n = i
            if n.isdigit():
              self.windows[int(n)] = v
              self.windowslen = max(self.windowslen, int(n)+1)
          #always set windowindex back to 0 for now..
          self.currentwindowindex = 0
        if (c['type'] == '> ' and c['cmd'] == 'Stop'):
          playwrighty.pause_video()



  def set_qr(self, func, param={}):
    """Set QR."""
    self.qr = "> " + func + "\n"
    if ('timestamp' not in param):
      param['timestamp'] = time.time()
    for k,v in param.items():
        if isinstance(v, str):
            tv = v.replace('\n', '\t')
        else:
            tv = v
        self.qr += f"$${k}={tv}\n"
    self.qr += "$$\n"
    return 0
  
  def comment_(self, sequence=[]):
    if (len(sequence) == 1):

      logger.info(f'> Comment_ {sequence}')

      print("> Comment_ called")
      #get audio input for query.  
      duration = sequence[0]-self.keybot #in seconds
      duration *=3  #double duration for feedback
      from extensions.trey.speech import listen_audio
      self.now = datetime.now()
      self.commentnowstr = self.now.strftime("%Y%m%d_%H%M%S") #set nowstr for feedback.  

      at = listen_audio(duration, "comment.wav")
      #at.join() #wait for it to finish.
      #have to just use some keys until this is done.  
      #need to return 1 to indicate we need more keys.
      #but this is only called once.  

      return 0 #handled, this function will not be called again with further parameters.
    else:
      #get real-time input
      from extensions.trey.speech import transcribe_now
      self.func = "Comment_"
      self.transcript += transcribe_now() + "\n"
      self.set_qr(self.func, {'transcript': self.transcript})
      #update display.  


    return 1
  
  def comment(self, sequence=[]):
    #start recording on 0, but return 1

    from extensions.trey.speech import transcribe_audio, get_duration, transcribe_audio_whisper
    timer = datetime.now()
#    self.transcript = transcribe_audio("feedback.wav")
#    self.transcript = transcribe_audio_whisper("comment.wav") #try whisper for better accuracy.  This is slower but hopefully more accurate, especially for short feedback.

    from extensions.trey.speech import transcribe_audio, listen_audio, get_duration, transcribe_audio_whisper

    logger.info(f'> Comment {sequence}')
    #stop recording.  for now just using fixed 10 seconds.  
    #needs to be async to do this properly.
    timer = datetime.now()

    self.transcript = transcribe_audio_whisper("comment.wav")
    dur = get_duration("comment.wav") #actual dynamic duration..
    if (dur == 0):
      duration = (timer - self.now).total_seconds() if self.now is not None else duration
    else:
      duration = dur

    lag = (datetime.now() - timer).total_seconds()
    lag = int(lag)
    print(f'Transcription completed in {lag} seconds: {self.transcript}')

    try:
      vars = {}
      vars['DURATION'] = duration
      vars['COMMENT'] = self.transcript
      vars['LAG'] = lag
      fname = '../transcripts/' + self.name + '/' + self.commentnowstr + '.wav'
      vars['FILE'] = fname
      shutil.copy('comment.wav', fname) #keep a copy for training..
      self.transcriber.write(self.name, "Comment", vars)  
      logger.info(f'> Comment& {vars}')
      self.transcriber.write_topic(self.name, "", self.transcript, saveTranscript=False, saveBook=True)

    except Exception as e:
      print(f'Error writing comment file: {e}')

    return 0

  def close_tab_(self, sequence=[]):
    #close current tab.  if param given, close that tab.
    if (len(sequence) > 0):
      logger.info(f'> Close Tab_ {sequence}')
      if (playwrighty.mybrowser is not None):
        vars = {}
        for (i, page_info) in enumerate(playwrighty.page_cache[-15:]):          
          print(f'Tab {i}: {page_info["url"]}')
#          logger.info(f'Tab {i}: {page_info["url"]}')
          vars[str(i)] = page_info["title"]


        self.func = "Close Tab_"
        tabno = sequence[-1]-self.keybot
        if (tabno < 0 or tabno >= len(playwrighty.page_cache)):
          tabno = len(playwrighty.page_cache)-1

        vars['idx'] = tabno

        self.set_qr(self.func, vars)
        self.speak(f'--{playwrighty.page_cache[tabno]["title"]}')
    return 1 #need more keys to close tab.


  def close_tab(self, sequence=[]):
    #default 0 tab closed..
    
    logger.info(f'> Close Tab {sequence}')
    if (playwrighty.mybrowser is not None):
      if (len(sequence) > 0):
        cacheno = sequence[-1]-self.keybot - 1
      else:
        cacheno = playwrighty.current_cache
      if (cacheno < 0 or cacheno >= len(playwrighty.page_cache)):
        cacheno = len(playwrighty.page_cache)-1
      playwrighty.close_tab(cacheno)
    return 0
  
  def list_tabs(self, sequence=[]):
    logger.info(f'> List Tabs {sequence}')
    if (playwrighty.mybrowser is not None):
      for i, page_info in enumerate(playwrighty.page_cache):
        print(f'Tab {i}: {page_info["url"]}')
        self.speak(f'Tab {i}: {page_info["title"]}')
    else:
      print('No browser session active.')
      self.speak('No browser session active.')
    return 0

  def list_bookmarks(self, sequence=[]):
    logger.info(f'> List Bookmarks {sequence}')
    #for now just demo..


    return 0

  def select_bookmark(self, sequence=[]):
    selected = 0
    cacheno = -1
    if (len(sequence) == 0):
      selected = 0
    if (len(sequence) > 0):
      selected = sequence[-1]-self.keybot
    if (len(sequence) > 1):
      cacheno = sequence[0] -self.keybot - 1

    logger.info(f'> Select Bookmark {sequence}')
    #get bookmark at index selected
    bookmark = playwrighty.get_bookmark_at_index(selected)

    #should keep 0 index as most recent.  
    if (bookmark is not None):
      url = bookmark['url']
      total_read = bookmark['total_read']
      print(f'Selected Bookmark {selected}: {url} at {total_read}')
      #get readable text
      urlt = url.rsplit('/', 1)[-1]
      self.speak(f'Selected Bookmark {selected}: {urlt}')
      #load page at this bookmark
      body_text, link_data, page, cacheno = playwrighty.read_page(url, cacheno)
      self.controlstate['app'] = "chrome"
      self.links = link_data
      #pause audio first..

      q2, q3, stop_event = self.speak(body_text, link_data, playwrighty.page_cache[cacheno]['alt_text'], total_read=total_read, cacheno=cacheno)
      playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)

  def add_bookmark(self, sequence=[]):
    logger.info(f'> Add Bookmark {sequence}')
    #do this also on pause..
    #for now just demo..
    #how to store local data for this?  
    #readable file?  Just use date for now..
    #get URL and location in page.  
    cacheno = -1
    if (playwrighty.mybrowser is not None):
      if (len(sequence) > 0):
        cacheno = sequence[-1]-self.keybot
      
      if (cacheno > -1 and cacheno < len(playwrighty.page_cache)):
        cacheno = cacheno
      else:
        cacheno = playwrighty.current_cache

      logger.info(f'$$cacheno={cacheno}')
      logger.info(f'$$current={playwrighty.current_cache}')
      page = playwrighty.get_ppage(cacheno, False) #dont activate.. we are closing sometimes..
      url = page.url
      total_read = 0
      total_read = playwrighty.update_page_offset(cacheno)
      #get date as YYYYMMDD

      today = datetime.now().strftime("%Y%m%d")
      #find URL in bookmarks already?
      body_text = playwrighty.page_cache[cacheno]['body']
      text = playwrighty.get_snippet(body_text, total_read) if body_text is not None else ""

      playwrighty.add_bookmark(url, total_read, text)
      body_length = playwrighty.page_cache[cacheno]['length'] if cacheno >=0 and cacheno < len(playwrighty.page_cache) else 0

      if (url != "" and url != "about:blank"):
        playwrighty.transcribe_bookmark(url, transcriber=self.transcriber, name=self.name)
#        self.transcriber.write(self.name, "Add Bookmark", {
#          'URL': url,'TOTAL_READ': total_read,'BODY_LENGTH': body_length,'TEXT': text
#        })  
      """
      os.makedirs('../transcripts/' + self.name, exist_ok=True)
      #add utf-8?  
      with open('../transcripts/' + self.name + '/' + today + '.txt', 'a', encoding='utf-8') as f:        
        f.write(f'> Add Bookmark\t{url}\t{total_read}\t{body_length}\t{text}\n')
        f.write(f'$$URL={url}\n')
        f.write(f'$$TOTAL_READ={total_read}\n')
        f.write(f'$$BODY_LENGTH={body_length}\n')
        f.write(f'$$TEXT={text}\n')
        f.write(f'$$TIME={datetime.now().strftime("%Y%m%d %H%M%S")}\n')
        f.write(f'$$\n')
        #dont worry about duplication at this point.
"""


    return 0


  def adjust_window_index(self, idx=0):
    if idx+self.currentwindowindex < 0:
      return 0
    elif (idx+self.currentwindowindex) >= self.windowslen:
      return self.windowslen-1
    else:
      return self.currentwindowindex + idx
    return self.currentwindowindex
  
  def adjust_playwrighty_index(self, idx=0):
    if idx+playwrighty.current_cache < 0:
      return 0
    elif (idx+playwrighty.current_cache) >= len(playwrighty.page_cache):
      return len(playwrighty.page_cache)-1
    else:
      return playwrighty.current_cache + idx
    return playwrighty.current_cache
  
  def select_tab_(self, sequence=[]):
    self.func = "Select Tab_"
    vars = {}
    cacheno = 0
    if (len(sequence) > 0) and sequence[-1] != self.keybot:

      logger.info(f'> Select Tab_ {sequence}')
      print("> Select Tab_")
        #find the current link from our reading.  
      testing = True
      if (playwrighty.mybrowser is not None and testing):


        cacheno = self.adjust_playwrighty_index(self.mid-sequence[-1])


        self.speak(f'--{playwrighty.page_cache[cacheno]["title"]}')
      last15 = playwrighty.page_cache[max(0, playwrighty.current_cache-11):min(playwrighty.current_cache+13, len(playwrighty.page_cache))]
      last15.reverse() #reverse to match with Future:Past order in display.. [48 - 68]
      start = 0
      if len(playwrighty.page_cache) < 12:
        start = 12 - len(playwrighty.page_cache) + playwrighty.current_cache + 1
        vars['idx'] = playwrighty.current_cache
        vars[':'] = playwrighty.current_cache
      else:
        vars['idx'] = playwrighty.current_cache
      for i, l in enumerate(last15):
        n = i + start
        vars[f'{n}'] = l['title']
  #          vars[f'href{i}'] = l['href']
      self.set_qr(self.func, vars)
      vars['idx'] = cacheno
      #show title..
      vars['title'] = playwrighty.page_cache[cacheno]["title"]

      self.set_qr(self.func, vars)
    return 1
  
  def select_tab(self, sequence=[]):
    logger.info(f'> Select Tab {sequence}')
    if (playwrighty.mybrowser is not None):
      select_index = playwrighty.current_cache
      with open(f"./temp/{select_index}/active.txt", "w") as f: #deactivate generatetts
        f.write("no")
      if (len(sequence) > 0):
        select_index = self.adjust_playwrighty_index(self.mid-sequence[-1])
      logger.info(f'Selecting Tab with index {select_index} of {len(playwrighty.page_cache)}')
      if (select_index >= 0 and select_index < len(playwrighty.page_cache)):
        from extensions.trey.trey import pause_reader, resume_reader, stop_audio
        stop_audio(playwrighty.current_cache) #stop audio to ensure it stops immediately.
        #should start from here again..
        time.sleep(0.5) #wait for pause to take effect.  Need better way to ensure this.
        playwrighty.current_cache = select_index
        page = playwrighty.page_cache[select_index]['page']
        print(f'Switched to Tab {select_index}: {page.url}')
        self.speak(f'Switched to Tab {select_index}')#: {playwrighty.page_cache[select_index]["title"]}')
        #read page from current offset.  
        body_text, link_data, page, cacheno = playwrighty.read_page('', select_index)
        self.links = link_data
        #pause audio first..

        q2, q3, stop_event = self.speak(body_text, link_data, playwrighty.page_cache[cacheno]['alt_text'], total_read=playwrighty.get_bookmark(page.url, cacheno), cacheno=cacheno)
        playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)

    else:
      print('No browser session active.')
      self.speak('No browser session active.')
    return 0

  def _ask(self, sequence=[]):
    logger.info(f'> _Ask {sequence}')
    self.corrections = [] #reset corrections for this query.
    self.suggestions = [] #reset suggestions for this query.
    print("> _Ask called")
    #get audio input for query.  
    from extensions.trey.speech import listen_audio
    self.transcript = "" #reset transcript..
    at = listen_audio(15, "ask.wav") #assume some more time for question..
    #at.join() #wait for it to finish.
    #have to just use some keys until this is done.  
    #need to return 1 to indicate we need more keys.
    #but this is only called once.  
    return 1


  def get_transcript(self):
    for c in self.corrections:
      #for now just global replace.  Possible we have issue with identifying from transcript_now use of ...
      self.transcript = self.transcript.replace(c[0], c[1])
    return self.transcript

  
  def ask_(self, sequence=[]):
    from extensions.trey.speech import transcribe_now

    self.func = "ask_"

    if (len(sequence) > 0 and sequence[-1] >= self.mid and sequence[-1] - self.mid < len(self.suggestions)):
      #select suggestion
      selected = sequence[-1] - self.mid
      s = self.suggestions[selected]
      self.corrections.append(s)

    
    lag = time.time()
    self.transcript = self.get_transcript() + transcribe_now().replace('...', '') 
    context, start_offset, end_offset = playwrighty.get_p_context(cacheno=-1, direction=0, strictness=0)
    suggestions = []
#    suggestions = self.get_suggestions(context, self.transcript)

    vars = {'transcript': self.transcript}
    startidx = 12
    for i, (s, idx) in enumerate(suggestions):
      vars[f'{startidx + i}'] = s[max(0, idx-10):idx+20] #show snippet of suggestion
    lag = time.time() - lag
    vars['...'] = lag
    self.set_qr(self.func, vars)
    self.suggestions = suggestions


    return 1
  
  def _find(self, sequence=[]):  
    logger.info(f'> _Find {sequence}')
    print("> _Find called")
    #get audio input for query.  
    from extensions.trey.speech import listen_audio
    at = listen_audio(5, "find.wav")
    #at.join() #wait for it to finish.
    #have to just use some keys until this is done.  
    #need to return 1 to indicate we need more keys.
    #but this is only called once.  
    return 1

  def next(self, sequence=[]):  
    logger.info(f'> Next {sequence}')
    print("> Next called")
    #no function, just demo..
    cacheno = -1
    if (len(sequence) > 0):
      cacheno = sequence[0]-self.keybot

    offset = playwrighty.pnext(self.tofind, cacheno)
    print(f'Found at offset {offset}')
    logger.info(f'$$FOUND_OFFSET={offset}')
    skipno,current, all = playwrighty.get_skip_from_offset(offset, cacheno)

    print(f'Skipping {skipno}')

  
    from extensions.trey.trey import skip_lines, speak
    skip_lines(skipno/3, cacheno)

    speak(f'Next {self.tofind} at {current} of {all}')

    return 0
  
  def _search_web(self, sequence=[]):  
    logger.info(f'> _Search Web {sequence}')
    print("> _Search Web called")
    #get audio input for query.  
    from extensions.trey.speech import listen_audio
    at = listen_audio(5, "query.wav")
    #at.join() #wait for it to finish.
    #have to just use some keys until this is done.  
    #need to return 1 to indicate we need more keys.
    #but this is only called once.  
    return 1

  def record_feedback_(self, sequence=[]):  
    if (len(sequence) == 1):

      logger.info(f'> Record Feedback_ {sequence}')

      print("> Record Feedback_ called")
      #get audio input for query.  
      duration = sequence[0]-self.keybot #in seconds
      duration *=3  #double duration for feedback
      from extensions.trey.speech import listen_audio
      self.now = datetime.now()
      self.feedbacknowstr = self.now.strftime("%Y%m%d_%H%M%S") #set nowstr for feedback.  
      self.helpdict['Record Feedback']['$$+'] = f"$DUR={duration}\n&Feedback\n"
      at = listen_audio(duration, "feedback.wav")
      #at.join() #wait for it to finish.
      #have to just use some keys until this is done.  
      #need to return 1 to indicate we need more keys.
      #but this is only called once.  

      return 0 #handled, this function will not be called again with further parameters.
    else:
      #get real-time input
      from extensions.trey.speech import transcribe_now
      self.func = "Record Feedback_"
      self.transcript += transcribe_now() + "\n"
      self.set_qr(self.func, {'transcript': self.transcript})
      #update display.  


    return 1

  def search_web_(self, sequence=[]):  

    logger.info(f'> Search Web_ {sequence}')
    #no function, just demo..
    if (len(sequence) == 0):
      #set engines..
      self.helpdict['Search Web']['$$+'] = ", ".join(playwrighty.get_engines())
    if (len(sequence) > 1 and sequence[-1] > self.keybot):
      self.speak(playwrighty.get_engine(sequence[-1]-self.keybot))


    return 1

  def record_feedback(self, sequence=[]):
    logger.info(f'> Record Feedback {sequence}')
    duration = sequence[0]-self.keybot if (len(sequence) > 0) else 5
    duration *=3  #triple duration for feedback
    print(f'> Record Feedback for {duration} seconds')
    from extensions.trey.speech import transcribe_audio, get_duration, transcribe_audio_whisper
    timer = datetime.now()
#    self.transcript = transcribe_audio("feedback.wav")
    self.transcript = transcribe_audio_whisper("feedback.wav") #try whisper for better accuracy.  This is slower but hopefully more accurate, especially for short feedback.


    dur = get_duration("feedback.wav") #actual dynamic duration..
    if (dur == 0):
      duration = (timer - self.now).total_seconds() if self.now is not None else duration
    else:
      duration = dur

    lag = (datetime.now() - timer).total_seconds()
    lag = int(lag)
    print(f'Transcription completed in {lag} seconds: {self.transcript}')
    #get current line and previous line in case we are on a partial..
    #then find the most likely location from text.  
    #if we are reading a page, get current line of that page..

    if (len(self.transcript) > 0):
      self.transcripthistory.append(self.transcript)
      #find the current link from our reading.  
      if (playwrighty.mybrowser is not None):
        tr = 0
        tr = playwrighty.update_page_offset()
#        tr -= (lag * 11) #assume 12 chars per second read. this is our timer.. 

        textduration = int(duration*3) #some extra lag here.  

        #too much lag to be accurate at the moment.  Maybe get better info with longer transcript..
        url = playwrighty.get_url(-1)      
        original = playwrighty.get_text(-1, tr, textduration+lag) 
        original = original.replace('\n','  ')
#        original = original.upper()
        #find best match location

        bestscore = 0
        # Get the score and the start/end indices of the match
        score = 0
        start = 0
        ostart = 0
        end = len(self.transcript)
        oend = duration*12
        #ScoreAlignment(score=27.77777777777778, src_start=0, src_end=24, dest_start=28, dest_end=40)
        ff = fuzz.partial_ratio_alignment(self.transcript, original)
        print(ff)
        print("$$FEEDBACK=" + self.transcript)
        print("$$ORIGINAL=" + original)        
        if (end < oend/3):
          print('!!Feedback shorter than expected')
          #too short.. not detected properly?  
          return -1
        #is this a match in our eyes.  Only want good data.  
        #play around with params here as model diverges / converges ..
        if (score in ff and ff.score > 25 and (ff.src_end - ff.src_start) > len(self.transcript)-4 and (ff.dest_end - ff.dest_start) / (ff.src_end - ff.src_start) > 0.7):
          ostart = ff.dest_start
          oend = ff.dest_end
          score = ff.score
          print(f'$$FOUND={original[ostart:oend]}')
          print(f'$$SCORE={score}')
          print(f'$$LAG={lag}')

          today = datetime.now().strftime("%Y%m%d")
          try:
            vars = {}
            vars['DURATION'] = duration
            vars['FEEDBACK'] = self.transcript
            vars['LANG'] = playwrighty.detect_language() if playwrighty.mybrowser is not None else "None"
            if (playwrighty.mybrowser is not None):
              #where is url?  
              print(f'$$URL={url}')
              vars['URL'] = url
              vars['TRANSCRIPT'] = original
              vars['LAG'] = lag
              vars['SCORE'] = score
              vars['START'] = ostart
              vars['END'] = oend
              vars['ORIGINAL'] = original[ostart:oend]
              fname = '../transcripts/' + self.name + '/' + self.feedbacknowstr + '.wav'
              vars['FILE'] = fname
            shutil.copy('feedback.wav', fname) #keep a copy for training..
            self.transcriber.write(self.name, "Record Feedback", vars, save=True)  
            self.set_qr("Record Feedback", vars) #update QR with feedback data for debugging and record keeping.
            #do we want to save to book as well?  for now yes, need reference info..
            self.transcriber.write_topic(self.name, "", f'$${self.feedbacknowstr}\n{self.transcript}', saveTranscript=False, saveBook=True)
          except Exception as e:
            print(f'Error writing feedback file: {e}')
        else:
          print('no good transcript match found')
          return -1 #error beep..
    else:
      print('no transcript detected')
      """
      possibles = original.split('  ')
      charlength = len(self.transcript)
      idx = 0
      startpos = 0
      endpos = 0
      currentstring = []
      while (idx < len(possibles)):
        if (endpos-startpos < charlength):
          currentstring.append(possibles[idx])
          endpos += len(possibles[idx]) + 1 #account for spaces
        else:
          if (startpos + len(possibles[idx]) >= charlength):
          
        idx += 1
      """      

    return 0


  def search_web(self, sequence=[]):
    logger.info(f'> Search Web {sequence}')
    query = "What is the capital of France?"
    from extensions.trey.speech import transcribe_audio, transcribe_audio_whisper
#    self.transcript = transcribe_audio("query.wav")
    self.transcript = transcribe_audio_whisper("query.wav") #try whisper for better accuracy.  This is slower but hopefully more accurate, especially for short queries.
    logger.info('$$AUDIO = ' + self.transcript)
    

    if (self.transcript != ""):
      query = self.transcript
      self.transcripthistory.append(self.transcript)
    engine = 0
    cacheno = -1
    print(sequence)

    #one param = engine
    if (len(sequence) > 0):
      engine = sequence[-1]-self.keybot
    #two = engine, cacheno
    if (len(sequence) > 1):
      engine = sequence[-1]-self.keybot
      cacheno = sequence[0]-self.keybot-1 

    
    from extensions.trey.trey import speak, pause_reader, resume_reader
    enginename = playwrighty.get_engine(engine) #set engine
    speak(f'Searching {enginename} for: {query}')

    body_text, link_data, page, cacheno = playwrighty.search_web(query, engine=engine, cacheno=cacheno)

#    print(body_text)
    self.links = link_data
    #should always have a value here..  
    total_read = playwrighty.get_bookmark(page.url, cacheno)
    print(f'Bookmark at {total_read}')
    q2, q3, stop_event = self.speak(body_text, link_data, playwrighty.page_cache[cacheno]['alt_text'], total_read, cacheno=cacheno)
    playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)
    logger.info(f'$$CACHENO={cacheno}')
    #self.transcript = "" #reset transcript.. cant do here..


    return 0

  def get_graphs(self, context, query):
    template = {
      "invoice_number": "verbatim-string",
      "invoice_date": "date",
      "total_amount": "number",
      "currency": "currency",
      "line_items": [
        {
          "description": "verbatim-string",
          "item_type": ["electronics", "clothing", "vehicle", "furniture", "other"],
          "quantity": "integer",
          "unit_price": "number",
          "total": "number"
        }
      ]
    }
    template = [
      {
      "name": "verbatim-string",
      "type": "string",
      "entities": [
        {
          "name": "verbatim-string",
          "type": "string",
          "relationships": [
            {
              "type": "string",
              "name": "verbatim-string"
            }
          ]
        }
      ]
    }
    ]
    examples = [
      {
        "name": "Social Graph",
        "type": "Social Graph",
        "entities": [
          {
            "name": "Paul",
            "type": "person",
            "relationships": [
              {
                "type": "friend",
                "name": "John"
              }, 
              {
                "type": "wife", 
                "name": "Mary"
              }, 
              { 
                "type": "colleague",
                "name": "Bob"
              }, 
              {
                "type": "organization",
                "name": "Google"
              }
            ]
          }, 
          {
            "name": "Google",
            "type": "organization",
            "relationships": [
              {
                "type": "parent", 
                "name": "Alphabet"
              }, 
              { 
                "type": "child",
                "name": "YouTube"
              }, 
              {
                "type": "child", 
                "name": "Nest Labs"
              },
              {
                "type": "competitor",
                "name": "Microsoft"
              }, 
              {
                "type": "customer",
                "name": "Apple"
              }
            ]

          }, 
          { 
            "name": "GitHub",
            "type": "organization",
            "relationships": [
              {
                "type": "parent", 
                "name": "Microsoft"
              }, 
              { 
                "type": "competitor",
                "name": "SourceForge"
              }
            ]

          }
        ]
      }, 
      {
        "type": "Time Graph", 
        "entities": [

        ]
      },
      {
        "type": "Site Graph", 
        "entities": [

        ]
      },
      {
        "type": "Knowledge Graph",
        "entities": [
        ]
      },
      {
        "type": "Dependency Graph",
        "entities": [
        ]
      }
      
    ]

    input_llm = "###INSTRUCTIONS###\nWe will extract the relevant information from the provided context and query, "
    input_llm += "and generate a relationship graph and respond with a structured and valid JSON output string based on the given template. "
    input_llm += "Names of relationship type can be generated or inferred.  \n"
    input_llm += "###JSON_SAMPLE###\n" + json.dumps(template, indent=4) + "\n"
    input_llm += "###RESPONSE_SAMPLE###\n" + json.dumps(examples, indent=4) + "\n"


    input_llm += "###INPUT_TEXT###\n"
    input_llm += f"::CONTEXT:: \n\n{context}\n\n::QUERY:: {query}"
    input_llm += "\n###JSON_OUTPUT###\n"
    answer = self.transcriber.ask_graph(context=input_llm, strictness=6) #allow for external knowledge, but not too much.  We want to extract from the context primarily.
    return answer

  def ddedup(self, t, all, stringmap, threshold = 80):
    from rapidfuzz import fuzz, process
    alt = ''
    match = process.extractOne(t, all, scorer=fuzz.ratio)
    if (not match or match[1] < threshold):
      stringmap[t] = {'cnt': 0, 'alt': ''}
      all.append(t)
    else:
      stringmap[ match[0]]['alt'] = t

  def dedup(self, mylist, isentities=False, threshold = 80):
    #deduplicate based on names..
    stringmap = {}
    all = []
    if (isentities):
      for e in mylist:
        t = e['text']
        self.ddedup(t, all, stringmap, threshold)

      logger.info(stringmap)
      for name, obj in stringmap.items():
        #replace all with alt.  
        alt = obj['alt']
        if (alt !=''):
          for e in mylist:
            if (e['text'] == alt):
              e['text'] = name
    else:
      for r in mylist:
        h = r['head']['text']
        t = r['tail']['text']
        self.ddedup(h, all, stringmap, threshold)
        self.ddedup(t, all, stringmap, threshold)

      logger.info(f'> Dedup')        
      logger.info(stringmap)
      for name, obj in stringmap.items():
        #replace all with alt.  
        alt = obj['alt']
        if (alt !=''):
          for r in mylist:
            if (r['head']['text'] == alt):
              r['head']['text'] = name
            if (r['tail']['text'] == alt):
              r['tail']['text'] = name

      
  def get_graphs2(self, context, loc, query, answer, vars, qr_queue=None, reader_queue=None):
    myloc = loc
    context = context[-4095:]  # only keep the last 8kb of context

    model_path = self.config['kg']['model_path']
    entity_labels = self.config['kg']['entity_labels']
    relation_labels = self.config['kg']['relation_labels']
    lag = time.time()
    if not hasattr(self, 'model') or self.model is None:
        logger.info(f'Loading GLiNER model from {model_path}')
        self.model = GLiNER.from_pretrained(model_path, local_files_only=True)
    model = self.model #keep for next call.  
    subcontexts = [context[i : i + 2048] for i in range(0, len(context), 2048)]
#    self.relations = [] #dont reset for now..just add..
#    self.entities = []
    allentities = []
    allrelations = []
    for (j, subcontext) in enumerate(subcontexts):
        # subcontext is already defined in the loop, no need to redefine it
        #find first space and last space
        first_space = subcontext.find(' ')
        last_space = subcontext.rfind(' ')
        entities, relations = model.inference(
            texts=[subcontext[first_space:last_space]],
            labels=entity_labels,
            relations=relation_labels,
            threshold=0.3,
            adjacency_threshold=0.4,
            relation_threshold=0.6, #too few relations at the moment..
            return_relations=True,
            flat_ner=False
        )
        logger.info(entities)
        logger.info(relations)
        for e in entities[0]:
          e['start'] -= len(context) + j*2048
          e['start'] += loc
        for r in relations[0]:
          r['head']['start'] -= len(context) + j*2048
          r['tail']['start'] -= len(context) + j*2048
          r['head']['start'] += loc
          r['tail']['start'] += loc
        allentities.extend(entities[0])
        allrelations.extend(relations[0])

    subanswers = [answer[i : i + 2048] for i in range(0, len(answer), 2048)]
    for (k, subanswer) in enumerate(subanswers):
        # subcontext is already defined in the loop, no need to redefine it
        #quick fix.. probably more logic needed to find better split points..
        first_space = subanswer.find(' ')
        last_space = subanswer.rfind(' ')
        entities, relations = model.inference(
            texts=[subanswer[first_space:last_space]],
            labels=entity_labels,
            relations=relation_labels,
            threshold=0.3,
            adjacency_threshold=0.4,
            relation_threshold=0.6, #too few relations at the moment..
            return_relations=True,
            flat_ner=False
        )
        logger.info(entities)
        logger.info(relations)
        for e in entities[0]:
          e['start'] = -1 #temporary entity..
        for r in relations[0]:
          r['head']['start'] = -1
          r['tail']['start'] = -1
        allentities.extend(entities[0])
        allrelations.extend(relations[0])


    #try to deduplicate..
    logger.info(f'$$NUMRELATIONS={len(allrelations)}') #measuring time for now..
    logger.info(f'$$NUMENTITIES={len(allentities)}')
    logger.info(f'> Dedup')
    self.dedup(allrelations)
    self.dedup(allentities, True)

    self.entities.extend(allentities)
    self.relations.extend(allrelations)
    self.dedup(self.relations)
    self.dedup(self.entities, True)

    #set qr info..
    vars["GRAPHS"] = json.dumps(allrelations)
    vars["ENTITIES"] = json.dumps(allentities)
    logger.info(f'$$NUMRELATIONS={len(allrelations)}') #measuring time for now..
    logger.info(f'{allrelations}')
    logger.info(f'$$NUMENTITIES={len(allentities)}')
    entity_counts = Counter(e['head']['text'] for e in allrelations if (len(e['head']['text']) > 3))
    #find central entity.  Create map of counts..
    max_key = max(entity_counts, key=entity_counts.get)
    vars["ENTITY"] = max_key


    if (qr_queue is not None):
      self.set_qr("graph", vars) #do again to load graph..
      qr = "<<" + self.name + ">>\n"
      qr += self.qr + "\n"
      qr_queue.put(qr)
      self.qr = ""

    logger.info(f'!!LAG {time.time() - lag}')
    self.synth.play_synth([53+12,55+12,52+12]) #play a sound to indicate graph is ready.
    return allentities, allrelations
    

  def generate_suggestions(self, query, suggest):
    #for now single replacement, but eventually could do combinations.  
    asuggest = []
    suggest.sort(key=lambda x: x[2], reverse=True)  # Sort by score in descending order
    for i, (word, qword, score, idx) in enumerate(suggest):
      orig = query
      query = query.replace(qword, word)
      asuggest.append((orig, query, idx))
    return asuggest




  def get_suggestions(self, context, query):
    immediate_context = context[-500:] if len(context) > 500 else context
    clean_text = re.sub(r"[^\w\s]", " ", immediate_context)  # Remove punctuation for better word matching
    clean_query = re.sub(r"[^\w\s]", " ", query)  # Remove punctuation for better word matching
    word_list = clean_text.split()
    word_list = [w.lower() for w in word_list if len(w) > 4]  # Convert to lowercase for case-insensitive comparison
    qwords = query.split()
    qwords = [w.lower() for w in qwords if len(w) > 4]  # Convert to lowercase for case-insensitive comparison
    #check for misspellings in query..
    similarity_matrix = cdist(word_list, qwords, scorer=fuzz.ratio, workers=-1)
    #any high similarity matches?  
    threshold = 80
    row_idx, col_idx = np.where(similarity_matrix >= threshold)  # example threshold
    suggest = []
    for r, c in zip(row_idx, col_idx):
      if (similarity_matrix[r, c] == 100):
        #ignore
        a = 0
      else:
        #should we replace qword with word_list word? 
        #query = query.replace(qwords[c], word_list[r])
        print(f"'{word_list[r]}' & '{qwords[c]}': {similarity_matrix[r, c]}")
        #get first index in query..
        query_index = query.find(qwords[c])
        suggest.append((word_list[r], qwords[c], similarity_matrix[r, c], query_index))

        
    if (len(suggest) > 0):
      suggest = self.generate_suggestions(query, suggest)
      return suggest

  def ask(self, sequence=[]):
    logger.info(f'> Ask {sequence}')
    query = "What are you doing?"
    from extensions.trey.speech import transcribe_audio, transcribe_audio_whisper
#    self.transcript = transcribe_audio("ask.wav")
    self.transcript = transcribe_audio_whisper("ask.wav") #try whisper for better accuracy.  This is slower but hopefully more accurate, especially for short queries.
    logger.info('$$AUDIO = ' + self.transcript)
    if (self.transcript != ""):
      query = self.transcript
      self.transcripthistory.append(self.transcript)


    cacheno = -1
    print(sequence)
    direction = -1 #default to review already read text..
    strictness = -1 #default to only use prior text..
    if (len(sequence) > 0):
      cacheno = sequence[0]-self.keybot - 1 #first key is cacheno..
    if (len(sequence) > 1):
      direction = 1 if sequence[-1]-self.keybot > 0 else -1
    if (len(sequence) > 2):
      strictness = sequence[1]-self.keybot
    if (cacheno < 0):
      cacheno = playwrighty.current_cache

    #for now just query ollama?  better if we have vectra or qdrantz..
    url = playwrighty.page_cache[cacheno]['page'].url
    title = playwrighty.page_cache[cacheno]['title']
    offset = playwrighty.page_cache[cacheno]['current_offset'][url]

    context_length = 100000 #for example..
    end_offset = offset
    start_offset = end_offset - context_length
    if (direction > 0):
      start_offset = end_offset
      end_offset = start_offset + context_length
    if (start_offset < 0):
      start_offset = 0
    if (end_offset > len(playwrighty.page_cache[cacheno]['body'])):
      end_offset = len(playwrighty.page_cache[cacheno]['body'])

    context, start_offset, end_offset = playwrighty.get_p_context(cacheno=cacheno, direction=direction, strictness=strictness)
    #pause before asking, maybe some silence, but probably better overall?  
    from extensions.trey.trey import pause_reader, resume_reader
    pause_reader()
    try:
      logger.info(f'$$QUERY={query}')
      synth.play_synth([53+12,55+12,52+12]) #
      answer = self.transcriber.ask_ollama(context=f"::CONTEXT:: \n\n{context}\n\n::QUERY:: {query}", model="gemma3:4b", strictness=strictness)
      logger.info(f'$$:={len(answer)}\n$$ANSWER={answer}')
      self.speak(f'{answer}', total_read=1)
      delay = len(answer) /14 #estimate 14 chars per second for just reading speed
      t = threading.Timer(delay, resume_reader)
      t.start()  # Start the timer in a new thread
      #too slow..
      vars = {"DIRECTION": direction, "URL": playwrighty.page_cache[cacheno]['page'].url, "(": start_offset, ")": end_offset, "QUERY": query}
      vars["ANSWER"] = answer
      vars["**"] = title
      vars[":"] = end_offset
      self.transcriber.write(self.name, "Ask", vars, save=True) #save for book..
      self.func = "ask"
      if (self.qr_queue is not None):
        self.set_qr(self.func, vars) #answer quickly before loading graph..
        qr = "<<" + self.name + ">>\n"
        qr += self.qr + "\n"
        self.qr_queue.put(qr)
        self.qr = ""


      graphs = ""
#      graphs = self.get_graphs(context, query)
      #start thread for this.  
      if (self.graph_thread is not None and self.graph_thread.is_alive()):
        logger.info('!!Graph thread still running, waiting for it to finish before starting a new one.')
        self.synth.play_synth([53+12,55+12,52+12]) #play a sound to indicate waiting for graph thread
        time.sleep(2)
#        self.graph_thread.join()  # Wait for the previous thread to finish
      self.graph_thread = threading.Thread(target=self.get_graphs2, args=(context, end_offset, query, answer, vars, self.qr_queue))
      self.graph_thread.start()
#      self.get_graphs2(context, query, vars) #ad to vars..
#      self.get_graphs2(context, end_offset, query,answer, vars)


      self.set_qr(self.func, vars) #do again to load graph..

      #for now just pause reader
    except Exception as e:
      logger.error(f'!!ask\n{e}')
      answer = "Sorry, I could not process your question."
      self.speak(answer)
      return -1

    return 0


  def find(self, sequence=[]):
    logger.info(f'> Find {sequence}')
    query = "What is the capital of France?"
    from extensions.trey.speech import transcribe_audio
    self.tofind = transcribe_audio("find.wav")
    logger.info('$$AUDIO = ' + self.tofind)
    

    if (self.tofind != ""):      
      query = self.tofind
      self.tofindhistory.append(self.tofind)

    cacheno = -1
    print(sequence)
    direction = 1
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot - 1
    if (len(sequence) > 1):
      direction = 1 if sequence[-2]-self.keybot > 0 else -1
    if (cacheno < 0):
      cacheno = playwrighty.current_cache
    
    from extensions.trey.trey import speak, pause_reader, skip_lines

#    pause_reader() #pause before starting to read new page.

    speak(f'Searching for: {query}')
#    print(body_text)
    #find in current page text.  
    offset = playwrighty.pfind(query, cacheno, direction=direction)
    #skip to this offset..
    print(f'Found at offset {offset}')
    logger.info(f'$$FOUND_OFFSET={offset}')
    if (offset < 0):
      speak(f'Could not find {query}')
      return 0
    skipno,current,all = playwrighty.get_skip_from_offset(offset, cacheno)
    logger.info(f'$$SKIPNO={skipno}')
    print(f'$$SKIPNO {skipno}')

    skip_lines(skipno/3, cacheno)
    speak(f'Found {query} at {current} of {all}')
    logger.info(f'$$FOUND={query}')

    return 0




  def _click_link(self, sequence=[]):
    logger.info(f'> _Click Link {sequence}')
    print("> _Click Link")
    self.func = "_Click Link"
    #display links on page.  
    #possibly handle here instead of end..
    total_read = 0
    total_read = playwrighty.update_page_offset()
    links = playwrighty.get_links(-1, total_read)
    #display links
    self.currentlinks = []
    for i, link in enumerate(reversed(links)): #start from most recent..
      self.currentlinks.append(link["text"])

    for i, link in enumerate(links):
      print(f'Link {i}: {link["text"]} ({link["href"]})')
    self.set_qr(self.func, {'links': self.currentlinks})
    #update display.  
    
    return 1



  def click_link_(self, sequence=[]):
    if (len(sequence) > 0) and sequence[-1] != self.keybot:

      logger.info(f'> Click Link_ {sequence}')
      print("> Click Link_")
        #find the current link from our reading.  
      testing = True
      if (playwrighty.mybrowser is not None and testing):
        total_read = 0
        total_read = playwrighty.update_page_offset()
        linkno = playwrighty.get_link_number(-1, total_read, -(sequence[-1]-self.keybot))
        links = playwrighty.page_cache[playwrighty.current_cache]['links']
        link = links[linkno]
        lenlinks = len(links)


        from extensions.trey.trey import pause_reader, resume_reader
        pause_reader() #pause first before clicking link.
        time.sleep(0.5) #wait for pause to take effect.  Need better way to ensure this.
        logger.info(f'--{link["text"]}')
        self.func = "Click Link_"
        #should make this more general.. send last ten links
        last15 = links[max(0, linkno-15):min(linkno+5, lenlinks)]
        last15.reverse() #reverse to match with Future:Past order in display.. [48 - 68]
        #does this match up with keys?  
        vars = {}
        for i, l in enumerate(last15):
          vars[f'{i}'] = l['text']
#          vars[f'href{i}'] = l['href']
        vars['idx'] = linkno

        self.set_qr(self.func, vars)
        self.speak(f'--{link["text"]}')
        resume_reader() #resume after speaking link number.

    return 1
  
  def click_link(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [53] #default to first link
    logger.info(f'> Click Link {sequence}')
    print('> Click Link {sequence}')

    #find the current link from our reading.  
    if (playwrighty.mybrowser is not None):
      total_read = 0
      total_read = playwrighty.update_page_offset()
      q3 = playwrighty.page_cache[playwrighty.current_cache]['sim_queue']
      siml = []
      while (q3 is not None and not q3.empty()):
        siml.insert(0,q3.get()) #get current similar offset.



      #Use simlink if we are using future links.  
      #should be the location of the simlink.  
#      if sequence[-1]-self.keybot > 0 and len(siml) > sequence[-1]-self.keybot-1:
#        total_read = siml[sequence[-1]-self.keybot-1]
      from extensions.trey.trey import pause_reader, resume_reader, stop_audio

#      pause_reader() #pause first before clicking link.
#      stop_audio() #stop audio to prevent overlap.  We will restart if we get a valid page back.
#      time.sleep(0.3) #wait for pause to take effect.  Need better way to ensure this.
      a = playwrighty.click_link(-1, total_read, -(sequence[-1]-self.keybot))
      if (isinstance(a, tuple)):
        body_text, link_data, page, cacheno = a
        self.links = link_data
        #print(body_text)
        print(f'Clicked link, got new page {page.url}')
        lang = playwrighty.detect_language(cacheno)
        total_read = playwrighty.get_bookmark(page.url, cacheno)
        alt_text = playwrighty.page_cache[cacheno]['alt_text']
        q2, q3, stop_event = self.speak(body_text, link_data, alt_text, total_read, lang, cacheno) #add offset to skip until where we were.)
        playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)
        resume_reader()
        return 0
      elif (isinstance(a, str)):
        #internal link..
        pause_reader()
        self.speak(f'{a}')
        time.sleep(min(len(a)/40, 4)) #wait for speaking to finish.  Need better way to ensure this.
        #dont block input too long..
        resume_reader()
        logger.info(f'Internal Link: {a}')
        return 0
      else:
        print(f'Clicked link, no new page returned {a}')
        link = None
        idx = sequence[-1]-7-self.keybot
        if (idx >= 0 and idx < len(self.links)):
          link = self.links[idx]
        q2, q3, stop_event = self.speak(f"Clicked link {idx} {link['text']} but nothing new to read.  Go back or restart search")
        return -1

  def go_back(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [53] #default to first link
    logger.info(f'> Go Back {sequence}')

    #find the current link from our reading.  
    if (playwrighty.mybrowser is not None):
      total_read = 0
      a = playwrighty.go_back(-sequence[-1]+self.keybot)
      if (isinstance(a, tuple)):
        body_text, link_data, page, cacheno = a

        self.links = link_data
#        print(body_text)
        page = playwrighty.page_cache[cacheno]['page']
        total_read = playwrighty.get_bookmark(page.url, cacheno)
        logger.info('$$Total_Read = ' + str(total_read))
        lang = playwrighty.detect_language(cacheno)
        alt_text = playwrighty.page_cache[cacheno]['alt_text']
        q2, q3, stop_event = self.speak(body_text, link_data, alt_text, total_read, lang, cacheno) #add offset to skip until where we were.  
        playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)
        return 0
      else:
        print(f'Clicked back, no new page returned {a}')
        logger.info('No valid page to go back to.')
        return -1

  def page(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [61] #default to page down
    logger.info(f'> Page {sequence}')
    from extensions.trey.trey import page, pause_reader, resume_reader
#    pause_reader() #this does not add bookmark..
    page(sequence[-1]-self.keybot)
    return 0
#    resume_reader()

  def pause_reader(self, sequence=[]):
    logger.info(f'> Pause Reader {sequence}')
    from extensions.trey.trey import pause_reader
    cacheno = -1
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot - 1
      logger.info(f'Selecting Tab with index {cacheno} of {len(playwrighty.page_cache)}')
      if (cacheno >= 0 and cacheno < len(playwrighty.page_cache)):
        from extensions.trey.trey import pause_reader, resume_reader, stop_audio

        pause_reader(cacheno)
      else:
        pause_reader(playwrighty.current_cache)
    else:
      pause_reader()
    self.add_bookmark(sequence) #pass cacheno if passed..
    return 0

  def resume_reader(self, sequence=[]):
    logger.info(f'> Resume Reader {sequence}')
    from extensions.trey.trey import resume_reader
    cacheno = -1
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot -1 #keybot..
      logger.info(f'Selecting Tab with index {cacheno} of {len(playwrighty.page_cache)}')
      if (cacheno >= 0 and cacheno < len(playwrighty.page_cache)):
        from extensions.trey.trey import pause_reader, resume_reader, stop_audio

        resume_reader(cacheno)
      else:
        resume_reader(playwrighty.current_cache)
    else:
      resume_reader() #resume all..
    return 0

  def skip_lines(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [54] #default to 3 lines
    cacheno = playwrighty.current_cache
    skipno = sequence[-1]
    if (skipno == _META): #skip start..
      skipno = -333
    elif (skipno == _META+12): #skip end
      skipno = 333
    elif (skipno == _VIDEO+12): #skip video..
      playwrighty.skip_ad(cacheno)
      return 0
    else:
      skipno = skipno-self.keybot
    logger.info(f'> Skip Lines {sequence}')
    from extensions.trey.trey import skip_lines
    skip_lines(skipno, cacheno)
    return 0

  def select_type(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [54] #default to content type
    logger.info(f'> Select Type {sequence}')
    from extensions.trey.trey import select_type
    select_type(sequence[-1]-self.keybot)


  def start_me(self, sequence=[]):
    #Pass parameter for which topic to start.  
    #for now just -N entries.  
    """Start MIDI input/output."""
    return 0
  
  def stop_me(self, sequence=[]):
    """Stop MIDI input/output."""
    logger.info(f'> Stop ME {sequence}')
    from extensions.trey.trey import stop_audio
    cacheno = -1
    if (len(sequence) > 0):
      self.add_bookmark(sequence)
      cacheno = sequence[-1]-self.keybot -1
      stop_event = playwrighty.get_stop_event(cacheno)
      if (stop_event is not None):
        stop_event.set()  # Signal the specific audio thread to stop
    else:
      self.add_bookmark()
      stop_audio() #stop all.  

    return 0


  def read_screen(self, sequence=[]):
    logger.info(f'> Read Screen {sequence}')
    if (len(sequence) > 0):
      if (sequence[-1] == self.mid+1): #read screen command
        #use PyQt to read screen.
        buffer = None
        if (self.qapp is None):
          logger.error('No QApplication instance provided, cannot read screen.')
          return 0
        else:
          screens = self.qapp.screens()
          for i, s in enumerate(screens):
              logger.info(f'Screen {i}: {s.name()} - Size: {s.size()}')
              logger.info('Capturing Screen')

              screenshot = s.grabWindow( 0 ) # 0 is the main window, you can specify another window id if needed
              screenshot.save('shot' + str(i) + '.jpg', 'jpg')
                  # Convert QImage to bytes
  #            buffer = BytesIO()
  #            screenshot.save(buffer, "PNG") # Or other suitable format like "BMP"
  #            buffer.seek(0)


        #call OCR function here.
        #use last screen for now.
        img = Image.open('shot' + str(i) + '.jpg')
  #      img = Image.open(buffer)
        lines, links = self.ocr_image(img)
        self.links = links
        print(f'OCR found {len(lines)} lines and {len(links)} links')
        #group by paragraph.
        par = ""
        all = ""
        for i in range(len(lines)):
          line = lines[i]['text']
          if (i > 0 and lines[i]['par_num'] == lines[i-1]['par_num']):
            par += "\n" + line
          else:
            if (par != ""):
              print("PAR: " + par)
              #do something with paragraph here.  
              all += par + "\n\n"
            par = line

        if (par != ""):
          print("PAR: " + par)
          all += par + "\n\n"

        self.speak(all)
          
        return 0
      elif (sequence[-1] == _META): #read screen command
        #reset the playwrighty last10 to the time, and recycle browser pages..
        #close browser and reopen..
        playwrighty.close_browser()
        time.sleep(2)
        #reset the last10 to current time..
        now = datetime.fromtimestamp(self.transcriber.timewindow.getTime())
        st = datetime.fromtimestamp(self.transcriber.timewindow.getStartTime())
        et = datetime.fromtimestamp(self.transcriber.timewindow.getEndTime())
        allcmds = self.transcriber.read(self.name, st, et) #default 7 days

        self.load_bookmarks2(allcmds)

        playwrighty.open_browser()
    
    else:
      #start the browser if any params passed for now..  
      playwrighty.open_browser()
      if (playwrighty.mybrowser is not None): #we have started a browser session with playwright.
        logger.info('Getting page from Playwright')
        try:
          text, links, alt_text_data = playwrighty.get_page_details(playwrighty.get_ppage(playwrighty.current_cache))
          text, links, page, cacheno = playwrighty.read_page('', playwrighty.current_cache) #read current page
          self.controlstate['app'] = 'chrome' #set app to chrome for now.  Should be more general.
          total_read = playwrighty.get_bookmark(page.url, cacheno)
          self.links = links
          print(f'Playwright found {len(text)} characters and {len(links)} links  on the page') 
          q2, q3, stop_event = self.speak(text, links, alt_text_data, total_read, cacheno=cacheno)
          playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)
          if page.locator("video").count() > 0: #prioritize video if present.. not sure if best..
            pause_reader() #pause before starting to read new page.
            playwrighty.play_video(cacheno)
        except Exception as e:
          logger.error(f'Error reading page with Playwright: {e}')
        return 0

  def text_only(self, text):
#    from markdown import Markdown
    # Configure parser to output plain text
#    md = Markdown(output_format="plain")

    # Convert text
#    text_only = md.convert(text)    
    text_only = text
    return text_only
  
  def speak(self, text, links=[], alt_text_data=[], total_read=0, lang="en", cacheno=-1):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    #really want to be able to turn on/off speaking with some setting similar to OPACITY..
    ttext = self.text_only(text)
    return speak(ttext, links, alt_text_data, total_read, lang, cacheno)

  
  def ocr_image(self, img):
    # Get detailed OCR data
    from languages.mousemovement1 import mousemovement1
    mm = mousemovement1(self.config)
    mm.startx = self.startx
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    # Loop through the detected words and print their positions
    n_boxes = len(data['text'])
    prevbox = {"x":0, "y":0, "w":0, "h":0}
    currentbox = {"x":0, "y":0, "w":0, "h":0, "text":"", "block_num":-1, "par_num":-1, "line_num":-1, "word_num":-1, "conf":-1}
    prevconf = 0
    currentline = ""
    alllines = []
    alllinks = [] #get all interactive words.  
    for i in range(n_boxes):
        if int(data['conf'][i]) > 60 or prevconf > 60:  # Filter by confidence
            prevconf = int(data['conf'][i])
            text = data['text'][i]

            #seems to come in order.  
            if (text.strip() == ""):
                continue

            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
#            print(f"Text: '{text}', Position: (x={x}, y={y}, w={w}, h={h}, block_num={data['block_num'][i]}, par_num={data['par_num'][i]}, line_num={data['line_num'][i]}, word_num={data['word_num'][i]}, conf={data['conf'][i]})")
#            print(currentbox)
            #check if this is clickable.  
            #move mouse to it and see if it changes.

            
            mm.mouse_move([x+10,y+5], True)
            time.sleep(0.05) #give it a moment to change
            cursor_type = mm.get_current_cursor_type()
            print(f'Cursor type at ({x+10},{y+5}) is {cursor_type}')
            if (cursor_type == win32con.IDC_HAND): #32512 is arrow, 32649
                alllinks.append({"text":text, "x":x, "y":y, "w":w, "h":h, "block_num":data['block_num'][i], "par_num":data['par_num'][i], "line_num":data['line_num'][i], "word_num":data['word_num'][i], "conf":data['conf'][i]})
                print(f"LINK: '{text}', Position: (x={x}, y={y}, w={w}, h={h}, block_num={data['block_num'][i]}, par_num={data['par_num'][i]}, line_num={data['line_num'][i]}, word_num={data['word_num'][i]}, conf={data['conf'][i]})")


            
            if (currentbox["line_num"] == data['line_num'][i] and currentbox["par_num"] == data['par_num'][i] and currentbox["block_num"] == data['block_num'][i]):
                #same line
                currentline += " " + text
                currentbox = {"x":min(prevbox["x"], x), "y":min(prevbox["y"], y), "w":0, "h":0,"text":"", "block_num":data['block_num'][i], "par_num":data['par_num'][i], "line_num":data['line_num'][i], "word_num":data['word_num'][i], "conf":data['conf'][i]}
                currentbox["w"] = max(prevbox["x"]+prevbox["w"], x+w) - currentbox["x"]
                currentbox["h"] = max(prevbox["y"]+prevbox["h"], y+h) - currentbox["y"]
            else:
                if (currentline != ""):
                    print("LINE: " + currentline)
                    print(f"Position: (x={currentbox['x']}, y={currentbox['y']}, w={currentbox['w']}, h={currentbox['h']})")
                    currentbox["text"] = currentline
                    alllines.append(currentbox)
                currentline = text
                currentbox = {"x":x, "y":y, "w":w, "h":h, "text":"", "block_num":data['block_num'][i], "par_num":data['par_num'][i], "line_num":data['line_num'][i], "word_num":data['word_num'][i], "conf":data['conf'][i]}


    if (currentline != ""):
        print("LINE: " + currentline)
        currentbox["text"] = currentline
        alllines.append(currentbox)
    return alllines, alllinks


  def select_window_(self, sequence=[]):
    self.func = "Select Window_"
    vars = {}
    select_index = self.currentwindowindex #always zero.. can only select up to 12 windows deep for now..
    if (len(sequence) > 0) and sequence[-1] != self.keybot:
      select_index = self.adjust_window_index(self.mid-sequence[-1])


    if (select_index > self.windowslen - 1):
      select_index = self.windowslen - 1
    if (select_index < 0):
      select_index = 0
    logger.info(f'> Select Window_ {sequence}')
    print("> Select Window_")
      #find the current link from our reading.
    
    last15 = self.windows[max(0, self.currentwindowindex-11):min(self.currentwindowindex+13, self.windowslen)]
    last15.reverse() #reverse to match with Future:Past order in display.. [48 - 68]
    vars['**'] = self.windows[select_index] #this should display..

    start = 0
    if self.windowslen < 12:
      start = 12 - self.windowslen + self.currentwindowindex + 1
      vars['idx'] = self.currentwindowindex
      vars[':'] = self.currentwindowindex
    else:
      vars['idx'] = self.currentwindowindex



    for i, l in enumerate(last15):
      n = i + start
      vars[f'{n}'] = l
#          vars[f'href{i}'] = l['href']
    self.set_qr(self.func, vars)
    #show title..

    self.set_qr(self.func, vars)
    return 1
  
  def select_window(self, sequence=[]):
    logger.info(f'> Select Window {sequence}')
    self.func = "Select Window"
    select_index = self.currentwindowindex #always zero.. can only select up to 12 windows deep for now..
    if (len(sequence) > 0):
      select_index = self.adjust_window_index(self.mid-sequence[-1])
    logger.info(f'Selecting Tab with index {select_index} of {self.windowslen}')

    vars = {'**': self.windows[select_index], ':': select_index}

    self.set_qr(self.func, vars)


    return 0
