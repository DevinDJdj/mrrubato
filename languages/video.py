import logging
from pynput import *
import pytesseract
from PIL import Image
from io import BytesIO
import win32con
import time
from datetime import datetime, timedelta
import shutil

import languages.helpers.transcriber as transcriber
import extensions.trey.playwrighty as playwrighty


logger = logging.getLogger(__name__)

class video:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.transcriber = None
    self.qapp = qapp
    self.func = None
    self.cmd = None
    self.qr = "" #info for QR message
    self.qrin = "" #info from incoming QR message
    self.startx = startx
    self._bbox = [0,0,0,0] #for now just use this for all functions that need a bbox.  This is left, top, right, bottom.  We can also use this for screen toggle to indicate where the screen overlay should be.
    self.bbox = [100,200,100,200]   
    self.bbox_aftertouch = [400,500,400,500] #just start here, or from last bbox.  Load from settings..
    self.opacity = 0.4
    self.speed = 1.0
    self.geo = None
    self.name = "video"
    self.keybot = 49 #
    self.mid = 60 #middle C for bbox calc
    self.keyoffset = 1 #offset within octave mapping
    self.links = []
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.transcript = ""
    self.feedbacknowstr = ""
    self.funcdict = {}
    self.suggestions = []

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

    return 0
  
  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
         "Pause": [49,48], #pause video
         "Unpause": [49,50], #unpause video/audio
         "Screen Toggle": [49,51], #show/hide screen overlay, param set opacity..
      },
      "3": {
        "Start": [49,61,62], #Start/resume recording
        "Stop": [49,61,60], #stop/pause recording
        "Help": [49,61,50], 
        "Set Speed": [49,52,56], #set speed of time
        "Comment": [49,53, 56], #record comment
        "Screenshot": [49,53,55], #take screenshot
        "Zoomshot": [49,53,57], #take zoomed screenshot
        "Next": [49, 53, 54], #next video in playlist or folder
      },
      "4": {
        "Screenshot Feedback": [49,53,55,53], #screenshot with feedback
        #old style recording commands..
        "Start Record": [49,56,57,56], #start record old style > ./record.py
        "Set Composer": [49,56,52,56], #set composer for recording find in DB
        "Select Composer": [49,56,53,56], #select composer for recording find in DB go through sequential..        
        "Set Song": [49,56,54,56], #select song for recording find in DB
        "Select Song": [49,56,55,56], #select song for recording find in DB go through sequential..
        "Toggle Screen Record": [49,56,51,56], #toggle screen display for recording
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
      "Stop": "stop",
      "Comment": "comment",
      "Start": "start",
      "Help": "help",
      "Pause": "pause",
      "Next": "next",
      "Unpause": "unpause",
      "Set Speed": "set_speed",
      "Screenshot": "screenshot",
      "_Screenshot": "_screenshot",
      "Zoomshot": "zoomshot",
      "Screen Toggle": "screen_toggle",
      "_Screenshot Feedback": "_screenshot_feedback",
      "Screenshot Feedback": "screenshot_feedback",
      "Screenshot Feedback_": "screenshot_feedback_",

      "Start Record": "start_record",
      "Set Composer": "set_composer",
      "Select Composer": "select_composer",
      "Set Song": "set_song",
      "Select Song": "select_song",
      "Toggle Screen Record": "toggle_screen_record",

    }
    self.helpdict = {
      "Stop": {
"> ": "stop", 
"$$": "$cacheno", 
"&&": "Stop/Pause audio."},

      "Comment": {
"> ": "0=$DUR=5 seconds\n1=$DUR*3 seconds", 
"$$": "$DUR (audio duration), &comment", 
"&&": "Add comment to current book."},

      "Start": {
"> ": "start",
"$$": "None",
"&&": "Start/Resume recording."},

      "Help": {
"> ": "help",
"$$": "None",
"&&": "Show this help message."},       

      "Pause": {
"> ": "pause",
"$$": "None",
"&&": "Pause video playback."},

      "Next": {
"> ": "next",
"$$": "$no-5 default $54 next in playlist",
"&&": "Next video in playlist or folder."},

      "Unpause": {
"> ": "unpause",
"$$": "",
"&&": "Unpause video playback."},
      "Set Speed": {
"> ": "set speed $value",
"$$": "$value (multiplier 0.2-5.0)",
"&&": "Set playback speed, relative to current."}, 

      "Screenshot": {
"> ": "screenshot",
"$$": "$bbox4 (X1, X2, Y1, Y2)",
"&&": "Take screenshot of video."},

      "Zoomshot": {
"> ": "zoomshot",
"$$": "$bbox4 (X1, X2, Y1, Y2)",
"&&": "Take zoomed screenshot of video."},
      "Screen Toggle": {
"> ": "screen_toggle",
"$$": "$opacity | $record",
"&&": "Toggle video screen overlay."},
      "Screenshot Feedback": {
"> ": "screenshot feedback",
"$$": "$bbox4 (X1, X2, Y1, Y2)",
"&&": "Take screenshot of video and read what is in selected area."},

      "Start Record": {
"> ": "start record",
"$$": "",
"&&": "Start video recording."},
      "Set Composer": {
"> ": "set composer",
"$$": "$composer",
"&&": "Set composer for recording."},
      "Select Composer": {
"> ": "select composer",
"$$": "$composer",
"&&": "Select composer for recording."},
      "Set Song": {
"> ": "set song",
"$$": "$song",
"&&": "Set song for recording."},
      "Select Song": {
"> ": "select song",
"$$": "$song",
"&&": "Select song for recording."},
      "Toggle Screen Record": {
"> ": "toggle screen record",
"$$": "",
"&&": "Toggle screen display for recording."},

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
  

  def comment_(self, sequence=[]):
    if (len(sequence) == 1):

      logger.info(f'> Comment_ {sequence}')

      print("> Comment_ called")
      #get audio input for query.  
      duration = sequence[0]-self.keybot #in seconds
      duration *=3  #double duration for feedback
      from extensions.trey.speech import listen_audio
      self.now = datetime.now()
      self.commentnowstr = self.now.strftime("%Y%m%d%H%M%S") #set nowstr for feedback.  
      self.helpdict['Comment']['$$+'] = f"$DUR={duration} seconds"
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
    #start recording on 0, but return 1

    from extensions.trey.speech import transcribe_audio, get_duration, transcribe_audio_whisper
    timer = datetime.now()
#    self.transcript = transcribe_audio("feedback.wav")
#    self.transcript = transcribe_audio_whisper("comment.wav") #try whisper for better accuracy.  This is slower but hopefully more accurate, especially for short feedback.

    from extensions.trey.speech import transcribe_audio, listen_audio, get_duration, transcribe_audio_whisper

    logger.info(f'> Comment {sequence}')
    #stop recording.  for now just using fixed 10 seconds.  
    #needs to be async to do this properly.
    timer = datetime.now()

    self.transcript = transcribe_audio_whisper("comment.wav")
    dur = get_duration("comment.wav") #actual dynamic duration..
    if (dur == 0):
      duration = (timer - self.now).total_seconds() if self.now is not None else duration
    else:
      duration = dur

    lag = (datetime.now() - timer).total_seconds()
    lag = int(lag)
    print(f'Transcription completed in {lag} seconds: {self.transcript}')

    try:
      vars = {}
      vars['DURATION'] = duration
      vars['COMMENT'] = self.transcript
      vars['LAG'] = lag
      fname = '../transcripts/' + self.name + '/' + self.commentnowstr + '.wav'
      vars['FILE'] = fname
      shutil.copy('comment.wav', fname) #keep a copy for training..
      self.transcriber.write(self.name, "Comment", vars)  
      self.transcriber.write_topic(self.name, "", self.transcript, saveTranscript=False, saveBook=True)

    except Exception as e:
      print(f'Error writing comment file: {e}')

    return 0
    


  def start(self, sequence=[]):
    """Start Recording."""
    logger.info(f'> Start {sequence}')
    self.set_qr("Start", {'type': 'record'})
    return 0
  
  def stop(self, sequence=[]):
    """Stop Recording."""
    logger.info("> Stop {sequence}")
    self.set_qr("Stop", {'type': 'record'})
    return 0

  def help(self, sequence=[]):
    """Show all commands."""
    logger.info(f'> Help {sequence}')
    return 0


  def toggle_screen_record(self, sequence=[]):
    """Toggle Screen Record."""
    logger.info(f'> Toggle Screen Record {sequence}')
    self.set_qr("Toggle Screen Record", {'type': 'video'})
    return 0
  
  def set_composer(self, sequence=[]):
    """Set Composer."""
    #listen to audio..
    logger.info(f'> Set Composer {sequence}')
    if (len(sequence) > 0):
      composer = self.transcriber.get_composer(sequence[-1]-self.keybot) #get composer from key cache
      self.set_qr("Set Composer", {'type': 'video', 'composer': composer})
    return 0
  
  def select_composer(self, sequence=[]):
    """Select Composer."""
    logger.info(f'> Select Composer {sequence}')
    if (len(sequence) > 0):
      composer = self.transcriber.get_composer(sequence[-1]-self.keybot) #get composer from key cache
      self.set_qr("Select Composer", {'type': 'video', 'composer': composer})
    return 0
  
  def set_song(self, sequence=[]):
    """Set Song."""
    #listen to audio..
    logger.info(f'> Set Song {sequence}')
    if (len(sequence) > 0):
      song = self.transcriber.get_song(sequence[-1]-self.keybot) #get song from key cache
      self.set_qr("Set Song", {'type': 'video', 'song': song})
    return 0
  
  def select_song(self, sequence=[]):
    """Select Song."""
    logger.info(f'> Select Song {sequence}')
    if (len(sequence) > 0):
      song = self.transcriber.get_song(sequence[-1]-self.keybot) #get song from key cache
      self.set_qr("Select Song", {'type': 'video', 'song': song})
    return 0
  
  def select_song_(self, sequence=[]):
    """Select Song."""
    logger.info(f'> Select Song_ {sequence}')
    if (len(sequence) > 0 and sequence[-1] == self.keybot):
      #confirm selection and start recording.  
      #show selections..

      self.set_qr("Start Record", {'type': 'video', 'song': self.selected_song})
      return 0
    return 1

  def start_record(self, sequence=[]):
    """Start Record."""
    logger.info(f'> Start Record {sequence}')
    self.set_qr("Start Record", {'type': 'video'})
    return 0
    
  def next(self, sequence=[]):
    """Next Video."""
    logger.info(f'> Next {sequence}')
    cacheno = 1 #default to next..
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot-4 #first key cache selection
      #ends on 54 so 54 is next, 53 is current, 52 is previous.
    #pause trey.  
    self.set_qr("Next", {'type': 'video', 'no': cacheno})
    return 0

  def pause(self, sequence=[]):
    """Pause Video."""
    logger.info(f'> Pause {sequence}')
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot #first key cache selection
      playwrighty.pause_video(cacheno, self.transcriber) #pause video and add bookmark..
    else:
      #pause trey.  
      self.set_qr("Pause", {'type': 'video'})
    return 0

  def unpause(self, sequence=[]):  
    """Unpause Video."""
    logger.info(f'> Unpause {sequence}')
    cacheno = -1
    if (len(sequence) > 0):
      cacheno = sequence[-1]-self.keybot #first key cache selection
      playwrighty.play_video(cacheno) #play video if it is valid cache no..
    else:
        #unpause trey.  
        self.set_qr("Unpause", {'type': 'video'})

    
    return 0


  def set_speed(self, sequence=[]):
    logger.info(f'> Set Speed {sequence}')
    if (len(sequence) > 0):
      adjust = float(sequence[-1] - self.keybot) / 4.0 #just use 10 keys for mid.. 0.2 - 5.0
      #use reverse? 
      if (adjust <= 0.2):
        adjust = 0.2
      if adjust > 5:
        adjust = 5
      self.speed = round(adjust, 1)
      logger.info(f'$$SPEED={self.speed}')
      self.set_qr("Set Speed", {'ADJUST': adjust, 'SPEED': self.speed})
      playwrighty.set_speed(self.speed) #set global speed for all videos.  
    return 0

  def get_XY(self, key, idx=0):
    """Get X,Y from key."""
    #map key to screen position
    #for now just return center of screen
    offset = key - self.mid #for now hardcoded mid.  
    if (self.geo is not None):
        if (idx < 2):
            return self._bbox[0] + self._bbox[2] * (offset+12) // 24
        else:
            return self._bbox[1] + self._bbox[3] * (offset+12) // 24
  def contain_bbox(self, bbox):
    """Contain BBOX within screen."""
    if (self.geo is not None):
        if (bbox[0] < self._bbox[0]):
            bbox[0] = self._bbox[0]
        if (bbox[1] > self._bbox[1]):
            bbox[1] = self._bbox[1]
        if (bbox[2] < self._bbox[2]):
            bbox[2] = self._bbox[2]
        if (bbox[3] > self._bbox[3]):
            bbox[3] = self._bbox[3]
    return bbox


  def get_bbox_aftertouch(self, sequence=[]):
    """Get BBOX from aftertouch sequence."""
    bbox = self.bbox_aftertouch
    #adjust, then save.  
    p = sequence[3] #pressure for now, but could use other params here.
    r = sequence[2] #rotational for now, but could use other params here.
    v = sequence[1] #vertical for now, but could use other params here.
    k = sequence[0] #key for now, but could use other params here.
    if (k == 53): #set first point with original last keypress..
        y = v -35 if (v < 30 or v > 40) else 0 #vertical midpoint 35?  
        y = -y
        x = r if abs(r) > 10 else 0 #rotational
        if (p > 50):
            bbox[0] = bbox[0] - 5 #shift left
            bbox[1] = bbox[1] - 5 #shift left
        else:
            bbox[0] = bbox[0] + int(x/2)
            bbox[2] = bbox[2] + int(y/2)
    elif (k == 55): #for now fixed..
        y = v - 35 if (v < 30 or v > 40) else 0 #vertical midpoint 35?  
        y = -y
        x = r if abs(r) > 10 else 0 #rotational
        if (p > 50):
            bbox[0] = bbox[0] + 5 #shift right
            bbox[1] = bbox[1] + 5 #shift right  
        else:
            bbox[1] = bbox[1] + int(x/2)
            bbox[3] = bbox[3] + int(y/2)
        
    bbox = self.contain_bbox(bbox)
    self.bbox_aftertouch = bbox       
    return bbox
  
  def get_bbox(self, sequence=[]):
    """Get BBOX from sequence."""
    #get BBOX
    if (self.bbox_aftertouch != [400,500,400,500]):
        #default to use aftertouch bbox..
        bbox = self.bbox_aftertouch #start with aftertouch bbox if it has been set, then adjust based on sequence.  This allows for more fluid adjustment.  We can also use aftertouch for more fluid adjustment.
    else:
        bbox = self.bbox #default bbox if no aftertouch has been set.  This is just a starting point, and can be adjusted with the sequence.
        if (len(sequence) > 3):
            for i in range(4):  
                bbox.append(self.get_XY(sequence[i], i))
        elif (len(sequence) > 1):
            tempb = self.bbox #use previous bbox to calc offset
            for i in range(2):  
                bbox.append(self.get_XY(sequence[i], i*2))
                if (i==0):
                    offset = tempb[1]-tempb[0]
                else:
                    offset = tempb[3]-tempb[2]
                bbox.append(bbox[-1]+offset)

        
        if (len(sequence) > 4):
            logger.info(f'Using custom bbox {bbox} from {sequence}')
            #override with more precise bbox
            adjust = 10
            for i in range(4, len(sequence)):
                """down left, up right, left down, right up""" #ok
                """left up, right down""" #ok
                """up left, down right""" #ng
                """[60,60,61,61]""" #up
                """[59,59,60,60]""" #left
                """[61,61,60,60]""" #right


                #i.e. move left, down = 59 decrease x1, 59 = decrease x2, 61 = increase y1, 61 = increase y2
                #squeeze towards mid, 61 = increase x1, 59 = decrease x2, 59 = decrease y1, 61 = increase y2
                #4n+2, 4n+3 = y adjustments reversed
                if (i // 4 == 2 or i // 4 == 3):
                    adjust = -10
                bbox[i%4] += (self.mid-sequence[i])*adjust

            #check bounds.  
            bbox = self.contain_bbox(bbox)


    return bbox

  def ar2str(self, arr):
    """Array to String."""
    string_elements = [str(x) for x in arr]
    single_string = ", ".join(string_elements)

    return single_string

  def qr_in(self, data):
    #handle incoming QR data for now just MPE aftertouch. 
    #used for internal comms as well.. should change queue for that..
    if (self.cmd == "Screenshot" or self.cmd == "Screenshot Feedback"):
      cmds = self.transcriber.read_lines(self.name, data.split('\n')) #save all QR data to transcript.  This is for debugging and record keeping, as well as for loading state from previous sessions.
      for c in cmds:
        if (c['type'] == '> ' and c['cmd'] == 'Aftertouch'):
          #open the page.  
          logger.info(f'Screenshot Aftertouch: {c}')
          self.func = "Screenshot_"
          
          seq = c['vars']['SEQ']
          self.bbox = self.get_bbox_aftertouch(seq)

          logger.info(f'> Screenshot_ {seq}')
          logger.info(f'$$BBOX={self.bbox}')
          self.set_qr(self.func, {'BBOX': self.ar2str(self.bbox), 'SEQ': self.ar2str(seq)})



  def set_qr(self, func, param={}):
    """Set QR."""
    self.qr = "> " + func + "\n"
    for k,v in param.items():
        self.qr += f"$${k}={v}\n"
    self.qr += "$$\n"
    return 0  
  
  def screenshot_(self, sequence=[]):  
    if (len(sequence) >= 4):
      #calc new BBOX from sequence and display
      self.func = "Screenshot_"
      self.bbox = self.get_bbox(sequence)

      logger.info(f'> Screenshot_ {sequence}')
      logger.info(f'$$BBOX={self.bbox}')
      self.set_qr(self.func, {'BBOX': self.ar2str(self.bbox), 'SEQ': self.ar2str(sequence)})
      #show bbox on screen for user to see
    if (len(sequence) > 0 and sequence[-1] == self.keybot):
      #complete command..
      self.cmd = None
      return 0
    return 1

  def screenshot(self, sequence=[]):
    """Take Screenshot."""
    #always in groups of 4 for bbox
    #no need, this should be done..
    self.cmd = None
    self.bbox = self.get_bbox(sequence)
    logger.info(f'> Screenshot {sequence}') 
    logger.info(f'$$BBOX={self.bbox}')

    self.func = "Screenshot"

    #qr specific to current action.
    self.set_qr(self.func, {'TRANSCRIPT': self.transcript, 'BBOX': self.ar2str(self.bbox), 'SEQ': self.ar2str(sequence)})
    #possibly return other data here for other functions.  
    return 0

  def _screenshot_feedback(self, sequence=[]):
     """allow for mouse input to set bbox."""
     logger.info(f'> _Screenshot Feedback {sequence}')
     print("> _Screenshot Feedback called")


     #get audio input for query.  
     from extensions.trey.speech import listen_audio
     self.now = datetime.now()
     self.feedbacknowstr = self.now.strftime("%Y%m%d%H%M%S") #set nowstr for feedback.  
     duration = 15
     at = listen_audio(duration, "feedback.wav") #default 30 seconds and save to feedback.wav
     self.func = "_Screenshot Feedback"
     #indicate to get OCR text
     self.set_qr(self.func, {'DURATION': duration, 'TIME': self.feedbacknowstr})
     #show that we are recording for duration seconds.

     return 1

  def screenshot_feedback_(self, sequence=[]):
     """Take Screenshot Feedback_.  Use 53 to indicate that we are done building bbox."""

     if (len(sequence) == 1):
      #this was causing duplicate recording..
#        self._screenshot_feedback(sequence)
        return 1 #still not complete..
     
     if (len(sequence) > 1 and sequence[-1] == self.keybot): #end of message OK to OCR.
        #calc new BBOX from sequence and display
        self.func = "Screenshot Feedback_"
        self.bbox = self.get_bbox(sequence[0:-1])

        logger.info(f'> Screenshot Feedback_ {sequence}')
        logger.info(f'$$BBOX={self.bbox}')


        self.set_qr(self.func, {'OCR': 'True', 'BBOX': self.ar2str(self.bbox), 'SEQ': self.ar2str(sequence)})
        #do OCR in thread or in UI side..
        #need transcriber there too.. or just write as is message and append OCR variable..

        return 0
     elif (len(sequence) > 1):
        #calc new BBOX from sequence and display
        self.func = "Screenshot Feedback_"
        self.bbox = self.get_bbox(sequence)

        logger.info(f'> Screenshot Feedback_ {sequence}')
        logger.info(f'$$BBOX={self.bbox}')

        self.set_qr(self.func, {'BBOX': self.ar2str(self.bbox), 'SEQ': self.ar2str(sequence)})
     return 1
     
  def screenshot_feedback(self, sequence=[]):
    """Take Screenshot, OCR screenshot and record input"""
    #always in groups of 4 for bbox
    #no need, this should be done..
    self.func = "Screenshot Feedback"
    logger.info(f'> Screenshot Feedback {sequence}') 
    logger.info(f'$$BBOX={self.bbox}')
    #transcribe audio now..
    from extensions.trey.speech import transcribe_audio, transcribe_audio_whisper
    timer = datetime.now()
    self.transcript = transcribe_audio_whisper("feedback.wav")
    lag = (datetime.now() - timer).total_seconds()
    lag = int(lag)

    self.func = "Screenshot Feedback"
    fname = '../transcripts/' + self.name + '/' + self.feedbacknowstr + '.wav'
    shutil.copy('feedback.wav', fname) #keep a copy for training..

    self.set_qr(self.func, {'TRANSCRIPT': self.transcript, 'FNAME': fname, 'LAG': lag, 'BBOX': self.ar2str(self.bbox), 'SEQ': self.ar2str(sequence)})



    #possibly return other data here for other functions.  
    return 0

  def _screenshot(self, sequence=[]):
    """Take Screenshot."""
    logger.info(f'> _Screenshot {sequence}')
    #show bbox on screen for user to see?
    return 2 #indicate skip this function.  

  def screen_toggle(self, sequence=[]):
    """Toggle Screen Overlay."""
    self.func = "Screen Toggle"
    logger.info(f'> Screen Toggle {sequence}')
    opacity = self.opacity
    vars = {}
    if (len(sequence) >=1):
        if (sequence[-1] == self.keybot-1):
          #turn off recording.  
          vars['RECORD'] = 'False'
          vars['OPACITY'] = opacity #use same opacity..
        elif (sequence[-1] == self.keybot+1):
          vars['RECORD'] = 'True'
          vars['OPACITY'] = opacity #use same opacity..
        else:
          opacity = (sequence[0]-self.keybot)*10  #use first param as opacity..
          if (opacity < 0):
              opacity = 0
          elif (opacity > 100):
              opacity = 100
          opacity = opacity / 100.0
          self.opacity = opacity
          vars['OPACITY'] = opacity
          vars['HIDE'] = 'False'

    self.set_qr(self.func, vars)
    return 0
  
  def zoomshot(self, sequence=[]):
    """Take Zoomed Screenshot."""
    logger.info(f'> Zoomshot {sequence}')
    return 0

  def speak(self, text, links=[]):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    return speak(text, links)

  
