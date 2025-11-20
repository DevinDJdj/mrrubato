import logging
from pynput import *
import pytesseract
from PIL import Image
from io import BytesIO
import win32con
import time
import os
from datetime import datetime, timedelta
import extensions.trey.playwrighty as playwrighty

logger = logging.getLogger(__name__)

class hotkeys:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):

    self.config = config
    self.qapp = qapp
    self.startx = startx
    self.func = None
    self.qr = "" #info for QR message

    self.geo = None
    self.name = "hotkeys"
    self.keybot = 53 #
    self.keymid = 7 #middle C for bbox calc
    self.keyoffset = 5 #offset within octave mapping
    self.links = []
    self.maxseq = 10 #includes parameters
    self.callback = None
    self.transcript = ""
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
    #if (playwrighty.mybrowser is not None):
      #this resets playwrighty context.
      #how do we keep context?  
      #playwrighty.close_browser()

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


  def insert_word(self, func, sequence=[], word=""):
    """Insert word into sequence.  Word may be sentence."""

    if (func == "search_web"):
      from mykeys import text2seq
      seq = text2seq(word)
      if (len(sequence) == 1): #default case.  Have to add extra keybot
        #should be using negative index so append to beginning.
        sequence = seq + sequence + [self.keybot] #separator
      else:
        sequence = seq + sequence
      return sequence

  def load_bookmarks(self):
    #load bookmarks from file for this date.  
    #maybe playwrighty should handle this?
    #get date as YYYYMMDD
    #for now just open most recent file.
    today = datetime.now().strftime("%Y%m%d")
    logger.info(f'Loading bookmarks')
    #yesterday also    
    yesterday = (datetime.now() - timedelta(1)).strftime("%Y%m%d")
    #list all files in directory
    files = os.listdir('../' + self.name)
    sorted_files = sorted(files)
    numloaded = 0
    for f in sorted_files:
      if (f.startswith(yesterday) or f.startswith(today)):
        with open('../' + self.name + '/' + f) as ff:
          lines = ff.readlines()
          for line in lines:
            #add bookmark manually.  
            parts = line.strip().split('\t')
            cmd = parts[0]
            if (cmd == '> Add Bookmark'):
              url = parts[1]
              total_read = int(parts[2])
              body_length = int(parts[3]) if len(parts) > 3 else 0

              print(f'Loaded bookmark {url} at {total_read}')
              playwrighty.add_bookmark(url, total_read) #call playwrighty add bookmark..
              numloaded += 1


    #list files in 
    logger.info(f'Loaded {numloaded} bookmarks from {len(sorted_files)} files')
    return 0    
  

  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
#        "Start": [53,54], #read from this cache page current point.  
        "Stop": [53,51],
        "Pause": [53,52],
        "Resume": [53,54],
        "Read Screen": [53,50],
#        "Page": [53,57],
      },
      "3": {
        "Skip Lines": [53,55, 57],
        "Page": [53,55, 59], #also read screen
        "Click Link": [53,55, 60], #also read screen
        "Find Last": [53,55, 58], #Jump in screen
        "Search Web": [53,55, 61], #also read screen
        "Comment": [53,56, 57], #record comment
        "Go Back": [53,55,51], 
        "List Tabs": [53,58,59],
        "Select Tab": [53,58,60],
#        "Select Type": [53,57, 58], #parameter type default go next.  
      }, 
      "4": {
        "Add Bookmark": [53,58,60,62], #feedback tells which mark it is.  Or default to set to 0 idx.  
        #manually select 0 idx = [53,58,60,62,53,53,53]
        "List Bookmarks": [53,58,60,63], #no params
      }
    }

    if (self.name in self.config['languages']):
      logger.info(f'Merging existing {self.name} config')
      #need logic to iterate and pick each one.  This is not working right.  
      default.update(self.config['languages'][self.name])
      for sl in self.config['languages'][self.name]:
        #check for each word
        if (sl not in default):
          default[sl] = {}
        if (sl != 'keybot'):
          for k in self.config['languages'][self.name][sl]:              
            default[sl][k] = self.config['languages'][self.name][sl][k]

      if ('keybot' in self.config['languages'][self.name]):
        default['keybot'] = self.config['languages'][self.name]['keybot']
        self.keybot = default['keybot']
      #update all others based on any keybot change.
      for sl in default:
        if (sl != 'keybot'):
          for k in default[sl]:
            #update all sequences by diff.
            seq = default[sl][k]
            #this allows to 0 index or any index if preferred..
            #easier to port relative words from other languages..
            #eventually probably get used to 0-indexing
            innerdiff = self.keybot - seq[0]
            if (len(seq) > 1): #dont update single key sequences. Eventually this shouldnt exist I think..
              for i in range(len(seq)):
                seq[i] += innerdiff

            default[sl][k] = seq
            print(f'Updated {sl} {k} sequence to {seq}')
    else:
      logger.info(f'No existing {self.name} config found, creating new one')

    self.config['languages'][self.name] = default
    self.funcdict = {
      "Stop": "stop_me",
      "Pause": "pause_reader",
      "Resume": "resume_reader",
      "Go Back": "go_back",
      "Start": "start_me",
      "Read Screen": "read_screen",
      "Skip Lines": "skip_lines",
      "Page": "page",
      "Click Link": "click_link",
      "Find Last": "find_last",
      "Search Web": "search_web",
      "Comment": "comment",
      "Select Type": "select_type",
      "List Tabs": "list_tabs",
      "Select Tab": "select_tab",
      "_Search Web": "_search_web",
      "Search Web_": "search_web_",
      "Add Bookmark": "add_bookmark",
      "List Bookmarks": "list_bookmarks"
    }

    self.load_bookmarks()
    return 0  

  #act differently based on words in sequence.    
  def act(self, cmd, words=[], sequence=[]):
    """ACT based on command and sequence."""
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
        getattr(self, func + "_")(sequence)
      
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
  

  def comment(self, sequence=[]):
    #start recording on 0, but return 1
    from extensions.trey.speech import transcribe_audio, listen_audio

    logger.info(f'> Comment {sequence}')
    #stop recording.  for now just using fixed 10 seconds.  
    #needs to be async to do this properly.
    listen_audio(10, "comment.wav")
    text = transcribe_audio("comment.wav")

    return 0
    
  def list_tabs(self, sequence=[]):
    logger.info(f'> List Tabs {sequence}')
    if (playwrighty.mybrowser is not None):
      for i, page_info in enumerate(playwrighty.page_cache):
        print(f'Tab {i}: {page_info["url"]}')
        self.speak(f'Tab {i}: {page_info["title"]}')
    else:
      print('No browser session active.')
      self.speak('No browser session active.')
    return 0

  def list_bookmarks(self, sequence=[]):
    logger.info(f'> List Bookmarks {sequence}')
    #for now just demo..

    return 0

  def add_bookmark(self, sequence=[]):
    logger.info(f'> Add Bookmark {sequence}')
    #do this also on pause..
    #for now just demo..
    #how to store local data for this?  
    #readable file?  Just use date for now..
    #get URL and location in page.  
    cacheno = -1
    if (playwrighty.mybrowser is not None):
      if (len(sequence) > 0):
        cacheno = sequence[-1]-self.keybot
      
      if (cacheno > -1 and cacheno < len(playwrighty.page_cache)):
        cacheno = cacheno
      else:
        cacheno = playwrighty.current_cache

      page = playwrighty.get_ppage(playwrighty.current_cache)
      url = page.url
      total_read = 0
      total_read = playwrighty.update_page_offset()
      #get date as YYYYMMDD

      today = datetime.now().strftime("%Y%m%d")
      #find URL in bookmarks already?
      playwrighty.add_bookmark(url, total_read)
      body_length = playwrighty.page_cache[playwrighty.current_cache]['length'] if playwrighty.current_cache >=0 and playwrighty.current_cache < len(playwrighty.page_cache) else 0

      os.makedirs('../' + self.name, exist_ok=True)
      with open('../' + self.name + '/' + today + '.txt', 'a') as f:        
        f.write(f'> Add Bookmark\t{url}\t{total_read}\t{body_length}\n')
        #dont worry about duplication at this point.



    return 0
  
  def select_tab(self, sequence=[]):
    logger.info(f'> Select Tab {sequence}')
    if (playwrighty.mybrowser is not None):
      select_index = 0
      if (len(sequence) > 1):
        select_index = sequence[-1]-(self.keybot+self.keymid) #offset from middle C
      if (select_index >= 0 and select_index < len(playwrighty.page_cache)):
        playwrighty.current_cache = select_index
        page = playwrighty.page_cache[select_index]['page']
        print(f'Switched to Tab {select_index}: {page.url}')
        self.speak(f'Switched to Tab {select_index}: {page.title}')
        #read page from current offset.  
        body_text, link_data, page, cacheno = playwrighty.read_page('', select_index)
        self.links = link_data
        #pause audio first..

        q2, q3, stop_event = self.speak(body_text, link_data)
        playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)

    else:
      print('No browser session active.')
      self.speak('No browser session active.')
    return 0

  def _search_web(self, sequence=[]):  
    logger.info(f'> _Search Web {sequence}')
    print("> _Search Web called")
    #get audio input for query.  
    from extensions.trey.speech import listen_audio
    at = listen_audio(5, "query.wav")
    #at.join() #wait for it to finish.
    #have to just use some keys until this is done.  
    #need to return 1 to indicate we need more keys.
    #but this is only called once.  
    return 1

  def search_web_(self, sequence=[]):  

    logger.info(f'> Search Web_ {sequence}')
    #no function, just demo..
    return 1


  def search_web(self, sequence=[]):
    logger.info(f'> Search Web {sequence}')
    query = "What is the capital of France?"
    from extensions.trey.speech import transcribe_audio
    self.transcript = transcribe_audio("query.wav")
    logger.info('$$AUDIO = ' + self.transcript)
    

    if (self.transcript != ""):
      query = self.transcript
    from extensions.trey.trey import speak
    speak(f'Searching the web for: {query}')
    engine = 0
    cacheno = -1
    print(sequence)

    #one param = engine
    if (len(sequence) > 0):
      engine = sequence[-1]-self.keybot
    #two = engine, cacheno
    if (len(sequence) > 1):
      engine = sequence[-2]-self.keybot
      cacheno = sequence[-1]-self.keybot

    
    body_text, link_data, page, cacheno = playwrighty.search_web(query, engine=engine, cacheno=cacheno)
#    print(body_text)
    self.links = link_data
    #should always have a value here..  
    total_read = playwrighty.get_bookmark(page.url, cacheno)
    q2, q3, stop_event = self.speak(body_text, link_data, total_read)
    playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)


    return 0



  def find_last(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [53] #default to first link
    logger.info(f'> Find Last {sequence}')
    #find the current link from our reading.  
    if (playwrighty.mybrowser is not None):
      current_cache = playwrighty.current_cache
      if (current_cache >= 0 and current_cache < len(playwrighty.page_cache)):
        #get queue for reading.
        q2 = playwrighty.page_cache[current_cache]['reader_queue']
        while (q2 is not None and not q2.empty()):
          total_read = q2.get() #get current link number.  
          #find last link read.  
        return playwrighty.find_last(sequence[-1]-self.keybot, current_cache, text_offset=total_read)



  def click_link(self, sequence=[]):
    if (len(sequence) < 1):
      sequence = [53] #default to first link
    logger.info(f'> Click Link {sequence}')
    print('> Click Link {sequence}')

    #find the current link from our reading.  
    if (playwrighty.mybrowser is not None):
      total_read = 0
      total_read = playwrighty.update_page_offset()
      q3 = playwrighty.page_cache[playwrighty.current_cache]['sim_queue']
      siml = []
      while (q3 is not None and not q3.empty()):
        siml.insert(0,q3.get()) #get current similar offset.



      #Use simlink if we are using future links.  
      #should be the location of the simlink.  
      if sequence[-1]-self.keybot > 0 and len(siml) > sequence[-1]-self.keybot-1:
        total_read = siml[sequence[-1]-self.keybot-1]

      a = playwrighty.click_link(-1, total_read, sequence[-1]-self.keybot)
      if (isinstance(a, tuple)):
        body_text, link_data, page, cacheno = a
        self.links = link_data
        print(body_text)
        total_read = playwrighty.get_bookmark(page.url, cacheno)

        q2, q3, stop_event = self.speak(body_text, link_data, total_read) #add offset to skip until where we were.)
        playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)
        return 0
      else:
        print(f'Clicked link, no new page returned {a}')
        link = None
        idx = sequence[-1]-7-self.keybot
        if (idx >= 0 and idx < len(self.links)):
          link = self.links[idx]
        q2, q3, stop_event = self.speak(f'Clicked link {idx} {link['text']} but nothing new to read.  Go back or restart search')
        return -1

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

        self.links = link_data
#        print(body_text)
        page = playwrighty.page_cache[cacheno]['page']
        total_read = playwrighty.get_bookmark(page.url, cacheno)
        logger.info('$$Total_Read = ' + str(total_read))
        q2, q3, stop_event = self.speak(body_text, link_data, total_read) #add offset to skip until where we were.  
        playwrighty.set_reader_queue(q2, q3, stop_event, cacheno)
        return 0
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

  def pause_reader(self, sequence=[]):
    logger.info(f'> Pause Reader {sequence}')
    from extensions.trey.trey import pause_reader
    pause_reader()
    self.add_bookmark()
    return 0

  def resume_reader(self, sequence=[]):
    logger.info(f'> Resume Reader {sequence}')
    from extensions.trey.trey import resume_reader
    resume_reader()

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


  def start_me(self, sequence=[]):
    #Pass parameter for which topic to start.  
    #for now just -N entries.  
    """Start MIDI input/output."""
    return 0
  
  def stop_me(self, sequence=[]):
    """Stop MIDI input/output."""
    logger.info(f'> Stop ME {sequence}')
    from extensions.trey.trey import stop_audio
    cacheno = -1
    if (len(sequence) > 0):
      self.add_bookmark(sequence)
      cacheno = sequence[-1]-self.keybot
      stop_event = playwrighty.get_stop_event(cacheno)
      if (stop_event is not None):
        stop_event.set()  # Signal the specific audio thread to stop
    else:
      self.add_bookmark()
      stop_audio() #stop all.  

    return 0


  def read_screen(self, sequence=[]):
    logger.info(f'> Read Screen {sequence}')

    if (playwrighty.mybrowser is not None): #we have started a browser session with playwright.
      logger.info('Getting page from Playwright')
      text, links = playwrighty.get_page_details(playwrighty.get_ppage(playwrighty.current_cache))
      text, links, page, cacheno = playwrighty.read_page('', playwrighty.current_cache) #read current page

      self.links = links
      print(f'Playwright found {len(text)} characters and {len(links)} links  on the page') 
      q2, q3, stop_event = self.speak(text, links)
      playwrighty.set_reader_queue(q2, q3, stop_event, playwrighty.current_cache)
      return 0
    
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

  def speak(self, text, links=[], total_read=0):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    return speak(text, links, total_read)

  
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
