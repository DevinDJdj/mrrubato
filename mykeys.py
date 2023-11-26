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
#Lets limit for now to 8 langs per iteration.  
#Lets dynamically use the languages.  

from languages import * #maybe we want this to be dynamic, but for now whatever.  
import importlib

class MyLang:
  #define action for some sequences.  
  def __init__(self, config):
    self.config = config
  
  def act(self, sequence):
    return -1

class MyKeys:
  def __init__(self, config):
    self.config = config
    self.sequence = []
    self.languages = []
    self.langkey = []
    self.langna = []
    self.langused = []
    self.currentlang = None
    self.currentlangna = ""
    self.currentchannel = 0
    self.notes = np.zeros(config['keymap']['global']['top'] - config['keymap']['global']['bottom'], dtype=int)
    for key, value in config['keymap']['languages'].items():
      #load files
      try:
        la = importlib.import_module("languages." + key)
        if la is not None:
          if self.currentlang is None:
            self.currentlang = la
            self.currentlangna = key
            self.langused.append(key)
          self.languages.append(la)
          self.langkey.append(value)
          self.langna.append(key)
          print("language added " + key)
      except:
        print("language doesnt exist " + key)
  
  def key(self, note, msg):
    #add this key to the notes map
    #if hasattr(msg, 'type') and msg.type=='note_on' and 
    #adjust message channel for anything but base channel
    #for now dont use tracks, just channels.  
    if hasattr(msg, 'channel') and msg.channel ==0:
      if (self.currentchannel > 0):
        msg.channel = self.currentchannel+8
    if hasattr(msg, 'type') and msg.type=='note_on' and hasattr(msg, 'velocity') and msg.velocity > 0:
      self.sequence.append(note)
      if (self.sequence[-4:-2] == self.config['keymap']['global']['LangSelect']):
        lkey = self.langkey.index(self.sequence[-2:])
        if lkey > -1:
          self.switchLang(lkey)
        
      if self.currentlang is not None:
        mylang = getattr(self.currentlang, self.currentlangna)

        myla = mylang(self.config) # Class From file 
        myla.act(self.sequence)


  def getLangs(self):
    return ','.join(self.langused)

  def getSequence(self, length=2):
    if (len(self.sequence) >= length):
      return self.sequence[-length:]
    else:
      return -1
    
  #add dictionary of functions not sure if we can do multiple languages at once.  
  # for now just using one.  Dict contains KEYS->Function
  def addLang(self, d):
    return -1
  
  #switch current control set.  
  def switchLang(self, lkey):
    if self.langna[lkey] not in self.langused:
      if len(self.langused) < 8:
        self.langused.append(self.langna[lkey])
      else:
        print("too many languages in one iteration! cant switch languages")
        return

    self.currentlang = self.languages[lkey]
    self.currentlangna = self.langna[lkey]
    if self.currentlangna in self.langused:
      self.currentchannel = self.langused.index(self.currentlangna)
      print("channel " + str(self.currentchannel))

    print("switchLang " + self.currentlangna)
  
    