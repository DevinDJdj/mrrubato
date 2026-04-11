import logging
from pynput import *
import pytesseract
from PIL import Image
from io import BytesIO
import win32con
import time
from datetime import datetime, timedelta
import shutil

import languages.helpers.transcriber as transcriber
import extensions.trey.playwrighty as playwrighty


logger = logging.getLogger(__name__)

class check:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.transcriber = transcriber.transcriber(self)
    self.qapp = qapp
    self.func = None
    self.cmd = None
    self.qr = "" #info for QR message
    self.qrin = "" #info from incoming QR message
    self.startx = startx
    self._bbox = [0,0,0,0] #for now just use this for all functions that need a bbox.  This is left, top, right, bottom.  We can also use this for screen toggle to indicate where the screen overlay should be.
    self.bbox = [100,200,100,200]   
    self.bbox_aftertouch = [400,500,400,500] #just start here, or from last bbox.  Load from settings..
    self.geo = None
    self.name = "check"
    self.keybot = 57 #
    self.mid = 60 #middle C for bbox calc
    self.keyoffset = 9 #offset within octave mapping
    self.links = []
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.transcript = ""
    self.feedbacknowstr = ""
    self.funcdict = {}
    self.suggestions = []
    self.transcripthistory = [] #store past transcripts for context.  This is not currently used for anything but could be used for context in future functions.

  def word(self, sequence=[]):
    """Word lookup."""
    
    cmd = ""
    sl = str(len(sequence))
    if (sl in self.config['languages'][self.name]):
      logger.info(f'Looking up sequence {sequence} in <<check>>')
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
    return 0
  
  def load(self):
    #load language specific data
     #config overrides load_data by default.  
    if hasattr(self, 'load_data'):
      self.load_data()
    else:
      logger.info(f'!! <{self.__class__.__name__}> No Data')
      print(f'!! <{self.__class__.__name__}> No Data')  
    return 0


  def load_transcript(self):
    #load commands from config into funcdict
    allcmds = self.transcriber.read(self.name, None, None) #default 7 days
    logger.info(f'Loaded {len(allcmds)} command transcripts for {self.name}')

    return 0
  
  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
         "Pause": [57,56], #pause check
         "Unpause": [57,58], #unpause check
      },
      "3": {
        "Help": [57,69,58], #show help for check commands
        "Comment": [57,61, 64], #record comment
      },
    }
    if (self.name in self.config['languages']):
      logger.info(f'Merging existing {self.name} config')
      #need logic to iterate and pick each one.  This is not working right.  
      default.update(self.config['languages'][self.name])
    else:
      logger.info(f'No existing {self.name} config found, creating new one')

    self.config['languages'][self.name] = default
    self.funcdict = {
      "Comment": "comment",
      "Help": "help",
      "Pause": "pause",
      "Unpause": "unpause",

    }
    self.helpdict = {
      "Comment": {"help": "comment", "params": "None", "desc": f"Add comment to {self.name} timeline."},
      "Help": {"help": "help", "params": "None", "desc": f"Show {self.name} commands."},
      "Pause": {"help": "pause", "params": "None", "desc": f"Pause {self.name} playback."},
      "Unpause": {"help": "unpause", "params": "None", "desc": f"Unpause {self.name} playback."},

    }

    self.load_transcript()
    return 0  

  #act differently based on words in sequence.    
  def act(self, cmd, words=[], sequence=[], doact=True):
    """ACT based on command and sequence."""
    if (not doact):
      if (len(sequence) == 1 and sequence[-1] == self.keybot):
        return 0
      elif (len(sequence) > 1 and sequence[-2:] == [self.keybot, self.keybot]):
        return 0
      else:
        return 1 #need more keys.

    logger.info("-> "+ cmd + " " + str(sequence))
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
          #no function, run sequence through mk.key
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
  

  def comment_(self, sequence=[]):
    if (len(sequence) == 1):

      logger.info(f'> Comment_ {sequence}')

      print("> Comment_ called")
      #get audio input for query.  
      duration = sequence[0]-self.keybot #in seconds
      duration *=3  #double duration for feedback
      from extensions.trey.speech import listen_audio
      self.now = datetime.now()
      self.feedbacknowstr = self.now.strftime("%Y%m%d%H%M%S") #set nowstr for feedback.  

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
    logger.info(f'> Comment {sequence}')
    duration = sequence[0]-self.keybot if (len(sequence) > 0) else 5
    duration *=3  #triple duration for feedback
    print(f'> Comment for {duration} seconds')
    from extensions.trey.speech import transcribe_audio, get_duration, transcribe_audio_whisper, transcript_info
    timer = datetime.now()
#    self.transcript = transcribe_audio("feedback.wav")
    self.transcript = transcribe_audio_whisper("comment.wav") #try whisper for better accuracy.  This is slower but hopefully more accurate, especially for short feedback.


    dur = get_duration("comment.wav") #actual dynamic duration..
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
      try:
        vars = {}
        vars['DURATION'] = duration
        vars['TRANSCRIPT'] = self.transcript
        vars['LANG'] = transcript_info['language'] if transcript_info is not None and 'language' in transcript_info else "unknown"
        if (playwrighty.mybrowser is not None):
            fname = '../transcripts/' + self.name + '/' + self.feedbacknowstr + '.wav'
            vars['FILE'] = fname
        shutil.copy('comment.wav', fname) #keep a copy for training..
        self.transcriber.write(self.name, "Comment", vars)  
        self.set_qr("Comment", vars) #update QR with feedback data for debugging and record keeping.

      except Exception as e:
        print(f'Error writing feedback file: {e}')
    return 0
    


  def help(self, sequence=[]):
    """Show all commands."""
    logger.info(f'> Help {sequence}')
    return 0



  def pause(self, sequence=[]):
    """Pause Check."""
    logger.info(f'> Pause {sequence}')
    cacheno = -1
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot #first key cache selection
    #pause trey.  
    self.set_qr("Pause", {'type': 'check', 'cacheno': cacheno})
    return 0

  def unpause(self, sequence=[]):  
    """Unpause Check."""
    logger.info(f'> Unpause {sequence}')
    cacheno = -1
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot #first key cache selection

    self.set_qr("Unpause", {'type': 'check', 'cacheno': cacheno})

    
    return 0


  def ar2str(self, arr):
    """Array to String."""
    string_elements = [str(x) for x in arr]
    single_string = ", ".join(string_elements)

    return single_string

  def qr_in(self, data):
    #handle incoming QR data for now just MPE aftertouch. 
    #used for internal comms as well.. should change queue for that..
    return 0



  def set_qr(self, func, param={}):
    """Set QR."""
    self.qr = "> " + func + "\n"
    for k,v in param.items():
        self.qr += f"$${k}={v}\n"
    self.qr += "$$\n"
    return 0  
  

  def speak(self, text, links=[]):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    return speak(text, links)

  
