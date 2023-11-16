import numpy as np
#midi controller points
#how do we adjust octaves and/or spacing
#Must use keys themselves to do all state changes.  
#C->E at bottom of keyboard?  
#at least two keys 
#can have some cycles.  
#but largely we would only have a few groupings.  
#this mimics the use of the computer keyboard which is nice.  
#so what are the cycles.  
#Movement and drawing?  


#algorithm points
#multikey detection

#will not use timing at the moment, this is too hard for users to reproduce.  
#only sequence is important.  
class MyKeysConfig:
  def __init__(self, bottom=21, top=108):
    self.bottom = bottom
    self.top = top


class MyKeys:
  def __init__(self, config):
    self.config = config
    self.sequence = []
    self.notes = np.zeros(config.top - config.bottom, dtype=int)

  
  def key(self, note):
    #add this key to the notes map
    self.sequence.append(note)
  
  def getSequence(self, length=2):
    if (len(self.sequence) >= length):
      return self.sequence[-length:]
    else:
      return -1