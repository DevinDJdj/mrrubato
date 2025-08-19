from pynput import *
import logging

logger = logging.getLogger(__name__)


class mousemovement1:
  #define action for some sequences.  
  def __init__(self, config):
    self.config = config
    self.name = "mousemovement1"
    self.mouse = mouse.Controller()
    self.callback = None
  
  def act(self, cmd, sequence=[]):
    """ACT based on command and sequence."""
    return -1

  def word(self, sequence=[]):
    """Word lookup."""

    cmd = ""
    sl = str(len(sequence))
    if (sl in self.config['languages'][self.name]):
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
      print("No Data defined for " + self.__class__.__name__)  
    return 0
  
  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
        "Left Click": [59,58],
        "Right Click": [62,63],
      }
    }
    if (self.name in self.config['languages']):
      logger.info(f'Merging existing {self.name} config')
      default.update(self.config['languages'][self.name])
    else:
      logger.info(f'No existing {self.name} config found, creating new one')

    self.config['languages'][self.name] = default

    self.funcdict = {
      "Left Click": "left_click",
      "Right Click": "right_click",
    }
    self.config['languages'][self.name] = default
    return 0
  
  def left_click(self):

    mouse.click(mouse.Button.left)
    return 0
  
  def right_click(self):
    mouse.click(mouse.Button.right)
    return 0