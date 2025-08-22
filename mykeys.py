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
import logging
import time

#logging.basicConfig(filename='trey.log', 
#    format='%(asctime)s %(levelname)-8s %(message)s',
#    level=logging.INFO,
#    datefmt='%Y-%m-%d %H:%M:%S')    

logger = logging.getLogger(__name__)


class MyLang:
  #define action for some sequences.  
  def __init__(self, config):
    self.config = config

  def act(self, cmd, sequence=[]):
    """ACT based on command and sequence."""
    return -1

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
    #load language specific data
    print("No load_data method defined for " + self.__class__.__name__)
    return 0
  
  def getKeys(self):
    return self.config['keymap']['languages'][self.config['currentlangna']]
  

class MyKeys:
  def __init__(self, config):
    self.config = config
    self.sequence = []
    self.fullsequence = []
    self.languages = {} #language modules.  
    self.langkey = []
    self.langna = []
    self.langused = []
    self.keybots = {} #botkey for each language.  
    self.keymaps = {} #keymaps for each language Just data.  
    #do we need to have fuzzy searching?  
    self.funcmaps = {} #function maps for each language -> language -> function
      #then funcdict for each language?  
    self.currentlang = None
    self.currentlangna = ""
    self.currentchannel = 0
    self.transcripts = {} #transcripts for each language
    self.currentseqno = 0
    self.startseqno = -16  #start of word/phrase.  #no phrases longer than 16 keys.  
    self.lastnotetime = 0
    self.currentcmd = None
    self.notes = np.zeros(config['keymap']['global']['top'] - config['keymap']['global']['bottom'], dtype=int)


    for key, value in config['keymap']['languages'].items():
      #load files
      try:
        la = importlib.import_module("languages." + key)
        la = getattr(la, key)  # Class From file
        if la is not None:
          if self.currentlang is None:
            self.currentlang = la
            self.currentlangna = key

          self.langused.append(key)
          #just use this language config.  
          self.languages[key] = la(config)  # Create instance of class
          self.languages[key].load()
          self.languages[key].callback = self.callback
          self.langkey.append(value)
          self.langna.append(key)
          print("language added " + key)
      except:
        print("language doesnt exist " + key)
  

  def callback(self, cmd):
    """Callback function for languages."""
    if cmd in self.funcmaps["global"]:
      func = self.funcmaps[cmd]
      if func in self.languages[self.currentlangna].funcdict: #is there override?  
        getattr(self.languages[self.currentlangna], self.languages[self.currentlangna].funcdict[func])()
      else:
        getattr(self, func)()


  def reset_sequence(self):
    self.fullsequence.extend(self.sequence)
    self.sequence = []
    self.currentseqno = 0
    self.startseqno = -16
    self.lastnotetime = 0
    
  def key(self, note, msg, callback=None):
    #add this key to the notes map
    #if hasattr(msg, 'type') and msg.type=='note_on' and 
    #adjust message channel for anything but base channel
    #for now dont use tracks, just channels.  

    if (hasattr(msg, 'time') and msg.time <= 0):
      msg.time = int(time.time() * 1000)

    if hasattr(msg, 'type') and msg.type=='note_on' and hasattr(msg, 'velocity') and msg.velocity > 0:
      #data is stale, start again.  
      if (self.lastnotetime < msg.time - 10000):
        self.reset_sequence()
        print("Resetting sequence due to long time since last note")

#        print("Resetting sequence due to long time since last note")

      self.sequence.append(note)
      self.currentseqno += 1
      self.lastnotetime = msg.time
      print(self.sequence)
      #try fixed length?  try to read messages.  If just garbage, check for any known word.  
      if (self.sequence[-3:] == self.config['keymap']['global']['Reset']):
        self.reset_sequence()
        return

      r1 = 4 #max length of sequence to check
      if (self.currentseqno <4):
        r1 = self.currentseqno

      found = False
      if (self.currentcmd is None):
        for i in range(r1, 0, -1):
          found = False
          #check all languages.  Not using global for now.  
          for (l,la) in self.languages.items():
            #really should create a keys -> word map for each language.
            word = la.word(self.sequence[-i:])
            if word != "":
              #found a word in the language
              found = True
              self.currentcmd = word
              self.currentlangna = l
              self.currentlang = la
              self.startseqno = self.currentseqno
              print("Word found: " + self.currentcmd + " in " + l)
              logger.info(f'Word found: {self.currentcmd} in {l}')

              break
          if found:
            break
                


  #      if (self.sequence[-4:] == self.config['keymap']['global']['LangSelect']):
  #        lkey = self.langkey.index(self.sequence[-2:])
  #        if lkey > -1:
  #          self.switchLang(lkey)

      if (self.currentcmd is not None):
#        print("> " + self.currentcmd + " " + str(self.sequence[self.startseqno:]))
        #check for any languages that can handle this sequence. we did not find a command.  
        action = self.languages[self.currentlangna].act(self.currentcmd, self.sequence[self.startseqno:])
        if (action == -1):
          #reset action
          logger.info(f'!! > <{self.currentlangna}>{self.currentcmd} {self.sequence[self.startseqno:]}')
          #reset command
          self.reset_sequence()
          self.currentcmd = None
        elif (action == 0):
          #action was successful, reset command
          logger.info(f'> <{self.currentlangna}>{self.currentcmd} {self.sequence[self.startseqno:]}')
          if callback is not None:
            callback(self.currentcmd + " " + str(self.sequence[self.startseqno:]))
          self.reset_sequence()
          self.currentcmd = None
        else:
          self.currentcmd = self.currentcmd
          return action
          #still waiting?  
#          logger.info(f'_ {self.currentcmd} {self.sequence[self.startseqno:]}')


  def getLangs(self):
    return ','.join(self.langused)

  def getSequence(self, length=2):
    if (len(self.sequence) >= length):
      return self.sequence[-length:]
    else:
      return -1

  def printMe(self):
    print("Current sequence: " + str(self.sequence))
    print("Full sequence: " + str(self.fullsequence))
    print("Current language: " + self.currentlangna)
    print("Current channel: " + str(self.currentchannel))
    print("Current seq no: " + str(self.currentseqno))
    print("Start seq no: " + str(self.startseqno))
    print("Last note time: " + str(self.lastnotetime))
    print("Notes: " + str(self.notes))


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
  
    