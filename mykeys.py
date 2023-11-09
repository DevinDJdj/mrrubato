import numpy as np

class MyKeys:
  def __init__(self, config):
    self.config = config
    self.notes = np.zeros(config.top - config.bottom, dtype=int)

  
  def key(self, msg):
    #add this key to the notes map