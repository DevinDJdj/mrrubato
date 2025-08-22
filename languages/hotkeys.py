import logging
from pynput import *

logger = logging.getLogger(__name__)

class hotkeys:
  #define action for some sequences.  
  def __init__(self, config):
    self.config = config
    self.name = "hotkeys"
    self.callback = None
    self.funcdict = {}

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
    return cmd

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
        "Start": [55,56],
        "Stop": [56,55],
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
      "Stop": "stop_me",

    }

    return 0  
  
  def act(self, cmd, sequence=[]):
    """ACT based on command and sequence."""
    if cmd in self.funcdict:
      func = self.funcdict[cmd]
      if hasattr(self, func):
        return getattr(self, func)(sequence)
      else:
        logger.error(f"Function {func} not found in {self.__class__.__name__}")
    else:
      print(f"Command {cmd} not found in function maps")
    return -1
  
  def stop_me(self, sequence=[]):
    """Stop MIDI input/output."""
    logger.info(f'> Stop ME')
    return 0
