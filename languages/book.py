import logging
import languages.helpers.timewindow as timewindow

from PIL import Image
from io import BytesIO
import win32con
import time
from datetime import datetime, timedelta
import shutil

import languages.helpers.transcriber as transcriber
#from server.login.app import index


logger = logging.getLogger(__name__)

class book:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.transcriber = transcriber.transcriber(self) #current_topic set by mykeys for now
    self.current_topic = None #set by mykeys
    self.qapp = qapp
    self.func = None
    self.cmd = None
    self.qr = "" #info for QR message
    self.qrin = "" #info from incoming QR message
    self.startx = startx
    self._bbox = [0,0,0,0] #for now just use this for all functions that need a bbox.  This is left, top, right, bottom.  We can also use this for screen toggle to indicate where the screen overlay should be.
    self.bbox = [100,200,100,200]   
    self.bbox_aftertouch = [400,500,400,500] #just start here, or from last bbox.  Load from settings..
    self.geo = None
    self.name = "book"
    self.keybot = 50 #
    self.mid = 60 #middle C for bbox calc
    self.keyoffset = 2 #offset within octave mapping
    self.links = []
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.transcript = ""
    self.feedbacknowstr = ""
    self.funcdict = {}
    self.suggestions = []
    self.transcripthistory = [] #store past transcripts for context.  This is not currently used for anything but could be used for context in future functions.
    self.topichistory = [] #store past topics for context.  This is not currently used for anything but could be used for context in future functions.
    self.links = [] #currently selected link structure from page..
    self.timewindow = timewindow.timewindow(self) #for timeline functions, can also be used for general time tracking.  This is initialized here but can be reset by timeline if needed.
    self.bookmarks = {} #bookname: index in bookcontext
    self.lastcacheno = 100


  def word(self, sequence=[]):
    """Word lookup."""
    
    cmd = ""
    sl = str(len(sequence))
    if (sl in self.config['languages'][self.name]):
      logger.info(f'Looking up sequence {sequence} in <<book>>')
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
  
  def load(self):
    #load language specific data
     #config overrides load_data by default.  
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
    #load commands from config into funcdict

    #load 6 months of book topics..
    book = self.transcriber.read(self.name, self.transcriber.getTime(-180), None, './book/')
    logger.info(f'Loaded {len(book)} book transcripts from ./book/')    


    return 0
  
  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
         "Pause": [50,49], #pause check
         "Unpause": [50,51], #unpause check
      },
      "3": {
        "Help": [50,52,51], #show help for check commands
        "Comment": [50,54, 55], #record comment
        "Select Book": [50,54,57], #open topic
        "Select Topic": [50,53,57], #open topic

      },
    }
    if (self.name in self.config['languages']):
      logger.info(f'Merging existing {self.name} config')
      #need logic to iterate and pick each one.  This is not working right.  
      default.update(self.config['languages'][self.name])
    else:
      logger.info(f'No existing {self.name} config found, creating new one')

    self.config['languages'][self.name] = default
    self.funcdict = {
      "Comment": "comment",
      "Help": "help",
      "Pause": "pause",
      "Unpause": "unpause",
      "Select Book": "select_book",
      "Select Topic": "select_topic",
      "Set Book": "set_book",

    }
    self.helpdict = {
      "Comment": {"help": "comment", "params": "None", "desc": f"Add comment to {self.name} timeline."},
      "Help": {"help": "help", "params": "None", "desc": f"Show {self.name} commands."},
      "Pause": {"help": "pause", "params": "None", "desc": f"Pause {self.name} playback."},
      "Unpause": {"help": "unpause", "params": "None", "desc": f"Unpause {self.name} playback."},
      "Select Book": {"help": "select_book", "params": "None", "desc": f"Open current book in {self.name}."},
      "Select Topic": {"help": "select_topic", "params": "None", "desc": f"Open current topic in {self.name}."},
      "Set Book": {"help": "set book [book]", "params": "[book]", "desc": "Set book by name."},

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
  

  def get_book_context(self, book, num=5):
    #get context for book from book transcripts.  
    ret = f"**{book}\n"
    logger.info(f'Getting context for book {book}')

    if (book in self.transcriber.langmap):
      bookcmds = []
      bookdata = self.transcriber.langmap[book]
      if ('&&' in bookdata and bookdata['&&'] is not None and bookdata['('] != bookdata[')']):
        bookcmds = bookdata['&&'][bookdata['(']:bookdata[')']+1]
      bookcmds.sort(key=lambda x: abs(self.timewindow.currenttime - x['timestamp']), reverse=True) #sort by recency to current time, most recent first.
      logger.info(f'Found {len(bookcmds)} commands for book {book} during time window {self.timewindow.currenttime} +/- {self.timewindow.window }')
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
    logger.info(f'--{self.topicarray[newidx]}')
    self.func = "Select Topic_"
    #should make this more general.. send last ten links
    last15 = self.topicarray[max(0, self.selectedtopicindex-11):min(self.selectedtopicindex+13, len(self.topicarray))]
    last15.reverse() #reverse to match with Future:Past order in display.. [48 - 68]
    #does this match up with keys?  
    vars = {}
    vars['topic'] = self.topicarray[newidx]
    ctxt = self.get_context(self.topicarray[newidx], 5) #get context for topic
    vars['context'] = ctxt.replace('\n', '<br>')

    start = 0
#    if self.selectedtopicindex < 12:
#      start = 12 - self.selectedtopicindex
    for i, l in enumerate(last15):
      i = i + start
      vars[f'{i}'] = l
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
    if (len(self.topichistory) < 1 or self.selectedtopic != self.topichistory[-1]):
      self.topichistory.insert(0, self.selectedtopic)

    ctxt = self.get_context(self.topicarray[self.selectedtopicindex], 5) #get context for topic
    logger.info(f'> Select Topic {sequence}')
    #get bookmark at index selected
    self.func = "Select Topic"
    self.set_qr(self.func, {'context': ctxt.replace('\n', '<br>'), 'topic': self.selectedtopic})
#    logger.info(ctxt.replace('\n', '<br>'))
    #keep track of topic history..
    writtentopic = self.transcriber.write_topic(self.name, self.selectedtopic) #write topic to _meta.. to pick up in other tools.  
    self.transcriber.write_topic(self.name, self.selectedtopic, ctxt) #write topic context?  Get latest info for robot.. trigger read of this file..
    self.speak(f'{self.selectedtopic}')
    self.transcript = writtentopic #set transcript here to include into midi.  Dont include context for now too much repetition..
    return 0


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
      vars[f'{i}'] = l
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

  def comment_(self, sequence=[]):
    if (len(sequence) == 1):

      logger.info(f'> Comment_ {sequence}')

      print("> Comment_ called")
      #get audio input for query.  
      duration = sequence[0]-self.keybot #in seconds
      duration *=3  #double duration for feedback
      from extensions.trey.speech import listen_audio
      self.now = datetime.now()
      self.feedbacknowstr = self.now.strftime("%Y%m%d%H%M%S") #set nowstr for feedback.  

      at = listen_audio(duration, "comment.wav")
      #at.join() #wait for it to finish.
      #have to just use some keys until this is done.  
      #need to return 1 to indicate we need more keys.
      #but this is only called once.  

      return 0 #handled, this function will not be called again with further parameters.
    else:
      #get real-time input
      from extensions.trey.speech import transcribe_now
      self.func = "Comment_"
      self.transcript += transcribe_now() + "\n"
      self.set_qr(self.func, {'transcript': self.transcript})
      #update display.  
    return 1


  def comment(self, sequence=[]):
    logger.info(f'> Comment {sequence}')
    duration = sequence[0]-self.keybot if (len(sequence) > 0) else 5
    duration *=3  #triple duration for feedback
    print(f'> Comment for {duration} seconds')
    from extensions.trey.speech import transcribe_audio, get_duration, transcribe_audio_whisper, transcript_info
    timer = datetime.now()
#    self.transcript = transcribe_audio("feedback.wav")
    self.transcript = transcribe_audio_whisper("comment.wav") #try whisper for better accuracy.  This is slower but hopefully more accurate, especially for short feedback.


    dur = get_duration("comment.wav") #actual dynamic duration..
    if (dur == 0):
      duration = (timer - self.now).total_seconds() if self.now is not None else duration
    else:
      duration = dur

    lag = (datetime.now() - timer).total_seconds()
    lag = int(lag)
    print(f'Transcription completed in {lag} seconds: {self.transcript}')
    #get current line and previous line in case we are on a partial..
    #then find the most likely location from text.  
    #if we are reading a page, get current line of that page..

    if (len(self.transcript) > 0):
      self.transcripthistory.append(self.transcript)
      try:
        vars = {}
        vars['DURATION'] = duration
        vars['TRANSCRIPT'] = self.transcript
        vars['LANG'] = transcript_info['language'] if transcript_info is not None and 'language' in transcript_info else "unknown"
        fname = '../transcripts/' + self.name + '/' + self.feedbacknowstr + '.wav'
        vars['FILE'] = fname
        shutil.copy('comment.wav', fname) #keep a copy for training..
        self.transcriber.write(self.name, "Comment", vars)  
        self.set_qr("Comment", vars) #update QR with feedback data for debugging and record keeping.

      except Exception as e:
        print(f'Error writing feedback file: {e}')
    return 0
    


  #no good way to set book currently, too hard for audio input..  
  def set_book(self, sequence=[]):
    logger.info(f'> Set Book {sequence}')
    book = "Australian Open 2026"
    from extensions.trey.speech import transcribe_audio, transcribe_audio_whisper
    self.transcript = transcribe_audio_whisper("book.wav")

    logger.info('$$AUDIO = ' + self.transcript)
    if (self.transcript != ""):
      book = self.transcript
    from extensions.trey.trey import speak
    speak(f'Setting book: {book}')

    return 0


  def _set_book(self, sequence=[]):  
    logger.info(f'> _Set Book {sequence}')
    print("> _Set Book called")
    #get audio input for query.  
    from extensions.trey.speech import listen_audio
    at = listen_audio(5, "book.wav")
    #but this is only called once.  
    return 1


  def help(self, sequence=[]):
    """Show all commands."""
    logger.info(f'> Help {sequence}')
    return 0



  def pause(self, sequence=[]):
    """Pause Check."""
    logger.info(f'> Pause {sequence}')
    cacheno = -1
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot #first key cache selection

    if (cacheno < 0):
      cacheno = self.lastcacheno
    else:
      cacheno = 100 + cacheno
    
    existing_book = self.bookmarks.get(self.transcriber.current_book, None)
    ctxt = self.get_book_context(self.transcriber.current_book, 5) #get context for book
    link_data = self.get_links(ctxt)
    if (existing_book is None):
      existing_book = {'total_read': 0, 'links': link_data, 'cacheno': cacheno, 'context': ctxt, 'q2': None}
    else:
      q2 = existing_book['q2']
      cacheno = existing_book['cacheno']
      total_read = existing_book['total_read']
      if (q2 is not None):
        while (q2 is not None and not q2.empty()):
            total_read = q2.get() #get current link number.  
      existing_book['total_read'] = total_read

    #pause trey.  
    self.set_qr("Pause", {'type': 'book', 'cacheno': cacheno})
    return 0

  def unpause(self, sequence=[]):  
    """Unpause Check."""
    logger.info(f'> Unpause {sequence}')
    cacheno = -1
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot #first key cache selection

    if (cacheno < 0):
      cacheno = self.lastcacheno
      self.lastcacheno += 1
      if (self.lastcacheno > 120):
        self.lastcacheno = 100 #overwrite..
    else:
      cacheno = 100 + cacheno

    self.set_qr("Unpause", {'type': 'book', 'cacheno': cacheno})
    #get book context and read..
    existing_book = self.bookmarks.get(self.transcriber.current_book, None)
    ctxt = self.get_book_context(self.transcriber.current_book, 5) #get context for book
    link_data = self.get_links(ctxt)
    if (existing_book is None):
      existing_book = {'total_read': 0, 'links': link_data, 'cacheno': cacheno, 'context': ctxt, 'q2': None}
      self.bookmarks[self.transcriber.current_book] = existing_book
    elif (existing_book['context'] != ctxt):
        existing_book['links'] = link_data
        existing_book['context'] = ctxt
        existing_book['total_read'] = 0 #set back to 0 if context has changed, otherwise keep track of how much we have read for this book.
        #existing_book['cacheno'] = cacheno

    #dont overwrite cacheno if we already have one for this book, otherwise we lose track of it and cant pause again.
    q2, q3, stop_event = self.speak(ctxt, link_data, [], total_read=existing_book['total_read'], cacheno=existing_book['cacheno'])
    existing_book['q2'] = q2


    
    return 0

  def get_links(self, ctxt):
    """
    {
            href: link.href,
            text: link.innerText,
            bbox: {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height
            },
            index: index
        }
    """
    links = []
    lines = ctxt.split('\n')
    cmds = self.transcriber.read_lines(self.transcriber.current_book, lines)
    total_read = 0
    for cmd in cmds:
      if cmd['type'] == '**':
        bytes_read = 0
        print(f'{cmd}')
        links.append({'href': cmd['lines'][0], 'text': cmd['topic'], 'bbox': self.bbox, 'index': total_read})
        for line in cmd['lines']:
          bytes_read = len(line) +1 #+1 for newline
        total_read += bytes_read

    self.links = links
    return links

  

  def ar2str(self, arr):
    """Array to String."""
    string_elements = [str(x) for x in arr]
    single_string = ", ".join(string_elements)

    return single_string

  def qr_in(self, data):
    #handle incoming QR data for now just MPE aftertouch. 
    #used for internal comms as well.. should change queue for that..
    return 0



  def set_qr(self, func, param={}):
    """Set QR."""
    self.qr = "> " + func + "\n"
    for k,v in param.items():
        self.qr += f"$${k}={v}\n"
    self.qr += "$$\n"
    return 0  
  

  def speak(self, text, links=[], alt_text_data=[], total_read=0, lang="en", cacheno=-1):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    #really want to be able to turn on/off speaking with some setting similar to OPACITY..

    return speak(text, links, alt_text_data, total_read, lang, cacheno)

  
