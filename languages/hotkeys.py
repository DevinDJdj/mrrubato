class hotkeys:
  #define action for some sequences.  
  def __init__(self, config):
    self.config = config
  
  def act(self, sequence):
    return -1