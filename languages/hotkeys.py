import logging
from pynput import *

logger = logging.getLogger(__name__)

class hotkeys:
  #define action for some sequences.  
  def __init__(self, config):
    self.config = config
  
  def load(self):
    #load language specific data
     #config overrides load_data by default.  
    if (self.__class__.__name__ in self.config['keymap']['languages']):
      logger.info(f'Loading language data for {self.__class__.__name__}')
    elif hasattr(self, 'load_data'):
      self.load_data()
    else:
      print("No Data defined for " + self.__class__.__name__)  
    return 0

  def load_data(self):

    #load language specific data into the config.  
    self.config['keymap']['languages']['hotkeys'] = {
      "Start": [1],
      "Stop": [2],
    }
    self.funcdict = {
    }

    return 0  
  
  def act(self, sequence):
    return -1