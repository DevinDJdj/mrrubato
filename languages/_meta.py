from pynput import *
import logging

logger = logging.getLogger(__name__)


class _meta:
  #define action for some sequences.  
  def __init__(self, config):
    self.config = config
  
  def act(self, sequence):
    
    return -1

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
        "Start": [24,21],
        "Stop": [24,22],
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


  def start_me(self, sequence=[]):
    #Pass parameter for which topic to start.  
    #for now just -N entries.  
    """Start Recording"""
    logger.info(f'> Start _ME')
    return 0
  
  def stop_me(self, sequence=[]):
    """Stop Recording"""
    logger.info(f'> Stop _ME')
    return 0
