import logging
from pynput import *
import pytesseract
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

class hotkeys:
  #define action for some sequences.  
  def __init__(self, config, qapp=None):
    self.config = config
    self.qapp = qapp
    self.name = "hotkeys"
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
        "Start": [53,54],
        "Stop": [53,52],
        "Read Screen": [53,50],
      },
      "3": {
        "Skip Lines": [53,55, 57],
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
      "Start": "start_me",
      "Read Screen": "read_screen",
      "Skip Lines": "skip_lines",

    }

    return 0  
  
  def act(self, cmd, sequence=[]):
    """ACT based on command and sequence."""
    if cmd in self.funcdict:
      func = self.funcdict[cmd]
      if hasattr(self, func):
        return getattr(self, func)(sequence)
      else:
        logger.error(f"Function {func} not found in {self.__class__.__name__}")
    else:
      print(f"Command {cmd} not found in function maps")
    return -1
  

  def skip_lines(self, sequence=[]):
    if (len(sequence) < 1):
      return 1
    else:
      logger.info(f'> Skip Lines {sequence}')
      from extensions.trey.trey import skip_lines
      skip_lines(sequence[-1]-55)

  def start_me(self, sequence=[]):
    #Pass parameter for which topic to start.  
    #for now just -N entries.  
    """Start MIDI input/output."""
    if (len(sequence) > 2):
      logger.info(f'> Start ME {sequence}')
      return 0
    else:
      return 1 # not enough keys.
  
  def stop_me(self, sequence=[]):
    """Stop MIDI input/output."""
    logger.info(f'> Stop ME {sequence}')
    from extensions.trey.trey import stop_audio
    stop_audio()

    return 0


  def read_screen(self, sequence=[]):
    if (len(sequence) < 1):
      return 1 #need more data
    else:
      logger.info(f'> Read Screen {sequence}')

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
      lines = self.ocr_image(img)

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

  def speak(self, text):
    from extensions.trey.trey import speak
#    print(f'Speaking: {text}')
    speak(text)

    return 0
  
  def ocr_image(self, img):
    # Get detailed OCR data
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    # Loop through the detected words and print their positions
    n_boxes = len(data['text'])
    prevbox = {"x":0, "y":0, "w":0, "h":0}
    currentbox = {"x":0, "y":0, "w":0, "h":0, "text":"", "block_num":-1, "par_num":-1, "line_num":-1, "word_num":-1, "conf":-1}
    prevconf = 0
    currentline = ""
    alllines = []
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
    return alllines
