import logging
from pynput import *
import pytesseract
from PIL import Image
from io import BytesIO
import win32con
import time

import extensions.trey.playwrighty as playwrighty


logger = logging.getLogger(__name__)

class hotkeys:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.qapp = qapp
    self.startx = startx
    self.name = "hotkeys"
    self.keybot = 53 #
    self.keyoffset = 5 #offset within octave mapping
    self.links = []
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.funcdict = {}

  def word(self, sequence=[]):
    """Word lookup."""
    
    cmd = ""
    sl = str(len(sequence))
    if (sl in self.config['languages'][self.name]):
      logger.info(f'Looking up sequence {sequence} in hotkeys')
      logger.info(self.config['languages'][self.name][sl])
      for k,v in self.config['languages'][self.name][sl].items():
        #check global first.  
        if (sequence == v):
          #can compare directly.  if strings, we do ','.join(self.sequence[-i:]) == v
          found = True
          cmd = k
    return cmd

  def unload(self):
    #unload language specific data
    if (playwrighty.mybrowser is not None):
      playwrighty.close_browser()
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

  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
        "Start": [53,54], #read from this cache page current point.  
        "Stop": [53,52],
        "Read Screen": [53,50],      
        "Go Back": [53,51], 
        "Next": [53,57], #parameter type
#        "Page": [53,57],
      },
      "3": {
        "Skip Lines": [53,55, 57],
        "Page": [53,55, 59], #also read screen
        "Click Link": [53,55, 60], #also read screen
        "Search Web": [53,55, 61], #also read screen
        "Comment": [53,56, 57], #record comment
        "Select Type": [53,57, 58], #parameter type default go next.  
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
      "Stop": "stop_me",
      "Go Back": "go_back",
      "Start": "start_me",
      "Read Screen": "read_screen",
      "Skip Lines": "skip_lines",
      "Page": "page",
      "Click Link": "click_link",
      "Search Web": "search_web",
      "Comment": "comment",
      "Select Type": "select_type",
      "Next": "next",

    }

    return 0  

  #act differently based on words in sequence.    
  def act(self, cmd, words=[], sequence=[]):
    """ACT based on command and sequence."""
    if cmd in self.funcdict:
      func = self.funcdict[cmd]
      #all require keybot at end.
      if hasattr(self, func):
        if (len(sequence) == 1 and sequence[0] == self.keybot):
          return getattr(self, func)(sequence[:-1])
        elif (len(sequence) > 1 and sequence[-2:] == [self.keybot, self.keybot]):
          return getattr(self, func)(sequence[:-2])
        else:
          return 1 #need more keys.
      else:
        logger.error(f"Function {func} not found in {self.__class__.__name__}")
    else:
      print(f"Command {cmd} not found in function maps")
    return -1
  

  def comment(self, sequence=[]):
    #start recording on 0, but return 1
    from extensions.trey.speech import transcribe_audio, listen_audio

    logger.info(f'> Comment {sequence}')
    #stop recording.  for now just using fixed 10 seconds.  
    #needs to be async to do this properly.
    listen_audio(10, "comment.wav")
    text = transcribe_audio("comment.wav")

    return 0
    
  def search_web(self, sequence=[]):
    logger.info(f'> Search Web {sequence}')
    query = "What is the capital of France?"
    from extensions.trey.trey import speak
    speak(f'Searching the web for: {query}')
    body_text, link_data, page, cacheno = playwrighty.search_web(query)
#    print(body_text)
    q2, stop_event = speak(body_text, link_data)
    playwrighty.set_reader_queue(q2, stop_event, cacheno)
    return 0
    
  def click_link(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [53] #default to first link
    logger.info(f'> Click Link {sequence}')

    #find the current link from our reading.  
    if (playwrighty.mybrowser is not None):
      total_read = 0
      current_cache = playwrighty.current_cache
      if (current_cache >= 0 and current_cache < len(playwrighty.page_cache)):
        #get queue for reading.
        q = playwrighty.page_cache[current_cache]['reader_queue']
        while (q is not None and not q.empty()):
          total_read = q.get() #get current link number.  


      a = playwrighty.click_link(-1, total_read, sequence[-1]-self.keybot)
      if (isinstance(a, tuple)):
        body_text, link_data, page, cacheno = a
        print(body_text)
        q2, stop_event = self.speak(body_text, link_data)
        playwrighty.set_reader_queue(q2, stop_event, cacheno)
      else:
        print(f'Clicked link, no new page returned {a}')
        link = None
        idx = sequence[-1]-7-self.keybot
        if (idx >= 0 and idx < len(self.links)):
          link = self.links[idx]
        q2, stop_event = self.speak(f'Clicked link {idx} {link['text']} but nothing new to read.  Go back or restart search')


  def go_back(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [53] #default to first link
    logger.info(f'> Go Back {sequence}')

    #find the current link from our reading.  
    if (playwrighty.mybrowser is not None):
      total_read = 0
      a = playwrighty.go_back(-sequence[-1]+self.keybot)
      if (isinstance(a, tuple)):
        body_text, link_data, page, cacheno = a
        print(body_text)
        q2, stop_event = self.speak(body_text, link_data)
        playwrighty.set_reader_queue(q2, stop_event, cacheno)
      else:
        print(f'Clicked back, no new page returned {a}')
        logger.info('No valid page to go back to.')
        return -1

  def page(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [61] #default to page down
    logger.info(f'> Page {sequence}')
    from extensions.trey.trey import page
    page(sequence[-1]-self.keybot)

  def skip_lines(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [54] #default to 3 lines
    logger.info(f'> Skip Lines {sequence}')
    from extensions.trey.trey import skip_lines
    skip_lines(sequence[-1]-self.keybot)

  def select_type(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [54] #default to content type
    logger.info(f'> Select Type {sequence}')
    from extensions.trey.trey import select_type
    select_type(sequence[-1]-self.keybot)

  def next_type(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [54] #default to next type
    logger.info(f'> Next {sequence}')
    from extensions.trey.trey import next_type
    next_type(sequence[-1]-self.keybot)

  def start_me(self, sequence=[]):
    #Pass parameter for which topic to start.  
    #for now just -N entries.  
    """Start MIDI input/output."""
    return 0
  
  def stop_me(self, sequence=[]):
    """Stop MIDI input/output."""
    logger.info(f'> Stop ME {sequence}')
    from extensions.trey.trey import stop_audio
    stop_audio()

    return 0


  def read_screen(self, sequence=[]):
    logger.info(f'> Read Screen {sequence}')

    if (playwrighty.mybrowser is not None): #we have started a browser session with playwright.
      logger.info('Getting page from Playwright')
      text, links = playwrighty.get_page_details(playwrighty.get_ppage(playwrighty.current_cache))
      self.links = links
      print(f'Playwright found {len(text)} characters and {len(links)} links  on the page') 
      q2, stop_event = self.speak(text, links)
      playwrighty.set_reader_queue(q2, stop_event, playwrighty.current_cache)
          
    else:
      #use PyQt to read screen.
      buffer = None
      if (self.qapp is None):
        logger.error('No QApplication instance provided, cannot read screen.')
        return 0
      else:
        screens = self.qapp.screens()
        for i, s in enumerate(screens):
            logger.info(f'Screen {i}: {s.name()} - Size: {s.size()}')
            logger.info('Capturing Screen')

            screenshot = s.grabWindow( 0 ) # 0 is the main window, you can specify another window id if needed
            screenshot.save('shot' + str(i) + '.jpg', 'jpg')
                # Convert QImage to bytes
#            buffer = BytesIO()
#            screenshot.save(buffer, "PNG") # Or other suitable format like "BMP"
#            buffer.seek(0)


      #call OCR function here.
      #use last screen for now.
      img = Image.open('shot' + str(i) + '.jpg')
#      img = Image.open(buffer)
      lines, links = self.ocr_image(img)
      self.links = links
      print(f'OCR found {len(lines)} lines and {len(links)} links')
      #group by paragraph.
      par = ""
      all = ""
      for i in range(len(lines)):
        line = lines[i]['text']
        if (i > 0 and lines[i]['par_num'] == lines[i-1]['par_num']):
          par += "\n" + line
        else:
          if (par != ""):
            print("PAR: " + par)
            #do something with paragraph here.  
            all += par + "\n\n"
          par = line

      if (par != ""):
        print("PAR: " + par)
        all += par + "\n\n"

      self.speak(all)
        
      return 0

  def speak(self, text, links=[]):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    return speak(text, links)

  
  def ocr_image(self, img):
    # Get detailed OCR data
    from languages.mousemovement1 import mousemovement1
    mm = mousemovement1(self.config)
    mm.startx = self.startx
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    # Loop through the detected words and print their positions
    n_boxes = len(data['text'])
    prevbox = {"x":0, "y":0, "w":0, "h":0}
    currentbox = {"x":0, "y":0, "w":0, "h":0, "text":"", "block_num":-1, "par_num":-1, "line_num":-1, "word_num":-1, "conf":-1}
    prevconf = 0
    currentline = ""
    alllines = []
    alllinks = [] #get all interactive words.  
    for i in range(n_boxes):
        if int(data['conf'][i]) > 60 or prevconf > 60:  # Filter by confidence
            prevconf = int(data['conf'][i])
            text = data['text'][i]

            #seems to come in order.  
            if (text.strip() == ""):
                continue

            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
#            print(f"Text: '{text}', Position: (x={x}, y={y}, w={w}, h={h}, block_num={data['block_num'][i]}, par_num={data['par_num'][i]}, line_num={data['line_num'][i]}, word_num={data['word_num'][i]}, conf={data['conf'][i]})")
#            print(currentbox)
            #check if this is clickable.  
            #move mouse to it and see if it changes.

            
            mm.mouse_move([x+10,y+5], True)
            time.sleep(0.05) #give it a moment to change
            cursor_type = mm.get_current_cursor_type()
            print(f'Cursor type at ({x+10},{y+5}) is {cursor_type}')
            if (cursor_type == win32con.IDC_HAND): #32512 is arrow, 32649
                alllinks.append({"text":text, "x":x, "y":y, "w":w, "h":h, "block_num":data['block_num'][i], "par_num":data['par_num'][i], "line_num":data['line_num'][i], "word_num":data['word_num'][i], "conf":data['conf'][i]})
                print(f"LINK: '{text}', Position: (x={x}, y={y}, w={w}, h={h}, block_num={data['block_num'][i]}, par_num={data['par_num'][i]}, line_num={data['line_num'][i]}, word_num={data['word_num'][i]}, conf={data['conf'][i]})")


            
            if (currentbox["line_num"] == data['line_num'][i] and currentbox["par_num"] == data['par_num'][i] and currentbox["block_num"] == data['block_num'][i]):
                #same line
                currentline += " " + text
                currentbox = {"x":min(prevbox["x"], x), "y":min(prevbox["y"], y), "w":0, "h":0,"text":"", "block_num":data['block_num'][i], "par_num":data['par_num'][i], "line_num":data['line_num'][i], "word_num":data['word_num'][i], "conf":data['conf'][i]}
                currentbox["w"] = max(prevbox["x"]+prevbox["w"], x+w) - currentbox["x"]
                currentbox["h"] = max(prevbox["y"]+prevbox["h"], y+h) - currentbox["y"]
            else:
                if (currentline != ""):
                    print("LINE: " + currentline)
                    print(f"Position: (x={currentbox['x']}, y={currentbox['y']}, w={currentbox['w']}, h={currentbox['h']})")
                    currentbox["text"] = currentline
                    alllines.append(currentbox)
                currentline = text
                currentbox = {"x":x, "y":y, "w":w, "h":h, "text":"", "block_num":data['block_num'][i], "par_num":data['par_num'][i], "line_num":data['line_num'][i], "word_num":data['word_num'][i], "conf":data['conf'][i]}


    if (currentline != ""):
        print("LINE: " + currentline)
        currentbox["text"] = currentline
        alllines.append(currentbox)
    return alllines, alllinks
