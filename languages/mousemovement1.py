from pynput import *
import logging

logger = logging.getLogger(__name__)


class mousemovement1:
  #define action for some sequences.  
  def __init__(self, config):
    self.config = config
    self.name = "mousemovement1"
    self.mouse = mouse.Controller()
  
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
    if (self.__class__.__name__ in self.config['languages']):
      logger.info(f'Loading language data for {self.__class__.__name__}')
    elif hasattr(self, 'load_data'):
      self.load_data()
    else:
      print("No Data defined for " + self.__class__.__name__)  
    return 0
  
  def load_data(self):

    #load language specific data into the config.  
    self.config['languages']['mousemovement1'] = {
      "1": {
        "Left Click": [49],
        "Right Click": [50],
      }
    }
    self.funcdict = {
      "Left Click": "left_click",
      "Right Click": "right_click",
    }
    return 0
  
  def left_click(self):

    mouse.click(mouse.Button.left)
    return 0
  
  def right_click(self):
    mouse.click(mouse.Button.right)
    return 0