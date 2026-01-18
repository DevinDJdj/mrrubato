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
    self.transcriber = transcriber.transcriber(self)
    self.qapp = qapp
    self.func = None
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
        "Set Language": [59,60], #Set language
      }, 
        "3": {
            "Help": [59,71,60], #show help
            "New Language": [59,61,62], #Create language definition..
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

    }
    self.helpdict = {
      "Help": {"help": "help", "params": "None", "desc": "Show video commands."},
        "Set Language": {"help": "set_language", "params": "None", "desc": "Set current language."},
        "New Language": {"help": "new_language", "params": "None", "desc": "Create new language definition."},

    }

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

  
