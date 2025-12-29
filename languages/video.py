import logging
from pynput import *
import pytesseract
from PIL import Image
from io import BytesIO
import win32con
import time

import languages.helpers.transcriber as transcriber

logger = logging.getLogger(__name__)

class video:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.transcriber = transcriber.transcriber(self)
    self.qapp = qapp
    self.func = None
    self.qr = "" #info for QR message
    self.startx = startx
    self.bbox = [0,0,100,100]   
    self.opacity = 0.4
    self.geo = None
    self.name = "video"
    self.keybot = 49 #
    self.mid = 60 #middle C for bbox calc
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


  def load_transcript(self):
    #load commands from config into funcdict
    allcmds = self.transcriber.read(self.name, None, None) #default 7 days
    logger.info(f'Loaded {len(allcmds)} command transcripts for {self.name}')

    return 0
  
  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
         "Pause": [49,48], #pause video
         "Unpause": [49,50], #unpause video
         "Screen Toggle": [49,51], #show/hide screen overlay, param set opacity..
      },
      "3": {
        "Start": [49,61,62], #Start/resume recording
        "Stop": [49,61,60], #stop/pause recording
        "Help": [49,61,50], 
        "Comment": [49,53, 56], #record comment
        "Screenshot": [49,53,55], #take screenshot
        "Zoomshot": [49,53,57], #take zoomed screenshot
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
      "Screen Toggle": "screen_toggle",

    }
    self.load_transcript()
    return 0  

  #act differently based on words in sequence.    
  def act(self, cmd, words=[], sequence=[]):
    """ACT based on command and sequence."""
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

  def get_XY(self, key, idx=0):
    """Get X,Y from key."""
    #map key to screen position
    #for now just return center of screen
    offset = key - self.mid #for now hardcoded mid.  
    if (self.geo is not None):
        if (idx < 2):
            return self.geo.x() + self.geo.width() * (offset+12) // 24
        else:
            return self.geo.y() + self.geo.height() * (offset+12) // 24
    
  def contain_bbox(self, bbox):
    """Contain BBOX within screen."""
    if (self.geo is not None):
        if (bbox[0] < self.geo.x()):
            bbox[0] = self.geo.x()
        if (bbox[1] > self.geo.x()+self.geo.width()):
            bbox[1] = self.geo.x()+self.geo.width()
        if (bbox[2] < self.geo.y()):
            bbox[2] = self.geo.y()
        if (bbox[3] > self.geo.y()+self.geo.height()):
            bbox[3] = self.geo.y()+self.geo.height()
    return bbox

  
  def get_bbox(self, sequence=[]):
    """Get BBOX from sequence."""
    #get BBOX
    bbox = []
    if (len(sequence) > 3):
        for i in range(4):  
            bbox.append(self.get_XY(sequence[i], i))
    elif (len(sequence) > 1):
        tempb = self.bbox #use previous bbox to calc offset
        for i in range(2):  
            bbox.append(self.get_XY(sequence[i], i*2))
            if (i==0):
                offset = tempb[1]-tempb[0]
            else:
                offset = tempb[3]-tempb[2]
            bbox.append(bbox[-1]+offset)
    else:
        #think xxyy is a more natural pattern for this..
        bbox.append(self.geo.x())
        bbox.append(self.geo.x()+self.geo.width())
        bbox.append(self.geo.y())
        bbox.append(self.geo.y()+self.geo.height())
    
    if (len(sequence) > 4):
        logger.info(f'Using custom bbox {bbox} from {sequence}')
        #override with more precise bbox
        adjust = 10
        for i in range(4, len(sequence)):
            """down left, up right, left down, right up""" #ok
            """left up, right down""" #ok
            """up left, down right""" #ng
            """[60,60,61,61]""" #up
            """[59,59,60,60]""" #left
            """[61,61,60,60]""" #right


            #i.e. move left, down = 59 decrease x1, 59 = decrease x2, 61 = increase y1, 61 = increase y2
            #squeeze towards mid, 61 = increase x1, 59 = decrease x2, 59 = decrease y1, 61 = increase y2
            #4n+2, 4n+3 = y adjustments reversed
            if (i // 4 == 2 or i // 4 == 3):
                adjust = -10
            bbox[i%4] += (self.mid-sequence[i])*adjust

        #check bounds.  
        bbox = self.contain_bbox(bbox)


    return bbox

  def ar2str(self, arr):
    """Array to String."""
    string_elements = [str(x) for x in arr]
    single_string = ", ".join(string_elements)

    return single_string

  def set_qr(self, func, param={}):
    """Set QR."""
    self.qr = "> " + func + "\n"
    for k,v in param.items():
        self.qr += f"$${k}={v}\n"
    self.qr += "$$\n"
    return 0  
  
  def screenshot_(self, sequence=[]):  
    if (len(sequence) >= 4):
      #calc new BBOX from sequence and display
      self.bbox = self.get_bbox(sequence)
      logger.info(f'> Screenshot_ {sequence}')
      logger.info(f'$$BBOX={self.bbox}')
      #show bbox on screen for user to see
      return 0

  def screenshot(self, sequence=[]):
    """Take Screenshot."""
    #always in groups of 4 for bbox
    #no need, this should be done..
    self.func = "Screenshot"
    self.bbox = self.get_bbox(sequence)
    logger.info(f'> Screenshot {sequence}') 
    logger.info(f'$$BBOX={self.bbox}')

    #qr specific to current action.
    self.set_qr(self.func, {'BB': self.ar2str(self.bbox), 'SEQ': self.ar2str(sequence)})
    #possibly return other data here for other functions.  
#    self.draw_screen_box(self.bbox)
    return 0

  def _screenshot(self, sequence=[]):
    """Take Screenshot."""
    logger.info(f'> _Screenshot {sequence}')
    #show bbox on screen for user to see?
    return 0

  def screen_toggle(self, sequence=[]):
    """Toggle Screen Overlay."""
    self.func = "Screen Toggle"
    logger.info(f'> Screen Toggle {sequence}')
    opacity = self.opacity
    if (len(sequence) >=1):
        opacity = (sequence[0]-self.keybot)*10
        if (opacity < 0):
            opacity = 0
        elif (opacity > 100):
            opacity = 100
        opacity = opacity / 100.0
        self.opacity = opacity
    self.set_qr(self.func, {'OPACITY': opacity})
    return 0
  
  def zoomshot(self, sequence=[]):
    """Take Zoomed Screenshot."""
    logger.info(f'> Zoomshot {sequence}')
    return 0

  def speak(self, text, links=[]):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    return speak(text, links)

  
