import logging
from pynput import *
import time
from datetime import datetime, timedelta
import languages.helpers.transcriber as transcriber
#import extensions.trey.playwrighty as playwrighty
import languages.helpers.timewindow as timewindow

logger = logging.getLogger(__name__)

class _meta:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.transcriber = None
    self.qapp = qapp
    self.func = None
    self.cmd = None
    self.qr = "" #info for QR message
    self.startx = startx
    self.name = "_meta"
    self.keybot = 48 #
    self.mid = 60 #middle C for bbox calc
    self.keyoffset = 0 #offset within octave mapping
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.audio_transcript = ""
    self.funcdict = {}
    self.suggestions = []
    self.alltopics = {}
    self.topicarray = []
    self.booktopicarray = [] #for only selected book..
    self.filteredtopicarray = []
    self.topichistory = [] #store past topics for context.  This is not currently used for anything but could be used for context in future functions.

    self.bookarray = []
    self.filteredbookarray = []
    self.bookhistory = []
    self.allbooks = {}
    self.selectedbook = None
    self.selectedbookindex = None
    self.selectedfilteredbookindex = None
    self.selectedtopic = None
    self.selectedtopicindex = None
    self.selectedfilteredtopicindex = None
    self.speed = 1.0
    self.zoom = 1.0
    self.timewindow = timewindow.timewindow(self) #starttime/endtime, etc.  

    #filter langs: 48,      49,      50,       51 .. 
#    self.langs = ["_meta", "video", "book", "video", "hotkeys", "hotkeys", "hotkeys", "hotkeys", "check"]


  def word(self, sequence=[]):
    """Word lookup."""
    
    cmd = ""
    sl = str(len(sequence))
    if (sl in self.config['languages'][self.name]):
      logger.info(f'Looking up sequence {sequence} in video')
      logger.info(self.config['languages'][self.name][sl])
      for k,v in self.config['languages'][self.name][sl].items():
        #check global first.  
        if (sequence == v):
          #can compare directly.  if strings, we do ','.join(self.sequence[-i:]) == v
          found = True
          cmd = k
          self.cmd = cmd
    return cmd

  def unload(self):
    #unload language specific data
    return 0
  
  def load(self, transcriber=None):
    #load language specific data
     #config overrides load_data by default.  
    if (transcriber is not None):
      self.transcriber = transcriber
    if hasattr(self, 'load_data'):
      self.load_data()
    else:
      logger.info(f'!! <{self.__class__.__name__}> No Data')
      print(f'!! <{self.__class__.__name__}> No Data')  
    return 0


  def load_transcript(self):
    #load commands from config into funcdict
    allcmds = self.transcriber.read(self.name, None, None) #default 7 days
    logger.info(f'Loaded {len(allcmds)} command transcripts for {self.name}')

    #load 6 months of book topics..
    book = self.transcriber.read('book', self.transcriber.getTime(-180), None, './book/')
    #get num topics.  
    numtopics = 0
    self.alltopics = {}
    for c in book:
      if (c['type']=='**'):
        if (c['cmd'] not in self.alltopics):
          self.alltopics[c['cmd']] = []
        self.alltopics[c['cmd']].append(c)
        numtopics += 1

        self.topicarray.insert(0, c) #time reverse order
    if (numtopics > 0):
      self.selectedtopicindex = 0      
      self.selectedtopic = self.topicarray[self.selectedtopicindex] #default to first topic.

    logger.info(f'Loaded {numtopics} topics and {len(book)} book transcripts from ./book/')

    self.transcriber.allbooks = self.transcriber.open_books() #open book files for writing topics.
    logger.info('Loaded book files for writing topics.')
    logger.info(f'Books: {self.transcriber.allbooks}')
    #tree struct..
    #recurse through books and subbooks to get a list. 
    #array struct filter by time window and relevancy?  relevancy = topic search...
    self.filtered = self.transcriber.filter_books_recursive()
    logger.info(f'Filtered book struct: {self.filtered}')
    self.bookarray = self.transcriber.relevant_book_array(self.filtered) #get list of books for selection.
    logger.info(f'Book array: {self.bookarray}')
    #sort by recency
    self.bookarray.sort(key=lambda x: abs(self.timewindow.currenttime - x['..']), reverse=True) #sort by recency to current time, most recent first.

    if (len(self.bookarray) > 0):
      self.selectedbookindex = 0      
      self.selectedbook = self.bookarray[self.selectedbookindex] #default to first book.
      self.transcriber.set_current_book(self.selectedbook['**']) #set current book in transcriber for topic writing.

    self.bookhistory = self.bookarray[:100] #store last 100 books for quick access.
    #find last used language and latest topic..
    self.transcriber.set_current_topic()


    return 0

  def load_booktopicarray(self):
    #load topics for selected book into booktopicarray.  
    self.booktopicarray = []
    if (self.selectedbook is not None):
      if (self.selectedbook['**'] in self.transcriber.langmap):
        bookdata = self.transcriber.langmap[self.selectedbook['**']]
        if ('&&' in bookdata and bookdata['&&'] is not None and bookdata['('] != bookdata[')']):
          self.booktopicarray = bookdata['&&'][bookdata['(']:bookdata[')']+1]
          for c in self.booktopicarray:
            if (c['type']=='**'):
              if (c['cmd'] not in self.alltopics):
                self.alltopics[c['cmd']] = []
              self.alltopics[c['cmd']].append(c)

              self.booktopicarray.insert(0, c) #time reverse order
          self.booktopicarray.sort(key=lambda x: abs(self.timewindow.currenttime - x['timestamp']), reverse=True) #sort by recency to current time, most recent first.  

  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
         "Pause": [48,49], #pause video
        #48, 52 FIND?  
        "Tick": [48,53], #manual tick forward in time by small increments.
        "Tock": [48,54], #manual tick backward in time by small increments.
      },
      "3": {
        "Start": [48,60,61], #Start/resume recording
        "Help": [48,60,49], #show help
        #48, 51 TOPIC
        "List Topics": [48,51,54], #list topics
        "Select Topic": [48,51,55], #select topic
        "Set Topic": [48,51,56], #set topic with voice command

        #48, 52 BOOK
        "List Books": [48,52,54], #list books
        "Select Book": [48,52,55], #select book
        "Set Book": [48,52,56], #set book with voice command
        #48, 50 TIME
        "Set Speed": [48,50,54], #set speed of time
        "Time Jump": [48,50,52], #jump to time 
        "Time Zoom": [48,50,53], #set zoom, separate from speed.  
        #48,55 Adjust display?
        "Tune Time": [48,55,50], #time display, zoom level temporary?  tick quant?
        "Tune Topic": [48,55,51], #topic display show in main?  
        "Tune Book": [48,55,52], #book display show in main?
        "Tune In": [48,55,56], #main display, show time/topic/book or other info?
        "Tune Out": [48,55,54], #audio volume/mute or other info?
      }
    }
    if (self.name in self.config['languages']):
      logger.info(f'Merging existing {self.name} config')
      #need logic to iterate and pick each one.  This is not working right.  
      default.update(self.config['languages'][self.name])
    else:
      logger.info(f'No existing {self.name} config found, creating new one')

    self.config['languages'][self.name] = default
    self.funcdict = {
      "Pause": "pause",
      "Start": "start",
      "Help": "help",
      "List Topics": "list_topics",
      "Select Topic": "select_topic",
      "Set Topic": "set_topic", #smart search of existing topics?  
      "_Set Topic": "_set_topic", #smart search of existing topics?
      "List Books": "list_books",
      "Select Book": "select_book",
      "Set Book": "set_book",
      "_Set Book": "_set_book",
      "Set Speed": "set_speed",
      "Time Jump": "time_jump",
      "Time Zoom": "time_zoom", 
      "Tick": "tick",
      "Tock": "tock",
      "Tune In": "tune_in",
      "Tune Out": "tune_out",
    }
    self.helpdict = {
      "Start": {
"> ": "start", 
"$$": "None", 
"&&": "Start/Resume video recording."},
      "Help": {
"> ": "help", 
"$$": "None", 
"&&": "Show video commands."},
      "Pause": {
"> ": "pause", 
"$$": "None", 
"&&": "Pause video playback."},
      "List Topics": {
"> ": "list topics", 
"$$": "None", 
"&&": "List available topics."},
      "Select Topic": {
"> ": "select topic", 
"$$": "$index", 
"&&": "Select topic by index from list."},
      "Set Topic": {
"> ": "set topic", 
"$$": "$topic", 
"&&": "Set topic by name."},
      "List Books": {
"> ": "list books", 
"$$": "None", 
"&&": "List available books."},
      "Select Book": {
"> ": "select book", 
"$$": "$index", 
"&&": "Select book by $index from list."},
      "Set Book": {
"> ": "set book", 
"$$": "&book", 
"&&": "Set book by name."},
      "Set Speed": {
"> ": "set speed", 
"$$": "$value", 
"&&": "Set playback speed, relative to current."}, 
      "Time Jump": {
"> ": "time jump", 
"$$": "$time", 
"&&": "Jump to specific time."},
      "Time Zoom": {
"> ": "time zoom", 
"$$": "$level", 
"&&": "Set zoom level of time."},
      "Tick": {
"> ": "tick", 
"$$": "None", 
"&&": "Manually tick forward in time by small increments."},
      "Tock": {
"> ": "tock", 
"$$": "None", 
"&&": "Manually tick backward in time by small increments."},
      "Tune In": {
"> ": "tune in", 
"$$": "$lang", 
"&&": "Tune in display to $lang.."},
      "Tune Out": {
"> ": "tune out", 
"$$": "$lang", 
"&&": "Tune out display to $lang.."},
                       
    }

    self.load_transcript()
    return 0  

  #act differently based on words in sequence.    
  def act(self, cmd, words=[], sequence=[], doact=True):
    """ACT based on command and sequence."""
    if (not doact):
      if (len(sequence) == 1 and sequence[-1] == self.keybot):
        return 0
      elif (len(sequence) > 1 and sequence[-2:] == [self.keybot, self.keybot]):
        return 0
      else:
        return 1 #need more keys.

    logger.info("-> "+ cmd + " " + str(sequence))
    if (len(sequence) == 0 and "_" + cmd in self.funcdict):
      #run prefix command
      logger.info("-_> "+ cmd + " " + str(sequence))
      func = self.funcdict["_" + cmd]
      if hasattr(self, func):
        return getattr(self, func)(sequence)
      
    elif cmd in self.funcdict:
      logger.info("--> "+ cmd + " " + str(sequence))
      func = self.funcdict[cmd]
      #all require keybot at end.

      #this function called every time a key is pressed.


      if hasattr(self, func + "_"):
        #no return here..
        if getattr(self, func + "_")(sequence) > 0:
          #no function, run sequence through mk.key
          a = 0
        else:
          logger.info(f'--> {func}_')
          if (len(sequence) == 1 and sequence[-1] == self.keybot):
            a = 0 #continue logic and see if we need to end.  
          elif (len(sequence) > 1 and sequence[-2:] == [self.keybot, self.keybot]):
            a = 0 #continue logic and see if we need to end.
          else:
            return -len(sequence)-1 #indicate handled, can look for other words from what position

      if hasattr(self, func):
        if (len(sequence) == 1 and sequence[-1] == self.keybot):
          return getattr(self, func)(sequence[:-1])
        elif (len(sequence) > 1 and sequence[-2:] == [self.keybot, self.keybot]):
          return getattr(self, func)(sequence[:-2])
        else:
          return 1 #need more keys.
      else:
        logger.error(f"Function {func} not found in {self.__class__.__name__}")



      
    else:
      print(f"{self.funcdict}")
      logger.info(f"{self.funcdict}")
      logger.error(f"Command {cmd} not found in function maps")
      print(f"Command {cmd} not found in function maps")
    return -1
  

  def start(self, sequence=[]):
    """Start Meta."""
    logger.info(f'> Start {sequence}')
    return 0
  
  def help(self, sequence=[]):
    """Show all commands."""
    logger.info(f'> Help {sequence}')
    return 0


  def tick(self, sequence=[]):
    logger.info(f'> Tick {sequence}')
#    t = self.timewindow.tick(self.speed)
    self.set_qr("Tick", {'TIME': self.timewindow.getTime(), 'SPEED': self.speed})
    return 0


  def tock(self, sequence=[]):
    logger.info(f'> Tock {sequence}')
#    t = self.timewindow.tick(-self.speed)
    self.set_qr("Tock", {'TIME': self.timewindow.getTime(), 'SPEED': -self.speed})
    return 0

  def set_speed(self, sequence=[]):
    logger.info(f'> Set Speed {sequence}')
    if (len(sequence) > 0):
      adjust = float(sequence[-1] - self.mid) / 5.0 #just use 10 keys for mid..
      if (adjust <= 0.2):
        adjust = 0.2
      if adjust > 5:
        adjust = 5
      self.speed *= adjust
      self.speed = round(self.speed)
      if (self.speed < 1):
        self.speed = 1
      logger.info(f'$$SPEED={self.speed}')
      self.set_qr("Set Speed", {'ADJUST': adjust, 'SPEED': self.speed})
    return 0

  def time_jump(self, sequence=[]):
    logger.info(f'> Time Jump {sequence}')
    jump = 1 #default jump level
    if (len(sequence) > 0):
      jump = float(sequence[-1] - self.keybot) - 6 #just use 10 keys for mid..
    t = self.timewindow.timeJump(jump)
    vars = {}
    logger.info(f'$$TIME={t}')
    self.set_qr("Time Jump", {'JUMP': jump, 'WINDOW': self.timewindow.window, 'TIME': t, 'START': self.timewindow.starttime, 'END': self.timewindow.endtime})
    return 0
  
  def time_zoom_(self, sequence=[]):
    #list similar items based on current time window.  
    logger.info(f'> Time Zoom_ {sequence}')
    self.func = "Time Zoom_"
    vars = {}
    similar = -1
    if (len(sequence) > 0):
      if (sequence[-1] >= self.keybot + 12): #if we go above keybot + 12, we can show similar items based on current time window.  
        similar = sequence[-1] - (self.keybot + 12)
        vars['SIMILAR'] = similar
    self.set_qr(self.func, vars)
    return 1
  
  def time_zoom(self, sequence=[]):
    logger.info(f'> Time Zoom {sequence}')
    zoom = 2.0 #default zoom level
    similar = -1
    if (len(sequence) > 0):
      zoom = float(sequence[-1] - self.keybot) - 6 #use 6 keys above keybot for zoom levels, so we have some negative and positive levels.
      if (zoom >= 6): #next octave, pick from similar items if exist..
        similar = sequence[-1] - (self.keybot + 12)
        zoom = 0 #just use same zoom level for similar items

      if zoom >= 0:
        zoom = pow(2, zoom) #exponential zoom for more range. max 64x
      else:
        zoom = pow(2, zoom) #exponential zoom for more range. min 1/64x
    w = self.timewindow.timeZoom(zoom)
    vars = {}
    logger.info(f'$$TIMEWINDOW={w}')
    vars['ZOOM'] = zoom
    vars['WINDOW'] = w
    vars['TIME'] = self.timewindow.getTime()
    vars['START'] = self.timewindow.starttime
    vars['END'] = self.timewindow.endtime
    if (similar >= 0):
      vars['SIMILAR'] = similar
    self.set_qr("Time Zoom", vars)


    return 0


  def list_topics(self, sequence=[]):
    logger.info(f'> List Topics {sequence}')
    #for now just demo..
    #list all topics from book transcripts.

    return 0

  def adjust_topic_index(self, idx):
    if idx+self.selectedtopicindex < 0:
      return 0
    elif (idx+self.selectedtopicindex) >= len(self.topicarray):
      return len(self.topicarray)-1
    else:
      return self.selectedtopicindex + idx

  def adjust_filteredtopic_index(self, idx):
    if idx+self.selectedfilteredtopicindex < 0:
      return 0
    elif (idx+self.selectedfilteredtopicindex) >= len(self.filteredtopicarray):
      return len(self.filteredtopicarray)-1
    else:
      return self.selectedfilteredtopicindex + idx
    
  def adjust_filteredbook_index(self, idx):
    if idx+self.selectedfilteredbookindex < 0:
      return 0
    elif (idx+self.selectedfilteredbookindex) >= len(self.filteredbookarray):
      return len(self.filteredbookarray)-1
    else:
      return self.selectedfilteredbookindex + idx
    
  def adjust_book_index(self, idx):
    if idx+self.selectedbookindex < 0:
      return 0
    elif (idx+self.selectedbookindex) >= len(self.bookarray):
      return len(self.bookarray)-1
    else:
      return self.selectedbookindex + idx


  def get_book_context(self, book, num=5):
    #get context for book from book transcripts.  
    ret = f"**{book}\n"
    if (book in self.transcriber.langmap):
      bookcmds = []
      bookdata = self.transcriber.langmap[book]
      if ('&&' in bookdata and bookdata['&&'] is not None and bookdata['('] != bookdata[')']):
        bookcmds = bookdata['&&'][bookdata['(']:bookdata[')']+1]
      bookcmds.sort(key=lambda x: abs(self.timewindow.currenttime - x['timestamp']), reverse=True) #sort by recency to current time, most recent first.

      sortedcmds = bookcmds[:num]
      sortedcmds.sort(key=lambda x: x['timestamp']) #sort by time for display.

      for cmd in sortedcmds:
        ret += f'$${datetime.fromtimestamp(cmd["timestamp"]).strftime("%Y%m%d_%H%M%S")}\n'
        ret += '\n'.join(cmd['lines']) + "\n"
    return ret

  def get_context(self, topic, num=5):
    #get context for topic from book transcripts.  
    ret = f"**{topic}\n"
#    if topic in self.alltopics:
#      topiccmds = self.alltopics[topic]
    if (topic in self.transcriber.langmap[self.name]['topics']):
      topicdata = self.transcriber.langmap[self.name]['topics'][topic]
      if 'data' in topicdata:
        topiccmds = topicdata['data']
      topiccmds.sort(key=lambda x: abs(self.timewindow.currenttime - x['timestamp']), reverse=True) #sort by recency to current time, most recent first.
      sortedcmds = topiccmds[:num]
      sortedcmds.sort(key=lambda x: x['timestamp']) #sort by time for display.
      context = []
      for cmd in sortedcmds:
        ret += f'$${datetime.fromtimestamp(cmd["timestamp"]).strftime("%Y%m%d_%H%M%S")}\n'
        ret += '\n'.join(cmd['lines']) + "\n"
    return ret
    

  def select_topic_(self, sequence=[]):

    logger.info(f'> Select Topic_ {sequence}')
    print("> Select Topic_")
    newidx = self.selectedtopicindex
    if (len(sequence) > 0):
      if (sequence[-1] == self.keybot): #dont adjust if keybot, 
        return 1
      newidx = self.adjust_topic_index(self.mid-sequence[-1])
    logger.info(f'--{self.topicarray[newidx]['**']}')
    self.func = "Select Topic_"
    #should make this more general.. send last ten links
    last15 = self.topicarray[max(0, self.selectedtopicindex-11):min(self.selectedtopicindex+13, len(self.topicarray))]
    last15.reverse() #reverse to match with Future:Past order in display.. [48 - 68]
    #does this match up with keys?  
    vars = {}
    vars['topic'] = self.topicarray[newidx]['**']
    ctxt = self.get_context(self.topicarray[newidx]['**'], 5) #get context for topic
    vars['context'] = ctxt.replace('\n', '<br>')

    start = 0
#    if self.selectedtopicindex < 12:
#      start = 12 - self.selectedtopicindex
    for i, l in enumerate(last15):
      i = i + start
      vars[f'{i}'] = l['**']
#          vars[f'href{i}'] = l['href']
    vars['idx'] = newidx
    self.set_qr(self.func, vars)

#    self.speak(f'{vars["topic"]}')
    
    return 1
    #scroll up or back?  
    #list most likely topics based on recency and relevance to current topic.

  def select_topic(self, sequence=[]):
    selected = 0
    if (len(sequence) > 0):
      selected = self.mid - sequence[-1]

    self.selectedtopicindex = self.adjust_topic_index(selected)
    self.selectedtopic = self.topicarray[self.selectedtopicindex] if self.selectedtopicindex < len(self.topicarray) else None
    if (len(self.topichistory) < 1 or self.selectedtopic['**'] != self.topichistory[-1]['**'] or self.selectedtopic['..'] != self.topichistory[-1]['..']):
      self.topichistory.insert(0, self.selectedtopic)

    ctxt = self.get_context(self.topicarray[self.selectedtopicindex]['**'], 5) #get context for topic
    logger.info(f'> Select Topic {sequence}')
    #get bookmark at index selected
    self.func = "Select Topic"
    self.set_qr(self.func, {'context': ctxt.replace('\n', '<br>'), 'topic': self.selectedtopic['**']})
#    logger.info(ctxt.replace('\n', '<br>'))
    #keep track of topic history..
    writtentopic = self.transcriber.write_topic(self.name, self.selectedtopic['**']) #write topic to _meta.. to pick up in other tools.  
    self.transcriber.write_topic(self.name, self.selectedtopic['**'], ctxt) #write topic context?  Get latest info for robot.. trigger read of this file..
    self.speak(f'{self.selectedtopic['**']}')
    self.transcript = writtentopic #set transcript here to include into midi.  Dont include context for now too much repetition..
    return 0

  def set_topic_(self, sequence=[]):

    logger.info(f'> Set Topic_ {sequence}')
    print("> Set Topic_")

    if (len(sequence) == 1):
      from extensions.trey.speech import transcribe_audio, transcribe_audio_whisper
      self.transcript = transcribe_audio_whisper("topic.wav")

      logger.info('$$AUDIO = ' + self.transcript)
    if (len(sequence) == 2):
      #stop recording..
      if (sequence[-1] == sequence[-2]):
        #dont refilter..  
        if (len(self.filteredtopicarray) > 0):
          self.transcript = "" #skip refilter if double press, just repeat same options.
      if (self.transcript != ""):
        self.filtertopic = self.transcript
        self.selectedfilteredtopicindex = 0

      #sort topics by relevance to filtertopic.. this is just a demo of filtering, we can do more complex filtering based on topics, time, etc.
      self.filteredtopicarray = self.transcriber.relevant_topic_array(self.name, self.filtertopic, self.timewindow.currenttime) #get list of topics for selection.
      logger.info(f'Filtered topic array: {self.filteredtopicarray}')
      #sort by recency
      self.filteredtopicarray.sort(key=lambda x: abs(self.timewindow.currenttime - x['timestamp']), reverse=True) #sort by recency to current time, most recent first.
    
    if (len(sequence) > 2):
      newidx = self.selectedfilteredtopicindex
      if (sequence[-1] == self.keybot): #dont adjust if keybot, 
        return 1
      newidx = self.adjust_filteredtopic_index(self.mid-sequence[-1])
      logger.info(f'--{self.filteredtopicarray[newidx]['topic']}')
      self.func = "Set Topic_"
      #should make this more general.. send last ten links
      last15 = self.filteredtopicarray[max(0, self.selectedfilteredtopicindex-11):min(self.selectedfilteredtopicindex+13, len(self.filteredtopicarray))]
      last15.reverse() #reverse to match with Future:Past order in display.. [48 - 68]
      #does this match up with keys?  
      vars = {}
      vars['topic'] = self.filteredtopicarray[newidx]['topic']
      ctxt = self.get_context(self.filteredtopicarray[newidx]['topic'], 5) #get context for topic
      vars['context'] = ctxt.replace('\n', '<br>')

      start = 0
  #    if self.selectedtopicindex < 12:
  #      start = 12 - self.selectedtopicindex
      for i, l in enumerate(last15):
        i = i + start
        vars[f'{i}'] = l['topic']
  #          vars[f'href{i}'] = l['href']
      vars['idx'] = newidx
      self.set_qr(self.func, vars)

#    self.speak(f'{vars["topic"]}')
    
    return 1

  def set_topic(self, sequence=[]):
    logger.info(f'> Set Topic {sequence}')
    selected = 0
    if (len(sequence) > 0):
      selected = self.mid - sequence[-1]

    self.selectedfilteredtopicindex = self.adjust_filteredtopic_index(selected)
    self.selectedtopic = self.filteredtopicarray[self.selectedfilteredtopicindex] if self.selectedfilteredtopicindex < len(self.filteredtopicarray) else None
    #find this in the main topic array..
    if self.selectedtopic is not None:
      for i, t in enumerate(self.topicarray):
        if t['**'] == self.selectedtopic['**'] and self.selectedtopic['..'] == t['..']: #match topic and time
          self.selectedtopicindex = i
          break
    #set transcriber selected topic for further writing..
    self.transcriber.current_topic = self.selectedtopic['**'] if self.selectedtopic is not None else self.transcriber.current_topic
    if (len(self.topichistory) < 1 or self.selectedtopic != self.topichistory[-1]):
      #not sure if we want to remove earlier instances..
      self.topichistory.insert(0, self.selectedtopic)

    ctxt = self.get_topic_context(self.topicarray[self.selectedtopicindex]['**'], 5) #get context for topic
    logger.info(f'> Set Topic {sequence}')
    #get bookmark at index selected
    self.func = "Set Topic"
    self.set_qr(self.func, {'context': ctxt.replace('\n', '<br>'), 'topic': self.selectedtopic['**']})
#    logger.info(ctxt.replace('\n', '<br>'))
    #keep track of topic history..
    writtentopic = self.transcriber.write_topic(self.name, self.selectedtopic['**']) #write topic to _meta.. to pick up in other tools.  
    self.transcriber.write_topic(self.name, self.selectedtopic['**'], ctxt) #write temp topic context?  Get latest info for robot.. trigger read of this file..
    self.speak(f'{self.selectedtopic["**"]}')
    self.transcript = writtentopic #set transcript here to include into midi.  Dont include context for now too much repetition..
    return 0


  def _set_topic(self, sequence=[]):  
    logger.info(f'> _Set Topic {sequence}')
    print("> _Set Topic called")
    #get audio input for query.  
    from extensions.trey.speech import listen_audio
    at = listen_audio(5, "topic.wav")
    #but this is only called once.  
    return 1




  def list_books(self, sequence=[]):
    logger.info(f'> List Books {sequence}')
    #for now just demo..
    #list all books from current reference folder.

    return 0

  #not implemented yet, show list of books based on recency..
  def select_book_(self, sequence=[]):

    logger.info(f'> Select Book_ {sequence}')
    print("> Select Book_")

    newidx = self.selectedbookindex
    if (len(sequence) > 0):
      if (sequence[-1] == self.keybot): #dont adjust if keybot, 
        return 1
      newidx = self.adjust_book_index(self.mid-sequence[-1])
    logger.info(f'--{self.bookarray[newidx]["**"]}')
    self.func = "Select Book_"
    #should make this more general.. send last ten links
    last15 = self.bookarray[max(0, self.selectedbookindex-11):min(self.selectedbookindex+13, len(self.bookarray))]
    last15.reverse() #reverse to match with Future:Past order in display.. [48 - 68]
    #does this match up with keys?  
    vars = {}
    vars['book'] = self.bookarray[newidx]['**']
    ctxt = self.get_book_context(self.bookarray[newidx]['**'], 5) #get context for book
    vars['context'] = ctxt.replace('\n', '<br>')

    start = 0
#    if self.selectedtopicindex < 12:
#      start = 12 - self.selectedtopicindex
    for i, l in enumerate(last15):
      i = i + start
      vars[f'{i}'] = l['**']
#          vars[f'href{i}'] = l['href']
    vars['idx'] = newidx
    self.set_qr(self.func, vars)

#    self.speak(f'{vars["topic"]}')
    
    return 1
    #scroll up or back?  
    #list most likely topics based on recency and relevance to current topic.

  def select_book(self, sequence=[]):
    selected = 0
    if (len(sequence) > 0):
      selected = self.mid - sequence[-1]

    self.selectedbookindex = self.adjust_book_index(selected)
    self.selectedbook = self.bookarray[self.selectedbookindex] if self.selectedbookindex < len(self.bookarray) else None
    #set transcriber selected book for further writing..
    self.transcriber.current_book = self.selectedbook['**'] if self.selectedbook is not None else self.transcriber.current_book
    if (len(self.bookhistory) < 1 or self.selectedbook != self.bookhistory[-1]):
      self.bookhistory.insert(0, self.selectedbook)

    ctxt = self.get_book_context(self.bookarray[self.selectedbookindex]['**'], 5) #get context for book
    logger.info(f'> Select Book {sequence}')
    #get bookmark at index selected
    self.func = "Select Book"
    self.set_qr(self.func, {'context': ctxt.replace('\n', '<br>'), 'book': self.selectedbook['**']})
#    logger.info(ctxt.replace('\n', '<br>'))
    #keep track of topic history..
    writtentopic = self.transcriber.write_topic(self.name, self.selectedbook['**']) #write topic to _meta.. to pick up in other tools.  
    self.transcriber.write_topic(self.name, self.selectedbook['**'], ctxt) #write temp topic context?  Get latest info for robot.. trigger read of this file..
    self.speak(f'{self.selectedbook["**"]}')
    self.transcript = writtentopic #set transcript here to include into midi.  Dont include context for now too much repetition..
    return 0


  def set_book_(self, sequence=[]):
    logger.info(f'> Set Book_ {sequence}')
    print("> Set Book_ called")
    if (len(sequence) == 1):
      #stop recording..
      from extensions.trey.speech import transcribe_audio, transcribe_audio_whisper
      self.transcript = transcribe_audio_whisper("book.wav")

    if (len(sequence) == 2):
      if (sequence[-1] == sequence[-2]):
        #dont refilter..  
        if (len(self.filteredtopicarray) > 0):
          self.transcript = "" #skip refilter if double press, just repeat same options.
      #otherwise get filter..

      logger.info('$$AUDIO = ' + self.transcript)
      if (self.transcript != ""):
        filterbook = self.transcript
        self.selectedfilteredbookindex = 0
        #sort books by relevance to filterbook.. this is just a demo of filtering, we can do more complex filtering based on topics, time, etc.
        self.filteredbookarray = self.transcriber.relevant_book_array(self.filtered, filterbook) #get list of books for selection.
        logger.info(f'Filtered book array: {self.filteredbookarray}')
        #sort by recency
        self.filteredbookarray.sort(key=lambda x: abs(self.timewindow.currenttime - x['..']), reverse=True) #sort by recency to current time, most recent first.
    
    if (len(sequence) > 2):
      #get audio input for query.  
      newidx = self.selectedfilteredbookindex
      if (sequence[-1] == self.keybot): #dont adjust if keybot, 
        return 1
      newidx = self.adjust_filteredbook_index(self.mid-sequence[-1])
      logger.info(f'--{self.filteredbookarray[newidx]["**"]}')
      self.func = "Set Book_"
      #should make this more general.. send last ten links
      last15 = self.filteredbookarray[max(0, self.selectedfilteredbookindex-11):min(self.selectedfilteredbookindex+13, len(self.filteredbookarray))]
      last15.reverse() #reverse to match with Future:Past order in display.. [48 - 68]
      #does this match up with keys?  
      vars = {}
      vars['book'] = self.filteredbookarray[newidx]['**']
      ctxt = self.get_book_context(self.filteredbookarray[newidx]['**'], 5) #get context for book
      vars['context'] = ctxt.replace('\n', '<br>')

      start = 0
  #    if self.selectedtopicindex < 12:
  #      start = 12 - self.selectedtopicindex
      for i, l in enumerate(last15):
        i = i + start
        vars[f'{i}'] = l['**']
  #          vars[f'href{i}'] = l['href']
      vars['idx'] = newidx
      self.set_qr(self.func, vars)

    return 1
  #no good way to set book currently, too hard for audio input..  


  def set_book(self, sequence=[]):
    logger.info(f'> Set Book {sequence}')
    selected = 0
    if (len(sequence) > 0):
      selected = self.mid - sequence[-1]

    self.selectedfilteredbookindex = self.adjust_filteredbook_index(selected)
    self.selectedbook = self.filteredbookarray[self.selectedfilteredbookindex] if self.selectedfilteredbookindex < len(self.filteredbookarray) else None
    #find this in the main book array..
    if self.selectedbook is not None:
      for i, b in enumerate(self.bookarray):
        if b['**'] == self.selectedbook['**']:
          self.selectedbookindex = i
          break
    #set transcriber selected book for further writing..
    self.transcriber.current_book = self.selectedbook['**'] if self.selectedbook is not None else self.transcriber.current_book
    if (len(self.bookhistory) < 1 or self.selectedbook != self.bookhistory[-1]):
      #not sure if we want to remove earlier instances..
      self.bookhistory.insert(0, self.selectedbook)

    ctxt = self.get_book_context(self.bookarray[self.selectedbookindex]['**'], 5) #get context for book
    logger.info(f'> Set Book {sequence}')
    #get bookmark at index selected
    self.func = "Set Book"
    self.set_qr(self.func, {'context': ctxt.replace('\n', '<br>'), 'book': self.selectedbook['**']})
#    logger.info(ctxt.replace('\n', '<br>'))
    #keep track of topic history..
    writtentopic = self.transcriber.write_topic(self.name, self.selectedbook['**']) #write topic to _meta.. to pick up in other tools.  
    self.transcriber.write_topic(self.name, self.selectedbook['**'], ctxt) #write temp topic context?  Get latest info for robot.. trigger read of this file..
    self.speak(f'{self.selectedbook["**"]}')
    self.transcript = writtentopic #set transcript here to include into midi.  Dont include context for now too much repetition..
    return 0

  def _set_book(self, sequence=[]):  
    logger.info(f'> _Set Book {sequence}')
    print("> _Set Book called")
    #get audio input for query.  
    from extensions.trey.speech import listen_audio
    at = listen_audio(5, "book.wav")
    #but this is only called once.  
    return 1

  def pause(self, sequence=[]):
    """Pause Video."""
    logger.info(f'> Pause {sequence}')
    return 0


  def tune_in(self, sequence=[]):
    logger.info(f'> Tune In {sequence}')
    lang = "ALL"

    if (len(sequence) > 0):
      #for now just use single key for language selection, can expand to more complex selection later.
      #i.e. just get commands which start with this sequence..
      #command lookup from lang index.
      langindex = sequence[-1]-self.keybot
      for (l, v) in enumerate(self.config['keymap']['languages']):
        if (v[0] == langindex+self.keybot): #for now..
          lang = l
          break
    self.set_qr("Tune In", {'LANG': lang,'WINDOW': self.timewindow.window, 'TIME': self.timewindow.getTime(), 'START': self.timewindow.starttime, 'END': self.timewindow.endtime})
    return 0

  def tune_out(self, sequence=[]):
    logger.info(f'> Tune Out {sequence}')
    lang = "ALL"

    if (len(sequence) > 0):
      #for now just use single key for language selection, can expand to more complex selection later.
      #i.e. just get commands which start with this sequence..
      #command lookup from lang index.
      langindex = sequence[-1]-self.keybot
      for (l, v) in enumerate(self.config['keymap']['languages']):
        if (v[0] == langindex+self.keybot): #for now..
          lang = l
          break

    self.set_qr("Tune Out", {'LANG': lang,'WINDOW': self.timewindow.window, 'TIME': self.timewindow.getTime(), 'START': self.timewindow.starttime, 'END': self.timewindow.endtime})
    return 0

  def set_qr(self, func, param={}):
    """Set QR."""
    self.qr = "> " + func + "\n"
    for k,v in param.items():
        self.qr += f"$${k}={v}\n"
    self.qr += "$$\n"
    return 0  
  

  def speak(self, text, links=[]):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    return speak(text, links)

  
