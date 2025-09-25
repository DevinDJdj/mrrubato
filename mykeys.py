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

import mido
from mido import Message, MidiFile, MidiTrack

from mido.ports import MultiPort

import base64
import os
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
  def __init__(self, config, qapp=None, startx=0):
    self.config = config
    self.langdir = config['keymap']['settings']['LANG_DIR']
    self.qapp = qapp
    self.startx = startx
    self.maxseq = 20 #can we chain together anything meaningful?  
    self.sequence = []
    self.words = [] #this can be passed from microphone input as well.  
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
    self.startseqno = 0  #start of word/phrase.  #no phrases longer than 16 keys.  
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
          self.languages[key] = la(config, self.qapp, self.startx)  # Create instance of class pass qapp for any UI stuff
          self.languages[key].load()
          self.languages[key].callback = self.callback
          if (self.languages[key].maxseq > self.config['keymap']['settings']['MAX_WORD']):
            self.maxseq = self.languages[key].maxseq

          self.langkey.append(value)
          self.langna.append(key)
          print("language added " + key)
      except:
        print("language doesnt exist " + key)


  def unload(self):
    #unload language specific data
    for (l,la) in self.languages.items():
      la.unload()
    return 0
  
  def set_startx(self, startx):
    print(f'Setting startx for languages to {startx}')
    self.startx = startx
    for (l,la) in self.languages.items():
      la.startx = startx


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
    self.words = []
    self.currentcmd = None
    self.currentlang = None
    self.currentlangna = ""
    self.currentseqno = 0
    self.startseqno = 0
    self.lastnotetime = 0
    
  def findword(self, sequence=[]):
    """Find word in all languages."""
    for (l,la) in self.languages.items():
      word = la.word(self.sequence)
      if word != "":
        return word, l, la
    return "", "", None
      
  def takeaction(self, cmd, l, ss, callback=None):
    #take action based on action returned from language.  
    #pass words as well.  
    logger.info(f'Checking action {cmd} in {l} for {ss}')
    action = self.languages[l].act(cmd, self.words, ss)
    if (action == -1):
      #reset action
      logger.info(f'!! > <{l}>{cmd} {ss}')
      #reset command
      self.reset_sequence()
      self.currentcmd = None
    elif (action == 0):
      #action was successful, reset command
      logger.info(f'> <{l}>{cmd} {ss}')
      if callback is not None:
        callback(cmd + " " + str(ss))

      #last command succeeds.  retrigger without this sequence.  
      #remove ss from end of sequence instead of resetting everything.  
      self.sequence = self.sequence[-len(ss):] #remove length of sequence.  
      self.sequence = self.sequence[-len(self.words[-1]['sequence']):] #remove length of last word.      
      self.words = self.words[:-1 ] #remove last word as it executed.  
      self.currentlangna = self.words[-1]['langna'] if len(self.words) > 0 else ""
      self.currentlang = self.words[-1]['lang'] if len(self.words) > 0 else ""
      self.currentcmd = self.words[-1]['word'] if len(self.words) > 0 else None
      self.currentseqno = len(self.sequence)

      return self.sequence
#      self.reset_sequence()
#      self.currentcmd = None
    else:
      self.currentcmd = self.currentcmd
      #search for word again?            
      #if isinstance(action, list):
        #nword, nl, nla = self.findword(action)
        #if (nword != ""):
          #change return action to new value.  
      #a = self.languages[]
      return action #return 
    return action
  
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


      if (self.currentseqno > self.maxseq):
        #trim sequence to max length.  
        self.reset_sequence()
        print("Resetting sequence due to max sequence length")
        return -1 #too long sequence notify error.  
        
      self.sequence.append(note)
      self.currentseqno += 1
      self.lastnotetime = msg.time
      print(self.sequence)
      #try fixed length?  try to read messages.  If just garbage, check for any known word.  
      if (self.sequence[-3:] == self.config['keymap']['global']['Reset']):
        self.reset_sequence()
        print("Resetting sequence due to Reset key")
        return -1 #reset sequence notify error.


      r1 = self.maxseq #max length of sequence to check
      if (self.currentseqno <self.maxseq):
        r1 = self.currentseqno


      found = False
      word = ""
      l = ""
      la = None
      if (self.currentcmd is None):
        word, l, la = self.findword(self.sequence)
      else:
        word, l, la = self.findword(self.sequence[self.startseqno:])
      if (word != ""):
        found = True
        print("Second Word found: " + word + " in " + l)
        logger.info(f'Second Word found: {word} in {l}')
        self.words.append({"word": word, "lang": la, "langna": l, "sequence": self.sequence[self.startseqno:]})
        self.startseqno = self.currentseqno
        self.currentcmd = word
        self.currentlang = la
        self.currentlangna = l
        
      """
      if (self.currentcmd is None):
#        for i in range(r1, 0, -1):
          found = False
          #check all languages.  Not using global for now.  
          for (l,la) in self.languages.items():
            #really should create a keys -> word map for each language.
#            word = la.word(self.sequence[-i:])
            word = la.word(self.sequence)
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
#          if found:
#            break
    """                


  #      if (self.sequence[-4:] == self.config['keymap']['global']['LangSelect']):
  #        lkey = self.langkey.index(self.sequence[-2:])
  #        if lkey > -1:
  #          self.switchLang(lkey)

      if (self.currentcmd is not None):
#        print("> " + self.currentcmd + " " + str(self.sequence[self.startseqno:]))
        #check for any languages that can handle this sequence. we did not find a command.  
        scmd = self.currentcmd
        ss = self.sequence[self.startseqno:]
        slangna = self.currentlangna
        #pass for determining action.  
        #if action is still expected, return [sequence]



        a = ss
        while (isinstance(a, list) and a != []):
          #potential to unwind entire stack here.  
          if (slangna == ""):
            print(f'Error: {scmd} no language for action' + str(a))
            break
          a = self.takeaction(scmd, slangna, ss, callback)
          scmd = self.currentcmd
          slangna = self.currentlangna
          #keep ss the same?
#          ss = self.sequence[self.startseqno:]
#          ss = a
          #still waiting?  
#          logger.info(f'_ {self.currentcmd} {self.sequence[self.startseqno:]}')

        #loop complete, did we do anything?  
        #so completing the loop requires a closure of the same number of commands in order to actually be executed.  
        #yeah I think thats nice.  But not sure if it will work logically.  
        print(f'Action returned {a} for {self.currentcmd} {self.sequence[self.startseqno:]}')
        if (isinstance(a, int)): #should always be true
          if (a == -1):
            #reset action
            logger.info(f'!! > <{self.currentlangna}>{self.currentcmd} {self.sequence[self.startseqno:]}')
            #reset command
            self.reset_sequence()
            self.currentcmd = None
          elif (a == 0):
            #action was successful, reset command
            logger.info(f'> <{self.currentlangna}>{self.currentcmd} {self.sequence[self.startseqno:]}')
            if callback is not None:
              callback(self.currentcmd + " " + str(self.sequence[self.startseqno:]))

            if (self.currentcmd == scmd):
              self.reset_sequence()
              #command completed.  
            #last command succeeds.  retrigger without this sequence.  
            #remove ss from end of sequence instead of resetting everything.  
            if (len(self.sequence) > 0):
              #rerun command
              self.key(self.sequence[-1], msg, callback)
              #this is closure of command.  So we know if we were waiting, it has completed.  
              #so act if seq[-1] == seq[-2] then we are done.
              #if there is nothing in expected variable, then take default.  
              #all actions expected variables must have default value.  

#            else:
#              self.reset_sequence()
        #      self.reset_sequence()
#              self.currentcmd = None
        else:
          print("Error: action not int") #action not intended ..
          print(a)
#          self.reset_sequence()

    return 0

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
  

  def text2midi(self, text):
    #convert text to midi keys.  
    mid = MidiFile()
#    mid.ticks_per_beat = 1000000
#    mid.tempo = 60
    track = MidiTrack()
    controltrack = MidiTrack()
#    track.append(MetaMessage('set_tempo', tempo=100000, time=0))
    mid.tracks.append(track)
    mytime = 0
#    text = text.upper()
    basemsg = Message('note_on', control=basenote, value=127, time=mytime) #all notes off
    track.append(basemsg)

    words = text.split(' ')
    b64folder = ""
    basenote = 112 #E8
    for w in words:
      b64word = base64.b64encode(w)
      b64folder += "/" + str(b64word)
      for c in text:
        note1 = basenote + ord(c) // 16
        note2 = basenote + ord(c) % 16
        print(f'Note [{note1},{note2}] for char {c}')
        omsg = Message('note_on', note=note1, velocity=127, time=mytime)
        track.append(omsg)
        mytime += 100
        omsgoff = Message('note_off', note=note1, velocity=0, time=mytime)
        track.append(omsgoff)
        omsg2 = Message('note_on', note=note2, velocity=127, time=mytime)
        track.append(omsg2)
        mytime += 100
        omsgoff2 = Message('note_off', note=note2, velocity=0, time=mytime)
        track.append(omsgoff2)

      baseoff = Message('note_off', control=basenote, value=0, time=mytime)
      track.append(baseoff)
      mytime += 300
      basemsg = Message('note_on', control=basenote, value=127, time=mytime) #all notes off
      track.append(basemsg)
      continue



    if (len(text) > 64):
      print("Text too long for midi, not saving.")
      return mid
    else:
      if not os.path.exists(self.langdir + "/" + b64folder):
        #do we want to save this?  to use for what?  
        os.makedirs(self.langdir + "/" + b64folder)
        mid.save(self.langdir + "/" + b64folder + "/" + "1" + '.mid')

    return mid
  
  def playmidi(self, mid):
    #play midi file.  
    with mido.open_output() as outport:
      for msg in mid.play():
        print(msg)
        outport.send(msg)
    return 0
    