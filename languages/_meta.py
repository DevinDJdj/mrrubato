import logging
from pynput import *
import time

import languages.helpers.transcriber as transcriber
import extensions.trey.playwrighty as playwrighty


logger = logging.getLogger(__name__)

class _meta:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.transcriber = transcriber.transcriber(self)
    self.qapp = qapp
    self.func = None
    self.qr = "" #info for QR message
    self.startx = startx
    self.name = "_meta"
    self.keybot = 48 #
    self.mid = 60 #middle C for bbox calc
    self.keyoffset = 0 #offset within octave mapping
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.audio_transcript = ""
    self.funcdict = {}
    self.suggestions = []
    self.alltopics = {}
    self.topicarray = []
    self.selectedtopic = None
    self.selectedtopicindex = None

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

    book = self.transcriber.read(self.name, None, None, './book/')
    #get num topics.  
    numtopics = 0
    self.alltopics = {}
    for c in book:
      if (c['type']=='**'):
        if (c['cmd'] not in self.alltopics):
          self.alltopics[c['cmd']] = []
        self.alltopics[c['cmd']].append(c)
        numtopics += 1

        self.topicarray.insert(0, c['cmd']) #time reverse order
    if (numtopics > 0):
      self.selectedtopicindex = 0      
      self.selectedtopic = self.topicarray[self.selectedtopicindex] #default to first topic.

    logger.info(f'Loaded {numtopics} topics and {len(book)} book transcripts from ./book/')

    return 0
  
  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
         "Pause": [48,49], #pause video
      },
      "3": {
        "Start": [48,60,61], #Start/resume recording
        "Help": [48,60,49], #show help
        "List Topics": [48,51,54], #list topics
        "Select Topic": [48,51,55], #select topic
        "Set Topic": [48,51,56], #set topic with voice command
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
      "Pause": "pause",
      "Start": "start",
      "Help": "help",
      "List Topics": "list_topics",
      "Select Topic": "select_topic",
      "Set Topic": "set_topic", #smart search of existing topics?  
      "_Set Topic": "_set_topic", #smart search of existing topics?  
    }
    self.helpdict = {
      "Start": {"help": "start", "params": "None", "desc": "Start/Resume video recording."},
      "Help": {"help": "help", "params": "None", "desc": "Show video commands."},
      "Pause": {"help": "pause", "params": "None", "desc": "Pause video playback."},
      "List Topics": {"help": "list topics", "params": "None", "desc": "List available topics."},
      "Select Topic": {"help": "select topic <index>", "params": "<index>", "desc": "Select topic by index from list."},
      "Set Topic": {"help": "set topic <name>", "params": "<name>", "desc": "Set topic by name."}
                       

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
  

  def start(self, sequence=[]):
    """Start Meta."""
    logger.info(f'> Start {sequence}')
    return 0
  
  def help(self, sequence=[]):
    """Show all commands."""
    logger.info(f'> Help {sequence}')
    return 0


  def list_topics(self, sequence=[]):
    logger.info(f'> List Topics {sequence}')
    #for now just demo..
    #list all topics from book transcripts.

    return 0

  def adjust_topic_index(self, idx):
    if idx+self.selectedtopicindex < 0:
      return 0
    elif (idx+self.selectedtopicindex) >= len(self.topicarray):
      return len(self.topicarray)-1
    else:
      return self.selectedtopicindex + idx
      
  def select_topic_(self, sequence=[]):
    if (len(sequence) > 0) and sequence[-1] != self.keybot:
      logger.info(f'> Select Topic_ {sequence}')
      print("> Select Topic_")
      newidx = self.adjust_topic_index(sequence[-1]-self.keymid)
      logger.info(f'--{self.topicarray[newidx]["text"]}')
      self.func = "Select Topic_"
      #should make this more general.. send last ten links
      last15 = self.topicarray[max(0, newidx-12):min(newidx+12, len(self.topicarray))]
      last15.reverse() #reverse to match with Future:Past order in display.. [48 - 68]
      #does this match up with keys?  
      vars = {}
      for i, l in enumerate(last15):
        vars[f'{i}'] = l
#          vars[f'href{i}'] = l['href']
      vars['idx'] = newidx
      self.set_qr(self.func, vars)
    #scroll up or back?  
    #list most likely topics based on recency and relevance to current topic.

  def select_topic(self, sequence=[]):
    selected = 0
    if (len(sequence) > 0):
      selected = sequence[-1]-self.keymid

    self.selectedtopicindex = self.adjust_topic_index(selected)
    self.selectedtopic = self.topicarray[self.selectedtopicindex] if self.selectedtopicindex < len(self.topicarray) else None
    logger.info(f'> Select Topic {sequence}')
    #get bookmark at index selected
    self.func = "Select Topic"
    self.set_qr(self.func, {'topic': self.selectedtopic})
    self.speak(f'Selected topic {self.selectedtopic}')
    return 0

  def set_topic(self, sequence=[]):
    logger.info(f'> Set Topic {sequence}')
    topic = "Australian Open 2026"
    from extensions.trey.speech import transcribe_audio
    self.transcript = transcribe_audio("topic.wav")

    logger.info('$$AUDIO = ' + self.transcript)
    if (self.transcript != ""):
      topic = self.transcript
    from extensions.trey.trey import speak
    speak(f'Setting topic: {topic}')

    return 0


  def _set_topic(self, sequence=[]):  
    logger.info(f'> _Set Topic {sequence}')
    print("> _Set Topic called")
    #get audio input for query.  
    from extensions.trey.speech import listen_audio
    at = listen_audio(5, "topic.wav")
    #but this is only called once.  
    return 1

  def pause(self, sequence=[]):
    """Pause Video."""
    logger.info(f'> Pause {sequence}')
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

  
