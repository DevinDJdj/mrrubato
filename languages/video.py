import logging
from pynput import *
import pytesseract
from PIL import Image
from io import BytesIO
import win32con
import time

logger = logging.getLogger(__name__)

class video:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.qapp = qapp
    self.startx = startx
    self.name = "video"
    self.keybot = 49 #
    self.keyoffset = 1 #offset within octave mapping
    self.links = []
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.audio_transcript = ""
    self.funcdict = {}

  def word(self, sequence=[]):
    """Word lookup."""
    
    cmd = ""
    sl = str(len(sequence))
    if (sl in self.config['languages'][self.name]):
      logger.info(f'Looking up sequence {sequence} in video')
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
      "2": {
      },
      "3": {
        "Start": [49,60,61], #Start recording
        "Stop": [49,61,60], #stop recording
        "Help": [49,50,51], 
        "Pause": [49,50,52], #pause video
        "Unpause": [49,50,53], #unpause video
        "Comment": [49,56, 57], #record comment
        "Screenshot": [49,52,55], #take screenshot
        "Zoomshot": [49,52,56], #take zoomed screenshot
      }
    }
    if (self.name in self.config['languages']):
      logger.info(f'Merging existing {self.name} config')
      #need logic to iterate and pick each one.  This is not working right.  
      default.update(self.config['languages'][self.name])
    else:
      logger.info(f'No existing {self.name} config found, creating new one')

    self.config['languages'][self.name] = default
    self.funcdict = {
      "Stop": "stop",
      "Comment": "comment",
      "Start": "start",
      "Help": "help",
      "Pause": "pause",
      "Unpause": "unpause",
      "Screenshot": "screenshot",
      "Zoomshot": "zoomshot",

    }

    return 0  

  #act differently based on words in sequence.    
  def act(self, cmd, words=[], sequence=[]):
    """ACT based on command and sequence."""
    if (len(sequence) == 0 and "_" + cmd in self.funcdict):
      #run prefix command
      func = self.funcdict["_" + cmd]
      if hasattr(self, func):
        return getattr(self, func)(sequence)
      
    elif cmd in self.funcdict:
      func = self.funcdict[cmd]
      #all require keybot at end.

      #this function called every time a key is pressed.
      if hasattr(self, func + "_"):
        return getattr(self, func + "_")(sequence)
      
      if hasattr(self, func):
        if (len(sequence) == 1 and sequence[0] == self.keybot):
          return getattr(self, func)(sequence[:-1])
        elif (len(sequence) > 1 and sequence[-2:] == [self.keybot, self.keybot]):
          return getattr(self, func)(sequence[:-2])
        else:
          return 1 #need more keys.
      else:
        logger.error(f"Function {func} not found in {self.__class__.__name__}")
    else:
      print(f"Command {cmd} not found in function maps")
    return -1
  

  def comment(self, sequence=[]):
    #start recording on 0, but return 1
    from extensions.trey.speech import transcribe_audio, listen_audio

    logger.info(f'> Comment {sequence}')
    #stop recording.  for now just using fixed 10 seconds.  
    #needs to be async to do this properly.
    listen_audio(10, "comment.wav")
    text = transcribe_audio("comment.wav")

    return 0
    


  def start(self, sequence=[]):
    """Start Recording."""
    logger.info(f'> Start {sequence}')
    return 0
  
  def stop(self, sequence=[]):
    """Stop Recording."""
    logger.info("> Stop {sequence}")
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

  def screenshot(self, sequence=[]):
    """Take Screenshot."""
    logger.info(f'> Screenshot {sequence}') 
    return 0
  
  def zoomshot(self, sequence=[]):
    """Take Zoomed Screenshot."""
    logger.info(f'> Zoomshot {sequence}')
    return 0

  def speak(self, text, links=[]):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    return speak(text, links)

  
