import logging
import shutil
from pynput import *
import pytesseract
from PIL import Image
from io import BytesIO
import win32con
import time
from datetime import datetime, timedelta

import languages.helpers.transcriber as transcriber
import extensions.trey.playwrighty as playwrighty


logger = logging.getLogger(__name__)

class base:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.transcriber = None
    self.qapp = qapp
    self.func = None
    self.cmd = None
    self.qr = "" #info for QR message
    self.qrin = "" #info from incoming QR message
    self.startx = startx
    self.name = "base"
    #self.keybot = 49 #no keybot for dynamic and short/created languages...
    self.mid = 60 #middle C for bbox calc
    self.keybot = 61
    self.keyoffset = 0 #offset within octave
    self.octaveshift = 1 #number of octaves to shift up for dynamic keys
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.transcript = ""
    self.funcdict = {}
    self.suggestions = []

  def word(self, sequence=[]):
    """Word lookup."""
    
    cmd = ""
    sl = str(len(sequence))
    if (sl in self.config['languages'][self.name]):
      logger.info(f'Looking up sequence {sequence} in base')
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
  
  def load(self, transcriber=None):
    #load language specific data
     #config overrides load_data by default.  
    if (transcriber is not None):
      self.transcriber = transcriber
    if hasattr(self, 'load_data'):
      self.load_data()
    else:
      logger.info(f'!! <{self.__class__.__name__}> No Data')
      print(f'!! <{self.__class__.__name__}> No Data')  
    return 0


  
  def load_data(self):

    #load language specific data into the config.  
    default = {
       "1":
        {
          "Error": [64],
          "OK": [66],
          "Good": [67],
        },
       "2":
        {
          "Pause": [61,60],
          "Unpause": [61,62],
          "Screen Toggle": [61,63],
          "Screenshot": [61,64],
          "Comment": [65,69],
        },
        "3":
        {
          "Help": [61,73,62],
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
        "Error": "error",
        "OK": "ok",
        "Good": "good",
        "Pause": "pause",
        "Unpause": "unpause",
        "Screen Toggle": "screen_toggle",
        "Screenshot": "screenshot",
        "Comment": "comment",
        "Help": "help",

    }
    self.helpdict = {
      "Error": {
"> ": "error", 
"$$": "", 
"&&": "Error,Dislike,Negative,Past",},
      "OK": {
"> ": "ok", 
"$$": "", 
"&&": "OK,Like,Positive,Present"},
      "Good": {
"> ": "good", 
"$$": "", 
"&&": "Good,Like,Positive,Present"},
      "Pause": {
"> ": "pause", 
"$$": "", 
"&&": "Pause"},
      "Unpause": {
"> ": "unpause", 
"$$": "", 
"&&": "Unpause"},

      "Screen Toggle": {
"> ": "screen_toggle", 
"$$": "$opacity | $record",
"&&": "Screen Toggle (Overlay),Record"},
      "Screenshot": {
"> ": "screenshot", 
"$$": "$bbox4",
"&&": "Take screenshot with optional bbox."},

      "Comment": {
"> ": "0=$DUR=5 seconds\n1=$DUR*3 seconds", 
"$$": "$DUR (audio duration), &comment", 
"&&": "Add comment to current book."},
            "Help": {
"> ": "help", 
"$$": "", 
"&&": "Show video commands."}, 

    }

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

    #seq will always be 0 in base language, only words.
    logger.info("-> "+ cmd + " " + str(sequence))
    if cmd in self.funcdict:
      logger.info("--> "+ cmd + " " + str(sequence))
      func = self.funcdict[cmd]
      #all require keybot at end.

      #this function called every time a key is pressed.

      if hasattr(self, func):
        #if 1 key.. no keybot
        if (cmd in self.config['languages'][self.name]["1"]):
          return getattr(self, func)(sequence)
        elif (len(sequence) == 1 and sequence[-1] == self.keybot):
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
      self.commentnowstr = self.now.strftime("%Y%m%d%H%M%S") #set nowstr for feedback.  

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
      self.transcriber.write_topic(self.name, "", self.transcript, saveTranscript=False, saveBook=True)

    except Exception as e:
      print(f'Error writing comment file: {e}')

    return 0
    


  def help(self, sequence=[]):
    """Show all commands."""
    logger.info(f'> Help {sequence}')
    return 0

  def pause(self, sequence=[]):
    """Pause Video."""
    logger.info(f'> Pause {sequence}')
    self.set_qr("Pause", {'type': 'base'})
    return 0

  def unpause(self, sequence=[]):  
    """Unpause Video."""
    logger.info(f'> Unpause {sequence}')
    return 0


  def set_qr(self, func, param={}):
    """Set QR."""
    self.qr = "> " + func + "\n"
    for k,v in param.items():
        self.qr += f"$${k}={v}\n"
    self.qr += "$$\n"
    return 0  
  

  def screenshot(self, sequence=[]):
    """Take Screenshot."""
    #call video module to take screenshot
    return 0

     
  def error(self, sequence=[]):
    """Indicate Error."""
    logger.info(f'> Error {sequence}')
    return 0
  
  def ok(self, sequence=[]):
    """Indicate OK."""
    logger.info(f'> OK {sequence}')
    self.set_qr("OK", {"time": datetime.now().isoformat()})
    return 0
  
  def good(self, sequence=[]):
    """Indicate Good."""
    logger.info(f'> Good {sequence}')
    return 0
   

  def screen_toggle(self, sequence=[]):
    """Toggle Screen Overlay."""
    #call video module to toggle screen overlay
    return 0
  

  def speak(self, text, links=[]):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    return speak(text, links)

  
