import logging
from pynput import *
import time

import languages.helpers.transcriber as transcriber
import extensions.trey.playwrighty as playwrighty


logger = logging.getLogger(__name__)

class _lang:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.transcriber = None
    self.qapp = qapp
    self.func = None
    self.cmd = None
    self.qr = "" #info for QR message
    self.startx = startx
    self.name = "_lang"
    self._langseq = [61,62] #default language key sequence "base"
    self.keybot = 59 #
    self.mid = 60 #middle C for bbox calc
    self.keyoffset = 11 #offset within octave mapping
    self.maxseq = 16 #includes parameters
    self.callback = None
    self.audio_transcript = ""
    self.funcdict = {}
    self.suggestions = []
    self.alltopics = {}
    self.topicarray = []
    self.wordmap = {} #sequence -> sequence mapping for new words or created words.  
    self.spokenwords = [] #list of words spoken, can use for context in new word creation.
    self.mywords = [] #list of words executed, can use for context in new word creation.
    self.selectedtopic = None

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
      "2": {
        "Set Language": [59,60], #Set language
      }, 
        "3": {
            "Help": [59,71,60], #show help
            "New Language": [59,61,62], #Create language definition..
            "New Word": [59,61,63], #Create new word definition..
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
      "Help": "help",
      "Set Language": "set_language",
      "New Language": "new_language",
      "New Word": "new_word",

    }
    self.helpdict = {
      "Help": {"help": "help", "params": "None", "desc": "Show video commands."},
        "Set Language": {"help": "set_language", "params": "None", "desc": "Set current language."},
        "New Language": {"help": "new_language", "params": "None", "desc": "Create new language definition."},
        "New Word": {"help": "new_word", "params": "None", "desc": "Create new word definition."},

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
    
  def help(self, sequence=[]):
    """Show all commands."""
    logger.info(f'> Help {sequence}')
    return 0



  def set_language(self, sequence=[]):
    if (len(sequence) == 0):
      sequence = self._langseq
    #find language from sequence
    logger.info(f'> Set Language {sequence}')

    #find in config.  
    lang = None
    for langname, langseq in self.config['languages'].items():
      if (langseq == sequence):
        lang = langname
        break
    if (lang is None):
        self.speak('Language not found')
        return -1
    self.func = "Set Language"
    self.set_qr(self.func, {'LANG': lang})
    self.speak(f'Set language {lang}')
    #shift octave.  
    #dynamically load language module here.

    self._langseq = sequence
    return 0
  
  
  def new_language(self, sequence=[]):
    """Create new language definition."""
    logger.info(f'> New Language {sequence}')
    self.func = "New Language"
    self.speak('Creating new language definition not yet implemented')
    return 0

  def text2seq(self, text):
    #convert text to sequence.  
    seq = []
    seq.append(110) #start text
      
    for c in text:
      n = ord(c)
      if (n >= 0 and n <= 255):
        c1 = n // 16
        c2 = n % 16
        note1 = 112 + c1
        note2 = 112 + c2
        seq.append(note1)
        seq.append(note2)
        print(f'Encoded char {c} to notes [{note1},{note2}]')
      else:
        print(f'Error: character {c} out of range')
        logger.error(f'Error: character {c} out of range')

    seq.append(111) #end text    
    return seq

  def new_word(self, sequence=[]):
    """Create new word definition."""
    numwords = 1
    if (len(sequence) == 1):
      #find last word used along with sequence.  
      #param for number of words to use for shortcut sequence..
      #pull from mykeys.. words[-i:]
      numwords = sequence[0] - self.keybot #number of words to use for new word sequence.
      if numwords <= 0:
        numwords = 1
      self.mywords = self.spokenwords[-numwords:] if len(self.spokenwords) >= numwords else self.spokenwords

    if (len(sequence) > 1):
      if (sequence[-1] == self.keybot and sequence[-2] == self.keybot ):
        definition = sequence[1:-2] #remove command, keybot sequence, and keybot at end.
      elif (sequence[-1] == self.keybot):
        definition = sequence[1:-1] #remove command and keybot at end.
      else:
        definition = sequence[1:] #remove command and keybot sequence.
        #show if already have a word..
        totalseq = []
        if (self.wordmap.get(tuple(definition)) is not None):
          #self.speak('Word already exists for this sequence')
          logger.info(f'Existing word sequence: {self.wordmap[tuple(definition)]["&&"]}, seq: {self.wordmap[tuple(definition)]["seq"]}')
          logger.info(f'Delete first or choose different sequence for new word.')
          return -1
        else:

          for i in range(len(self.mywords)):
            totalseq.extend(self.mywords[i]['sequence'])
            totalseq.extend(self.mywords[i]['ss']) #add params.  
            #add text to ss
            if 'transcript' in self.mywords[i]:
              totalseq.extend(self.text2seq(self.mywords[i]['transcript']))
          self.wordmap[tuple(definition)] = {'&&': definition, 'seq': totalseq} #add to wordmap for lookup.  can add more info here later like params or transcript.
          logger.info(f'Created new word with sequence {definition}')
#          self.speak(f'Created new word with sequence {definition}')
          return 0


      #need to parse definition into sequence and params.  for now, just use as text

    #identify if already assigned..
    #Use default params.. add dynamically to function dict?  
    logger.info(f'> New Word {sequence}')
    self.func = "New Word"
#    self.speak('Creating new word definition not yet implemented')
    
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

  
