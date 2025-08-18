from pynput import *
import logging

logger = logging.getLogger(__name__)


class _meta:
  #define action for some sequences.  
  def __init__(self, config):
    self.config = config
  
  def act(self, sequence):
    
    return -1

