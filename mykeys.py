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
import sys
import mido
from mido import Message, MidiFile, MidiTrack
from datetime import datetime
from mido.ports import MultiPort
#probably should move..
import extensions.trey.synth as synth
import winsound
import base64
import os
import threading

from collections import defaultdict

#logging.basicConfig(filename='trey.log', 
#    format='%(asctime)s %(levelname)-8s %(message)s',
#    level=logging.INFO,
#    datefmt='%Y-%m-%d %H:%M:%S')    

logger = logging.getLogger(__name__)


def merge(a: dict, b: dict, path=[]):
  for key in b:
      if key in a:
          if isinstance(a[key], dict) and isinstance(b[key], dict):
              merge(a[key], b[key], path + [str(key)])
          elif a[key] != b[key]:
              raise Exception('Conflict at ' + '.'.join(path + [str(key)]))
      else:
          a[key] = b[key]
  return a

def recursive_values(data):
    """
    Recursively walks a nested dictionary (and lists within it)
    and yields all non-container values.
    """
    if isinstance(data, dict):
        for k, value in data.items():
            # If the key is from struct, recurse into it
            if (isinstance(k, int)):
              yield from recursive_values(value)
            else:
              yield value
    else:
        # Base case: if it's a simple value, yield it
        yield data

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
  def __init__(self, config, qapp=None, startx=0, stop_event=None):
    self.config = config
    self.lasttick = time.time()
    self.stop_event = stop_event #stop event for MK
    self.synth_stop_event = None
    self.now = datetime.now()
    self.nowstr = self.now.strftime("%Y%m%d%H%M%S")
    self.mid = self.getmidifile()
    self.langdir = config['keymap']['settings']['LANG_DIR']
    self.transcriptdir = config['keymap']['settings']['TRANSCRIPT_DIR']
    self.qapp = qapp
    self.startx = startx
    self.helpx = config['keymap']['settings']['HELP_X']
    self.maxseq = 30 #can we chain together anything meaningful?  
    self.sequence = []
    self.words = [] #this can be passed from microphone input as well.  
    self.words_ = [] #this is the full list of executed words.  
    self.fullsequence = []
    self.stack = []
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
    self.play_feedback = False
    self.transcript = ""
    self.starttime = time.time()
    self.lasttick = self.starttime

    self.keystruct = {}
    self.qrin = [] #qr inputs

    if (self.config['keymap']['settings']['PLAY_FEEDBACK']):
        self.play_feedback = True
    else:
        self.play_feedback = False


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
      except Exception as e:
        print("language doesnt exist " + key)
        logger.error(f'Error loading language {key}: {e}')

    self.keystruct = self.gen_lang_struct() #initialize keystruct for all known words.  
    print("Keystruct generated")
    print(self.keystruct)


    
  def get_bbox(self):
    
    if (self.currentlangna !="" and hasattr(self.languages[self.currentlangna], 'bbox')):
      return self.languages[self.currentlangna].bbox
    return None
  
  def get_langs(self):
    #get all unique languages used in words
    self.langused = []
    for w in self.words_:
      if (w['langna'] not in self.langused):
        self.langused.append(w['langna'])
    return self.langused
  

  def get_words_(self, prefix=[]):
    if (len(prefix) == 0):
      #filter here for most used words.  
      ret = recursive_values(self.keystruct)

      return ret
    
    if (len(prefix) > 0):
      ret, end = self.get_keystruct(prefix)
      print(end)
      fret = recursive_values(end)
      print(fret)
      return fret      #should include all words with this prefix.. needs reformatting..
  
  def get_spoken_words(self):
    return self.words_


  def get_keystruct(self, keys, struct={}):
    end = self.add_keys(keys, struct)
    return struct, end
  
  def add_keys(self, keys, struct):
      if keys[0] not in struct:
          struct[keys[0]] = {}
      if len(keys) > 1:
        return self.add_keys(keys[1:], struct[keys[0]])
      return struct[keys[0]]

  def gen_lang_struct(self, config=None, lang=""):
    if (config is None):
      struct = {}
      final = {}
      for (l,la) in self.languages.items():
        if (hasattr(la, 'config') and hasattr(la, 'keybot')):
          struct = self.gen_lang_struct(la.config['languages'][l], lang=l)
          final = merge(final, struct)
      return final
    else:
      kb = self.languages[lang].keybot
      struct = {}
      final = {}
      for cmdlen, words in config.items():
        if (cmdlen.isnumeric()):
          for word, vals in words.items():
            ks,end = self.get_keystruct(vals)
            end[word] = {'lang': lang, 'word': word, 'keys': vals} #some info about word..
            #merge ks into struct
            #print(ks)
            final = merge(final, ks)            
          
      return final
    
  def gen_dot(self, config=None, lang=""):
    if (config is None):
      dot = "digraph G {\n"
      dot += "rankdir=LR;\n"
      dot += "node [shape=circle];\n"
      for (l,la) in self.languages.items():
        if (hasattr(la, 'config')):
          dot += self.gen_dot(la.config['languages'][l], lang=l)
      dot += "}\n"
    else:
      dot = ""
      for cmdlen, words in config.items():
        if (cmdlen.is_numeric()):
          for word, vals in words.items():
            for v in vals:
              dot += f'"{lang}:{word}\\n{v["action"]}" -> "{lang}:{v["next"]}\\n{v["next_action"]}" [ label="{cmdlen}" ];\n'
            
    return dot
  
  def add_qrin(self, data):
    #find this QRData.  If exists, ignore.  
    if (data not in self.qrin):
      self.qrin.insert(0, data) #add to start of list
    else:
      #dont keep duplicates for now..
      self.qrin.remove(data)
      self.qrin.insert(0, data) #move to start of list


  def get_qr(self):
    qr = ""
    for (l,la) in self.languages.items():
      if (hasattr(la, 'qr') and la.qr != ""):
        qr += "<" + l + ">\n"
        qr += la.qr + "\n"
        la.qr = "" #reset qr after getting it.
    qr += "<meta>\n"
    words = self.get_words_(self.sequence[self.startseqno:])
    #potentially get most likely words here only.
    for w in words:
      qr += f"~~{w['word']} | {w['keys']} <br>\n" #br working for line breaks..
    #output info about potential keys here.  

    return qr
  
  def start_feedback(self):
    if (self.play_feedback):
      self.synth_stop_event = threading.Event()  # Event to signal stopping
      self.play_thread = threading.Thread(target=synth.play_stream, args=(self.synth_stop_event,))
      self.play_thread.start()

#      from extensions.trey.speech import init_asr_model
#      self.asr_thread = threading.Thread(target=init_asr_model, args=())
#      self.asr_thread.start()


  def unload(self):
    #unload language specific data
    for (l,la) in self.languages.items():
      la.unload()
    if (self.play_feedback):
      logger.info('Stopping Synth thread')
      self.synth_stop_event.set()
      self.play_thread.join()
      time.sleep(2) #wait for this to end
      
    return 0
  
  def set_startx(self, startx):
    print(f'Setting startx for languages to {startx}')
    self.startx = startx
    for (l,la) in self.languages.items():
      la.startx = startx

  def set_geo(self, geo):
    print(f'Setting geometry for languages to {geo}')
    for (l,la) in self.languages.items():
        la.geo = geo

  def callback(self, cmd):
    """Callback function for languages."""
    if cmd in self.funcmaps["global"]:
      func = self.funcmaps[cmd]
      if func in self.languages[self.currentlangna].funcdict: #is there override?  
        getattr(self.languages[self.currentlangna], self.languages[self.currentlangna].funcdict[func])()
      else:
        getattr(self, func)()


  def reset_sequence(self):
#    self.fullsequence.extend(self.sequence)

#dont get rid of midi feedback tracks.  
#    if (len(self.mid.tracks[self.currentchannel]) >= len(self.sequence)):
#      for s in self.sequence:
#        self.mid.tracks[self.currentchannel].pop() #remove from midi track.
        #get rid of unused data..

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
    orig = ss.copy()
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
      #are we second word or first word?  
      #if we are second word, we must not remove the first word.


      self.sequence = self.sequence[:-len(orig)] #remove length of original sequence.  
      self.sequence = self.sequence[:-len(self.words[-1]['sequence'])] #remove length of last word.      

      self.words[-1]['ss'] = ss
      self.words_.append(self.words[-1]) #add to executed words.

      self.words = self.words[:-1 ] #remove last word as it executed.  
      self.currentlangna = self.words[-1]['langna'] if len(self.words) > 0 else ""
      self.currentlang = self.words[-1]['lang'] if len(self.words) > 0 else ""
      self.currentcmd = self.words[-1]['word'] if len(self.words) > 0 else None
      self.currentseqno = len(self.sequence)

      if (hasattr(self.languages[l], 'transcript') and self.languages[l].transcript != ""):
        self.transcript += self.languages[l].transcript + " "
        logger.info(f'Audio Transcript updated: {self.transcript}')
        seq = self.text2seq(self.languages[l].transcript)
        for idx,s in enumerate(seq):
          #for now assume we are not getting any new messages while appending this..  
          #or get last message time.
#          mytime = int((time.time()-self.starttime) * 1000)
          msg = Message('note_on', note=s, velocity=64, time=10) #microseconds..
          self.mid.tracks[self.currentchannel].append(msg) #add transcript
          msg = Message('note_off', note=s, velocity=64, time=10)
          self.mid.tracks[self.currentchannel].append(msg) #add transcript
          #only adding for posterity right now.  
        time.sleep(len(seq)*2/1000) #wait for notes to play out. 500 chars/sec

        self.languages[l].transcript = "" #reset transcript after adding to midi.

      return self.sequence
#      self.reset_sequence()
#      self.currentcmd = None
    elif (action < -1):
      #error in action
      logger.info(f'> <{l}>{cmd}_ {ss}')
      winsound.Beep(1000, 250) #beep to end success
      #reset command sequence to current sequence number.  
      # This command only needs closure keys.  
      
      #do we add here??  Maybe not..
      #self.words_.append({"word": cmd+"_", "lang": l, "langna": l, "sequence": self.sequence[self.startseqno:], "ss": [], "_words": self.words}) #add to executed words.

#      self.startseqno = self.currentseqno
#      self.currentcmd = self.currentcmd

    else:
      #set to None here?  Or keep currentcmd?
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
    logger.info(f'Key pressed: {note} Msg: {msg}')

    if (hasattr(msg, 'time') and msg.time <= 0):
      #this is default at the moment..
      temptime = time.time() - self.lasttick #msg.time #time.time() #msg.time
      msg.time = int(temptime * 1000) #time since last msg

    if self.play_feedback:
      #sound feedback when playing a note.  

      if (msg.type == 'note_on' and hasattr(msg, 'velocity') and msg.velocity > 0):
          self.lasttick = time.time()
          synth.note_on(msg.note, msg.velocity)
          self.mid.tracks[self.currentchannel].append(msg)
#          synth.play_note(msg.note, 0.3, msg.velocity/127)
      elif (msg.type == 'note_off' or (msg.type == 'note_on' and hasattr(msg, 'velocity') and msg.velocity == 0)):
          self.lasttick = time.time()
          synth.note_off(msg.note)
          self.mid.tracks[self.currentchannel].append(msg)

      #should also append audio transcript text here to keep in time..


    if hasattr(msg, 'type') and msg.type=='note_on' and hasattr(msg, 'velocity') and msg.velocity > 0:
      #data is stale, start again.  
      if (temptime > 10): #longer than 10 seconds..
        self.reset_sequence()
        print("Resetting sequence due to long time since last note")
#        winsound.Beep(2000, 500) #beep to end error

#        print("Resetting sequence due to long time since last note")


      if (self.currentseqno > self.maxseq):
        #trim sequence to max length.  
        self.reset_sequence()
        print("Resetting sequence due to max sequence length")
        return -1 #too long sequence notify error.  
        
      self.sequence.append(note)
      #not using currentchannel at the moment.. all languages using same track..
      #self.currentchannel = self.currentlang.keybot - 48 
      #have to move each word?  dont like this..


      self.currentseqno += 1
      self.lastnotetime = self.lasttick
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
        #start of word, take start of word action.  
        if (word != ""):
          self.takeaction(word, l, [], callback)

      else:
        #second word check occurs distinguish between parameters and new command.
        #if we find a new command, we switch to that command.
        #currently not sure if we are coming out of this loop correctly.  
        #need more complex command structure before it is meaningful to check this.  
        word, l, la = self.findword(self.sequence[self.startseqno:])
      if (word != ""):
        found = True
        print(f"&<{l}>{word}\n")
        logger.info(f'&<{l}>{word}\n')
        #_words words before this one.  
        self.words.append({"word": word, "lang": la, "langna": l, "sequence": self.sequence[self.startseqno:], "ss": [], "_words": self.words})
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
        logger.info("> " + self.currentcmd + " " + str(self.sequence[self.startseqno:]))
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
        logger.info(f'Action returned {a} for {self.currentcmd} {self.sequence[self.startseqno:]}')
        if (isinstance(a, int)): #should always be true
          if (a == -1):
            #reset action
            logger.info(f'!! > <{self.currentlangna}>{self.currentcmd} {self.sequence[self.startseqno:]}')
            #reset command
            self.reset_sequence()
            self.currentcmd = None
            winsound.Beep(2000, 500) #beep to end error
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
            winsound.Beep(1000, 500) #beep to end complete without error
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
  
  #switch current control set.  Not used at the moment.
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
  

  def text2seq(self, text):
    #convert text to sequence.  
    seq = []
    seq.append(110) #start text
      
    for c in text:
      n = ord(c)
      if (n >= 0 and n <= 255):
        c1 = n // 16
        c2 = n % 16
        note1 = 112 + c1
        note2 = 112 + c2
        seq.append(note1)
        seq.append(note2)
        print(f'Encoded char {c} to notes [{note1},{note2}]')
      else:
        print(f'Error: character {c} out of range')
        logger.error(f'Error: character {c} out of range')

    seq.append(111) #end text    
    return seq
  def seq2text(self, seq):
    #convert sequence to text.  
    text = ""
    
    skip = False
    for idx, m in enumerate(seq):
      if (skip):
        skip = False
        continue
      if (m > 109 and m < 112 ):
        text += "\n" #some separation.  
      elif (m >=112 and m <=127): #E8 to G9
        if (idx+1 >= len(seq)):
          print("!!>seq2text: odd length sequence error")
          logger.error("!!>seq2text: odd length sequence error")
          continue
        n = seq[idx+1]  
        if (n < 112 ):
          print("!!>seq2text: incorrect value for text sequence")
          logger.error("!!>seq2text: incorrect value for text sequence")
          skip = True
        c1 = (m - 112) * 16
        c2 = (n - 112)
        c = c1 + c2
        text += chr(c)
        print(f'Char from seq: {c1} {c2} {chr(c)}')
        skip = True
        
      else:
        #ignore non-text notes.
        c1 = 0
    
    return text
  

  def midi2text(self, mid):
    #convert midi keys back to text.  
    text = ""
    track1 = mid.tracks[0]
    track2 = mid.tracks[1]
    if (track1.len() != track2.len()):
      print("Error: midi tracks not same length")
      logger.error("Error: midi tracks not same length")
      return text
    
    for msg in track1:
      msg2 = next(track2) #should be same length
      if msg.type == 'note_on' and msg.velocity > 0:
        if (msg.note >= 112 and msg2.note >= 112): #E8
          c1 = (msg.note - 112) * 16
          c2 = (msg2.note - 112)
          c = c1 + c2
          text += chr(c)
        else:
          #ignore non-text notes.
          c1 = 0
      
    return text
  
  def getmidifile(self):
    #default 2 tracks and control..
    mid = MidiFile(type=1)
#    mid.ticks_per_beat = 1000000
#    mid.tempo = 60
    track = MidiTrack()
    track2 = MidiTrack()
    controltrack = MidiTrack()
#    track.append(MetaMessage('set_tempo', tempo=100000, time=0))
    mid.tracks.append(track)
    mid.tracks.append(track2)
    mid.tracks.append(controltrack)
    track.append(Message('program_change', channel=0, program=0, time=0))
    track2.append(Message('program_change', channel=0, program=0, time=0))
    controltrack.append(Message('program_change', channel=0, program=0, time=0))
    return mid

  def savemidi(self, fname=""):
    if (fname == ""):
      #use year folder
      fname = self.transcriptdir + "/" + self.nowstr[0:4] + "/" + self.nowstr + ".mid"
    folder = os.path.dirname(fname)
    if not os.path.exists(folder):
      os.makedirs(folder)
    self.mid.save(fname)
    logging.info("$$TRANSCRIPT=" + fname + "\n")
    print("$$TRANSCRIPT=" + fname + "\n")


  def text2midi(self, text):
    #convert text to midi keys.  
    mid = MidiFile()
#    mid.ticks_per_beat = 1000000
#    mid.tempo = 60
    track = MidiTrack()
    controltrack = MidiTrack()
    track2 = MidiTrack()
#    track.append(MetaMessage('set_tempo', tempo=100000, time=0))
    mid.tracks.append(track)
    mid.tracks.append(track2)
    track.append(Message('program_change', channel=0, program=81, time=0))
    track2.append(Message('program_change', channel=0, program=81, time=0))
    shorttime = 50
#    text = text.upper()
    basenote = 112 #E8


    words = text.split(' ')
    b64folder = ""
    totaltime = 0
    for w in words:

      #such a stupid thing to need to do..
      b64word = base64.b64encode(w.encode('utf-8')).decode('utf-8')
      b64folder += "/" + str(b64word)
      basemsg = Message('note_on', note=basenote, velocity=32, time=0) #all notes off
      track.append(basemsg)
      track2.append(basemsg)
      for c in w:
        note1 = basenote + ord(c) // 16
        note2 = basenote + ord(c) % 16
        print(f'Note [{note1},{note2}] for char {c}')
        omsg = Message('note_on', note=note1, velocity=64)
        track.append(omsg)
        omsg2 = Message('note_on', note=note2, velocity=100)
        track2.append(omsg2)
        omsgoff = Message('note_off', note=note1, velocity=0, time=shorttime)
        omsgoff2 = Message('note_off', note=note2, velocity=0, time=shorttime)
        track.append(omsgoff)
        track2.append(omsgoff2)
        totaltime += shorttime

      baseoff = Message('note_off', note=basenote, velocity=0, time=shorttime*4)
      totaltime += shorttime*4
      track.append(baseoff)
      track2.append(baseoff)


    
    if (len(text) > 64):
      print("Text too long for midi, not saving.")
      return mid
    else:
      if not os.path.exists(self.langdir + "/" + b64folder):
        #do we want to save this?  to use for what?  
        os.makedirs(self.langdir + "/" + b64folder)
        mid.save(self.langdir + "/" + b64folder + "/" + "1" + '.mid')
    
    print('total time ' + str(totaltime))
    return mid
  
  def playmidi(self, mid):
    #play midi file.  
    with mido.open_output() as outport:
      for msg in mid.play():
        print(msg)
        outport.send(msg)
    return 0
    
if (__name__ == "__main__"):
  sys.path.insert(0, 'c:/devinpiano/') #config.json path
  sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
  import config 

  mykeys = MyKeys(config.cfg)
  text = "This is a test of the midi text to key system"
  print("testing text to midi for: " + text)
  mid = mykeys.text2midi(text)
  mykeys.playmidi(mid)
  print("Done")