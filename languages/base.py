import logging
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
    self.transcriber = transcriber.transcriber(self)
    self.qapp = qapp
    self.func = None
    self.qr = "" #info for QR message
    self.qrin = "" #info from incoming QR message
    self.startx = startx
    self.name = "base"
    #self.keybot = 49 #no keybot for dynamic and short languages...
    self.mid = 60 #middle C for bbox calc
    self.keyoffset = 12 #offset within octave mapping anything above 12 is dynamic for now
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
       "Error": {"help": "error", "params": "None", "desc": "Indicate error."},
         "OK": {"help": "ok", "params": "None", "desc": "Indicate OK."},
            "Good": {"help": "good", "params": "None", "desc": "Indicate good."},
         "Pause": {"help": "pause", "params": "None", "desc": "Pause video playback."},
            "Unpause": {"help": "unpause", "params": "None", "desc": "Unpause video playback."},
            "Screen Toggle": {"help": "screen toggle", "params": "[opacity]", "desc": "Toggle screen overlay with optional opacity (0-100)."},
            "Screenshot": {"help": "screenshot [bbox]", "params": "[bbox]", "desc": "Take screenshot with optional bbox."},
            "Comment": {"help": "comment", "params": "None", "desc": "Record audio comment."},
            "Help": {"help": "help", "params": "None", "desc": "Show video commands."}, 

    }

    return 0  

  #act differently based on words in sequence.    
  def act(self, cmd, words=[], sequence=[]):
    """ACT based on command and sequence."""
    #seq will always be 0 in base language, only words.
    logger.info("-> "+ cmd + " " + str(sequence))
    if cmd in self.funcdict:
      logger.info("--> "+ cmd + " " + str(sequence))
      func = self.funcdict[cmd]
      #all require keybot at end.

      #this function called every time a key is pressed.

      if hasattr(self, func):
          return getattr(self, func)(sequence[:-1])
      else:
        logger.error(f"Function {func} not found in {self.__class__.__name__}")



      
    else:
      print(f"{self.funcdict}")
      logger.info(f"{self.funcdict}")
      logger.error(f"Command {cmd} not found in function maps")
      print(f"Command {cmd} not found in function maps")
    return -1
  

  def comment(self, sequence=[]):
    #start recording on 0, but return 1
    from extensions.trey.speech import transcribe_audio, listen_audio

    logger.info(f'> Comment {sequence}')
    #stop recording.  for now just using fixed 10 seconds.  
    #needs to be async to do this properly.
    listen_audio(10, "comment.wav")
    #not implemented yet..

    return 0
    


  def help(self, sequence=[]):
    """Show all commands."""
    logger.info(f'> Help {sequence}')
    return 0

  def pause(self, sequence=[]):
    """Pause Video."""
    logger.info(f'> Pause {sequence}')
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

  
