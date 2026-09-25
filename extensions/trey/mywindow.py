


import os
import random
import time
import threading
import sys
import math
#standard
from datetime import datetime, timedelta


#win32 libraries
import win32gui
import win32process
import win32api
import win32con

from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QDialog, QVBoxLayout, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QImage, QFont, QFontMetrics, QFontDatabase, QIcon, QColor
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread
import PyQt5.QtCore as QtCore
#video widget..
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

#Graph libraries, image processing
import networkx as nx
import matplotlib


import config
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from playsound3 import playsound

#OCR
import pytesseract

import markdown

import languages.helpers.transcriber as transcriber

import extensions.trey.synth as synth
import extensions.trey.speech as speech


import json
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='trey.log', 
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class Communicate(QtCore.QObject):
    mySignal = QtCore.pyqtSignal(int)



#thread to get QR data from window and add text info to trey cache.  
#Screen capture, input capture, QR code generation
import mss
import qrcode
from pynput import keyboard, mouse

import cv2
from qreader import QReader
import numpy as np

#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
sys.path.insert(2, 'c:/devinpiano/music/mrrubato') #config.py path Base project path
import config 
import mykeys

#import extensions.trey.trey as trey
#from extensions.trey.trey import pause_obs_capture, pause_reader, qapp, restart_me, resume_reader, start_obs_capture, stop_obs_capture, _get_window_info, _hide, speak, create_qr_code


# Step 1: Create a worker class
class QRInWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def qimage_to_cv2(self, qimage):
        """Converts a QImage into an OpenCV image (numpy array)."""
        # Ensure the QImage is in a format that allows direct byte access (e.g., RGBA8888 or RGB888)
        # OpenCV expects BGR format, so conversion might be needed later depending on the source
        if qimage.format() != QImage.Format_RGB888:
            # Convert to a standard 8-bit RGB format. Format_ARGB32 is common
            qimage = qimage.convertToFormat(QImage.Format_ARGB32)

        width = qimage.width()
        height = qimage.height()
        
        # Get a pointer to the raw bytes
        ptr = qimage.bits()
        # Set the size of the pointer to the total number of bytes
        ptr.setsize(qimage.byteCount())
        
        # Create a NumPy array from the raw data
        # The shape will be (height, width, channels)
        # The data is copied in this step
        arr = np.array(ptr).reshape(height, width, -1) # Use -1 to infer the number of channels

        # If the QImage was in ARGB32 format, the array will be in BGRA order (due to Qt's internal representation on many systems)
        # OpenCV uses BGR, so if you need to perform typical OpenCV operations, convert the color space
        if qimage.format() == QImage.Format_ARGB32:
            # Convert from BGRA to BGR
            arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
        elif qimage.format() == QImage.Format_RGB888:
            # Convert from RGB to BGR (OpenCV's default color order)
            arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        # Handle other formats as needed (e.g., grayscale)
        elif qimage.format() == QImage.Format_Grayscale8:
            # No color conversion needed for grayscale, it's a 2D array
            arr = arr.reshape(height, width)

        return arr

    def read_qr_code(self, img):
        
        #qreader too slow, use nano model for speed.
        #income as QImage
        img = self.qimage_to_cv2(img)
        #calc width, get upper right quadrant for now just read here.  
        x_start = int(img.shape[1] / 2)
        x_end = img.shape[1]
        y_start = 0
        y_end = int(img.shape[0] / 2)
        cropped_img = img[y_start:y_end, x_start:x_end, :]
#        print(f'Cropped image shape: {cropped_img.shape}')
        cropped_image = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_BGR2RGB)
        decoded_texts = self.qreader.detect_and_decode(image=cropped_image)
        if decoded_texts:
            for text in decoded_texts:
                print(f"QR In Code data: {text}")
                logger.info(f"QR In Code data: {text}")
            return decoded_texts
        else:
#            print("No QR In code detected.")
            return []
        
    def __init__(self, my_queue, parent=None, mywindow=None):
        super(QRInWorker, self).__init__(parent)
        self.my_queue = my_queue # Store parameter in the worker instance
        self.all_qr = [] #store all qr data seen.
        self.qreader = QReader(model_size='n')  # Initialize the QR code reader with a nano model
        self.mywindow = mywindow # Store reference to the window instance

    def find_recent_qr(self, qrin, timeframe=5):
        """Find QR data seen in the last timeframe seconds."""
        current_time = time.time()
        recent_qr = self.all_qr[-5:] #last 5 entries
        for qr in recent_qr:
            if ('data' not in qr or 'timestamp' not in qr):
                continue #not valid data
            if (qr['data'] == qrin and (current_time - qr['timestamp']) < timeframe):
                return True
        return False
    
    def run(self):
        """Long-running task to find QR data from window."""
        previmg = None
        logger.info(f'Starting QRInWorker run loop.')
        while (True):
            #get QR data from window
            #this has between 2-10 second delay in read_qr_code.  
            #print(time.time())
            screens = self.mywindow.qapp.screens()
            #assume last window
            qimage = screens[-1].grabWindow(0).toImage()
            #skip if same as previous image.
            if (qimage == previmg):
                time.sleep(0.5)
                continue #skip same image
            previmg = qimage
#            print(qimage.width(), qimage.height())
            qrdata = self.read_qr_code(qimage)
#            print(time.time())

            for qd in qrdata:
                logger.info(f'QRInWorker found QR data: {qd}')
                if (isinstance(qd, str) == False):
                    continue
                if (qd.find('<<meta>>') == -1): #for now dont accept meta data, simple way to not read self for now.
                    continue #not our data.
                if not self.find_recent_qr(qd): #skip anything we just saw.  
                    self.my_queue.put(qd)
                    self.all_qr.append({'data': qd, 'timestamp': time.time()})
                    self.progress.emit(qd) #can pass param here as well.  

            time.sleep(0.2) #run each 0.2 seconds
            print(time.time())
        self.finished.emit()


#separate worker probably better for non-QR commands..

# Step 1: Create a worker class
class QRWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, my_queue, parent=None):
        super(QRWorker, self).__init__(parent)
        self.my_queue = my_queue # Store parameter in the worker instance

    def run(self):
        """Long-running task."""
        while (self.my_queue is not None):
            while (not self.my_queue.empty()):
                #incoming data from mykeys..
                qrdata = self.my_queue.get() #get current link number.  
                logger.info(f'Worker processing QR data: {qrdata[0:50]}')
                self.progress.emit(qrdata) #can pass param here as well.  
#                time.sleep(0.2) #allow for QR data to be processed by any reader.  
            time.sleep(0.1) #wait before checking again
        self.finished.emit()


class QPaintedLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bbox = None


    def paintEvent(self, event):
        # Let QLabel paint its original content (like text/pixmap) first
#        print("painting QPaintedLabel")
        super().paintEvent(event)
        
        # Create a painter for the label
        painter = QPainter(self)
        
        # Set your drawing properties
        pen = QPen(QColor("red"))
        pen.setWidth(5)
        painter.setPen(pen)
        
        # Perform custom drawing
        if self.bbox is not None:
            painter.drawRect(self.bbox['x'], self.bbox['y'], self.bbox['width'], self.bbox['height'])
    
    def set_overlay_bbox(self, bbox):
        self.bbox = bbox
        self.update()  # Trigger a repaint to show the new bounding box


class MyWindow(QMainWindow):


    def reportProgressIn(self, qrdata):
        logger.info(f"QR In: {qrdata}")
        cmds = self.parseQRData(qrdata)
        for idx, cmd in enumerate(cmds):
            currentcmd = cmd['cmd']
            vars = cmd['vars']
            logger.info(f'Parsed QR command: {currentcmd} with vars: {vars}')
            written = self.transcriber.write(vars.get('KLANG', 'base'), currentcmd, vars, None, False) #dont write intermediate msg?            
            #make sure we have parsability..
            self.qr_in.append(written)

            #process incoming commands as needed.
            #for now just log them.
            if (cmd['type'] == '> '):
                if (currentcmd == "Record Feedback"):
                    #process feedback command.  
                    logger.info(f'Processing record feedback command with vars: {vars}')

    def reportProgress(self, qrdata):
#        logger.info(f"QR Out: {qrdata}")
        cmds = self.parseQRData(qrdata)
        #get lang.. dont show based on lang for now..
        is_joystick_cmd = next((cmd for cmd in cmds if cmd['lang'] == 'joystick'), None)
        if (len(cmds) > 0 and is_joystick_cmd is None):
            self.showQR(qrdata, cmds) #refresh QR display
            #process joystick command as needed.  For now just log it.

        pwords = []
        for idx, cmd in enumerate(cmds):
            if (cmd['type'] == '> '):
                currentcmd = cmd['cmd']
                vars = cmd['vars']
                if ('timestamp' in vars):
                    #compare to current time..
                    current_time = time.time()
                    if (float(vars['timestamp']) < current_time - 0.5):
                        metapos = qrdata.find('<<meta>>')
                        logger.info(f'!!TIME LAG {vars["timestamp"]} {current_time}\n{qrdata[:metapos]}')
#                        continue #skip this command if time mismatch dont want anything stale..
                logger.info(f'Parsed QR command: {currentcmd} with vars: {vars}')
                self.qr_out.append({'cmd': currentcmd, 'vars': vars, 'timestamp': time.time()})
                self.executeQRCommand(currentcmd, vars, cmd['lang'])
            if (cmd['type'] == '~~'):
                word = cmd['word']
                keys = cmd['keys']
                pwords.append({'word': word, 'keys': keys})
#                logger.info(f'Parsed QR word: {word} with keys: {keys}')
                #process as needed.
                #add to list of words to display..

        print(f'~~: {len(pwords)}')
#        self.updateWords(pwords)

    def add_setting(self, key, value, lang='_meta'):
        """Add a setting to the custom settings."""
        config.custom_settings[lang+"_"+key] = value

    def get_setting(self, key, default=None, lang='_meta'):
        """Get a setting from the custom settings."""
        return config.custom_settings.get(lang+"_"+key, default)


    def update_graph_entities(self, graphs, entities, main_entity, topic, show=True):
        if (len(entities) > 0 and main_entity): #update entities first.. only if this is graph in response to question..
            try:
            #add to transparent
                entities = json.loads(entities)
                if (show):
                    for i, ent in enumerate(entities):
                        #this is transient based on state..
                        if (i > 24):
                            break
                        self.label_filter_info[i].setText('(' + ent['label'][:3] + ') ' + ent['text'])
            except Exception as e:
                logger.error(f'!!Error parsing entities: {e}')
                logger.error(f'!!ENTITIES: {entities}')
        if (len(graphs) > 0): #actually just relationship triples..
            try:
                graphs = json.loads(graphs)
                #why this is in array not sure..
                kg = self.make_kg(graphs, entities, topic=topic) #pass topic and perhaps other..
                if (kg and main_entity and show): #dont visualize if we dont have a main entity, just update the graph data for now.
                    self.visualize_kg(kg, main_entity if main_entity else topic)
            except Exception as e:
                logger.error(f'!!Error parsing graphs: {e}')
                logger.error(f'!!Graphs data: {graphs}')

    def executeQRCommand(self, command, vars, lang='hotkeys'):
        #use transcriber here??
        import extensions.trey.trey as trey

        """Execute a QR command based on the parsed data."""
        logger.info(f'Executing QR command: {command} with vars: {vars}')
        #get current foreground window.  

        temp = win32gui.GetForegroundWindow()
        rect = win32gui.GetWindowRect(temp)
        lagtime = float(vars.get('timestamp', time.time()))
        match command:
            case "graph":
                graphs = vars.get('GRAPHS', '')
                main_entity = vars.get('ENTITY', '')
                entities = vars.get('ENTITIES', '')
                show = vars.get('show', True)
                logger.info(f'> graph\n==\n{graphs}')
                self.update_graph_entities(graphs, entities, main_entity, vars.get('**', self.transcriber.current_topic), show=show)
            case "ask":
                _ = vars.get('_', 'hotkeys')
                if (_ == 'hotkeys'):
                    logger.info('Received ask command')
                    answer = vars.get('ANSWER', '')
                    answer = answer.replace('\t', '\n') #for now just do here..
                    graphs = vars.get('GRAPHS', '')
                    main_entity = vars.get('ENTITY', '')
                    entities = vars.get('ENTITIES', '')
                    show = vars.get('show', True)

                    logger.info(f'> ask\n==\n{answer}\n==\n{graphs}')
                    self.update_graph_entities(graphs, entities, main_entity, vars.get('**', self.transcriber.current_topic), show=show)
                elif (_ == 'book'):
                    logger.info('Received ask command for book')
                    #just sending to vscode for now..

                #create knowledge graph
            case "OK":
                #testing
                logger.info('Received OK command, showing QR code with current settings')
                #test function for sending keystrokes.. better to use transcriber..
#                if (self.in_trey(rect)): #only capture second monitor clicks                
#                    send_ok()
                self.transcriber.write_plain(lang, command) #dont write intermediate msg?

                #send keystroke test..

            case "Generate Image":
                logger.info('Received Generate Image command')
                if (vars.get('fname', None) is not None):
                    fname = vars.get('fname')
                    if (os.path.exists(fname)):
                        self.play(fname)
                        logger.info(f'> Show Image {fname}')
                    else:
                        logger.error(f'!!> Show Image {fname} not found')

            case "Screen Toggle":
                tohide = vars.get('HIDE', 'True')
                if (self.isVisible()):
                    #remove stale info?  
                    if (tohide == 'True'):
                        self.hide()                
                        #pause OBS capture.

                        trey.pause_obs_capture()
                    else:
                        op = self.get_setting('OPACITY', 0.4, lang)
                        op = float(vars.get('OPACITY', op))
                        self.setWindowOpacity(op)
                        self.add_setting('OPACITY', op, lang)
                else:
                    op = self.get_setting('OPACITY', 0.4, lang)
                    op = float(vars.get('OPACITY', op))
                    rec = self.get_setting('RECORD', 'False', lang)
                    rec = vars.get('RECORD', rec)
                    self.setWindowOpacity(op)
                    self.add_setting('OPACITY', op, lang)
                    self.add_setting('RECORD', rec, lang)
                    
                    self.show()
                    #start OBS capture..
                    if (rec == 'True'):
                        trey.start_obs_capture()

            case "Stop":        
                type = vars.get('type', 'video')
                if (type == 'video'):
                    #not used
                    n = 0
                elif (type == 'record'):
                    trey.pause_obs_capture()
            case "Start":
                type = vars.get('type', 'video')
                if (type == 'video'):
                    #not used..
                    n = 0 
                elif (type == 'record'):
                    trey.start_obs_capture()
            case "Restart":
                type = vars.get('type', 'video')
                if (type == 'video'):
                    #not used..
                    n = 0
                elif (type == '_meta'):

                    trey.restart_me() #restart and leave transcription


            case "Next":
                type = vars.get('type', 'video')
                no = vars.get('no', '1')
                if (type == 'video'):
                    #logic to pick next video/audio in our commands.. tmap
                    self.play_tmap(int(no)) #play next item in tmap
                    n = 0
                elif (type == 'record'):
                    #not used..
                    n = 0
            case "Pause":
                type = vars.get('type', 'video')
                if (type == 'video'):
                    #logic to pause video playback
                    #pick next video/audio in our commands.. tmap
                    self.pause_tmap()
                    n = 0
                elif (type == 'record'):
                    trey.pause_obs_capture()
                elif (type == 'base'):
                    self.pause_tmap(False) #dont hide the video, just pause it..
                    #pause any other speaking or playing we are doing.
                    self.transcriber.write_plain('base', '> ' + command) #dont write intermediate msg?
                elif (type == 'book'):
                    cacheno = vars.get('cacheno', -1)
                    self.transcriber.write_plain('book', '> ' + command) #dont write intermediate msg?
                    trey.pause_reader(int(cacheno))




            case "Unpause":
                type = vars.get('type', 'video')
                if (type == 'video'):
                    #logic to unpause video playback
                    #pick next video/audio in our commands.. tmap
                    #anything with $$FILE or $$fname or..
                    self.play_tmap()
                    n = 0
                elif (type == 'record'):
                    trey.start_obs_capture()
                elif (type == 'book'):
                    cacheno = vars.get('cacheno', -1)
                    trey.resume_reader(int(cacheno))
            case "Get Video":
                cacheno = vars.get('cacheno', -1)
                self.get_video(cacheno)

            case "Get Cache":
                cacheno = vars.get('cacheno', -1)
                self.get_qr_cache(int(cacheno))

            case "Screenshot Feedback_":
                bbox = vars.get('BBOX', None)
                if (bbox is not None):
                    self.draw_screen_box(vars.get('BBOX', self.geometry().getRect()))

                #send back the OCR text as feedback.
                #just add to file assuming we 
                #probably dont need this..
                if (vars.get('OCR', 'False') == 'True'):
                    ocrtext, fname = self.save_screenshot(vars.get('KLANG', 'video'), vars.get('TRANSCRIPT', ''), vars.get('BBOX', None), True) #always OCR
                    vars['OCRTEXT'] = ocrtext
                    vars['FNAME'] = fname
                    self.ocrtext = ocrtext
                written = self.transcriber.write(vars.get('KLANG', 'video'), command, vars, None, False) #dont write intermediate msg?
                self.set_feedback(written, vars)
            case "Screenshot Feedback":
                #right now we are just calling screenshot..
                #get OCR, and transcribe.  This is delayed because of the transcription time..
                ocrtext, fname = self.save_screenshot(vars.get('KLANG', 'video'), '', vars.get('BBOX', None), True) #always OCR
                vars['OCRTEXT'] = ocrtext
                vars['FNAME'] = fname
                self.ocrtext = ocrtext
                written = self.transcriber.write(vars.get('KLANG', 'video'), command, vars, None, True) #write final message
                self.set_feedback(written, vars)
            case "_Click Link":
                self.show()
                #simulate click at link location if given.
            case "Time Zoom_":
                #zoom in or out around a time point.
                #preview info about this time..
                #update the main display with this?  
                i = 0
                similar = int(vars.get('SIMILAR', -1))
                if (similar != -1):
                    if (len(self.similar) > similar):
                        t = int(self.similar[similar]['timestamp']) #get time of this item
                        logger.info(f"Zooming to similar item at time: {t} with transcript: {self.similar[similar]['transcript']}")
                        self.show_tmap(t)
                        for (idx, item) in enumerate(self.similar):
                            vars[f'{idx}'] = f'{item["timestamp"]}  {item["transcript"][:50]}'
                        self.show_p({'type': '> ','cmd': command, 'vars': vars, 'timestamp': time.time()})

                        self.update_info(f'{t}\n{self.similar[similar]["transcript"]}')
#                        self.showQR(qrdata, cmds) #refresh QR display

            case "Time Jump" | "Time Zoom":
                t = float(vars.get('TIME', time.time()))
                w = float(vars.get('WINDOW', 86400)) #default 1 day
                s = float(vars.get('START', t-w/2))                              
                e = float(vars.get('END', t+w/2))
                similar = int(vars.get('SIMILAR', -1))
                if (similar != -1):
                    if (len(self.similar) >= similar):
                        #show info about this item, or jump to this time..  
                        t = int(self.similar[similar]['timestamp']) #get time of this item
                        s = t - w/2
                        e = t + w/2
                        self.set_time(t, s, e, w)
                        print(f"Similar items: {similar}")
                else:
                    self.add_setting('TIME', t, lang)
                    self.add_setting('WINDOW', w, lang)                
                    self.set_time(t, s, e, w)
                    print("Time Jump to: " + str(t) + " Start: " + str(s) + " End: " + str(e) + " Window: " + str(w))
                #set time locally.  
                #simulate click at link location if given.
            case "Set Speed":
 
                speed = float(vars.get('SPEED', '1.0'))
                adjust = float(vars.get('ADJUST', 1.0))
                logger.info(f"Setting speed with SPEED={speed}, ADJUST={adjust}, LANG={vars.get('LANG')}")
                lang = vars.get('LANG', lang)
                speed = self.set_speed(speed, adjust, lang)
                self.add_setting('SPEED', speed, lang)
                #video = playback speed
                #_meta = tick speed

                print(f"<<{lang}>>\n$$SPEED=" + str(speed))
            case "Tick":
                speed = self.get_setting('SPEED', 1.0, lang)
                print('Tick with speed: ' + str(speed))
                #jump forward by tick amount.  
                self.play_tmap(int(speed)) #play next item in tmap

            case "Tock":
                type = vars.get('type', 'video')
                speed = self.get_setting('SPEED', 1.0, lang)
                #jump backward by tick amount.
                if (type == 'video'):
                    self.play_tmap(int(-speed)) #play previous item in tmap
                elif (type == '_meta'):
                    #get trigger search of current recent key structure to other midi keys in transcriber..
                    current_time = int(vars.get('TIME', time.time()))
                    #rapidfuzz search for similar key structures in all midi in transcriber.  
                    midiarray = json.loads(vars.get('MIDI', "[]")) #load from string again..
                    print(f"<<{lang}>>\n$$MIDI=" + str(midiarray))
                    similar = []
                    if (random.random() < 0.2):  #only every once in a while.. too slow..
                        similar = self.transcriber.search_midi(midiarray, current_time)
                        print(f"Similar key structures found: {similar}")
                        print(f"<<{lang}>>\n$$SIMILAR=" + json.dumps(similar))
                    #what to do with this?  
                    #save it and show in QR?  
                    self.futuretree = self.transcriber.futuretree #map[lang] = ['..': '&&': '##':]
                    print(f"<<{lang}>>\n$$FUTURETREE=" + json.dumps(self.futuretree))
                    #display this in info section..
                    self.similar = similar

            case "Select Book":
                book = vars.get('book', 'None')
                self.add_setting('book', book, lang)
                context = vars.get('context', '')
                self.transcriber.current_book = book
                self.transcriber.current_context = context
                print(f"<<{lang}>>\n$$book=" + str(book))
                print(f"<<{lang}>>\n$$context=" + str(context))
                self.set_topic_info(book, context)
                self.bookhistory.insert(0, {'book': book, 'context': context, 'timestamp': time.time()}) #0 based index for most recent
                #bring vscode to front if not there..

                self.show_mrroboto()

            case "Select Window":
                wname = vars.get('**', 'None')

                #format this a bit nicer..
                self.set_topic_info('', wname)
                #bring vscode to front if not there..
                self.show_window(wname)

            case "Show Book":
                book = vars.get('book', 'None')
                context = vars.get('context', '')
                self.transcriber.current_book = book
                self.transcriber.current_context = context
                print(f"<<{lang}>>\n$$book=" + str(book))
                print(f"<<{lang}>>\n$$context=" + str(context))
                self.set_topic_info(book, context)
                self.show_mrroboto()
                
            case "Select Topic":
                topic = vars.get('topic', 'None')
                self.add_setting('topic', topic, lang)
                context = vars.get('context', '')
                self.supp_topics = vars.get('topics', '').split(',') #comma separated list of topics
                self.transcriber.current_topic = topic
                self.transcriber.current_context = context
                print(f"<<{lang}>>\n$$topic=" + str(topic))
                print(f"<<{lang}>>\n$$context=" + str(context))
                self.set_topic_info(topic, context)
                self.topichistory.insert(0, {'topic': topic, 'context': context, 'timestamp': time.time()}) #0 based index for most recent
                self.update_topic_history()
                #bring vscode to front if not there..
                self.show_mrroboto()
                #self.visualize_kg(self.transcriber.kg['**'], topic)

            case "Screenshot":
                print("Taking Screenshot")
                print(vars['BBOX'])
                self.draw_screen_box(vars.get('BBOX', self.geometry().getRect()))
                ocrtext, fname = self.save_screenshot(vars.get('KLANG', 'hotkeys'), vars.get('FNAME', ''), vars.get('BBOX', self.geometry().getRect()), True) #always OCR?
                vars['OCRTEXT'] = ocrtext
                vars['FNAME'] = fname
                self.ocrtext = ocrtext
                written = self.transcriber.write(vars.get('KLANG', 'video'), command, vars)
                self.set_feedback(written, vars)

                #send to QR In queue for processing by mykeys.  

            case "Screenshot_":
                self.draw_screen_box(vars.get('BBOX', None))

            case "Record Feedback_":
                #process feedback command.  
                logger.info(f'Processing record feedback command with vars: {vars}')
                #update QR info.. should display already..
            case "Tune In" | "Tune Out":
                t = float(vars.get('TIME', time.time()))
                w = float(vars.get('WINDOW', 86400)) #default 1 day
                s = float(vars.get('START', t-w/2))                              
                e = float(vars.get('END', t+w/2))

                #tune in window to display only this lang..
                lang = vars.get('LANG', 'ALL')


                if (lang != 'ALL'):
                    if (command == 'Tune In'):
                        self.langs.insert(0, lang) #move this lang to front of list to show first.
                    else:
                        if (lang in self.langs):
                            self.langs.remove(lang) #remove this lang from list to hide it.
                else:
                    if (command == 'Tune In'):                        
                        #show all langs..
                        self.langs = ['video', 'hotkeys', '_meta'] #for now hardcoded..
                    else:
                        self.langs = self.langs[:1] #for now just show first lang..

                self.set_time(s, e, w, t) #update display with new time window and lang settings.

            case "Open Browser":
                #refresh windows.  
                self.get_window_info() 

        lagtime = time.time() - lagtime
        if (command not in self.lagtracker):
            self.lagtracker[command] = {'_': lagtime, ':': 1}
        else:            
            self.lagtracker[command][':'] += 1
            self.lagtracker[command]['_'] += lagtime
        mycommand = self.lagtracker[command]
        if (lagtime > 0.5):
            logger.warning(f'!!LAG {lagtime:.2f}\n;> :={mycommand[":"]}\t_={mycommand["_"]:.2f}\n;> {command}\n {vars}')

        #add more commands as needed.


    def set_topic_info(self, topic, context):
        """Set the topic and context information in the UI."""
        #add status info and additional contextual info from history?..
        status_info = f"Status"
        if (topic):
            self.label_topic_info[0].setText(f'<table width="100%"><tr><td align="left">**{topic}</td>'
                                             f'<td align="right">{status_info}</td></tr></table>')
            self.label_topic_info[0].update()
        if (context):
            self.label_topic_info[1].setText(f'{context}') 
    #        self.label_topic_info[1].setText(f'{topic}<br>{context}') 

            self.label_topic_info[1].update()

    def send_window_info(self):
        #send window information to wherever it needs to go.
        #only do this when selecting a window..
        cmd = "Send Windows"
        vars = {}
        index = 0
        sorter = []
        for pid, w in self.windows.items():
            #send window information to wherever it needs to go.
            sorter.append(w)
        sorter.sort(key=lambda w: w['z_index'], reverse=True)
        for w in sorter:
            vars[index] = f"{w['title']}"
            index += 1
        logger.info(f'Sending window info: {vars}')

        self.inqueue.put(self.transcriber.write('hotkeys', cmd, vars, None, False)) #dont write intermediate msg?
        

    def show_window(self, wname):
        """Bring the specified window to the front if not already."""
        self.get_window_info() #update window info first.
        for pid, w in self.windows.items():
            if (wname.lower() in w['title'].lower()):
                logger.info(f'Bringing window to front: {w["title"]}')
                try:
                    #workaround for bringing window to front on Windows using pyautogui and win32gui
                    k = keyboard.Controller()
                    k.press(keyboard.Key.alt)

                    win32gui.SetForegroundWindow(w['hwnd'])
                    rect = win32gui.GetWindowRect(w['hwnd'])
                    win32gui.MoveWindow(w['hwnd'], self.startx, rect[1], rect[2]-rect[0], rect[3]-rect[1], True)
                    time.sleep(0.5)  # Small delay to ensure the window is brought to the front
                    k.release(keyboard.Key.alt)
                except Exception as e:
                    logger.error(f'Error bringing window to front: {e}')
                break

    def show_playwrighty(self):
        """Bring Playwright to the front if not already."""
        #get all windows, find mrroboto window and bring to front.  
        self.show_window('google chrome for testing')

    def show_mrroboto(self):
        """Bring MrRoboto to the front if not already."""
        #get all windows, find mrroboto window and bring to front.  
        self.show_window('mrroboto')

    def parseQRData(self, qrdata):
        """Parse the QR data and extract relevant information."""
        # For simplicity, just return the data as is.
        lines = qrdata.split('\n')
        currentcmd = ""
        vars = {}
        ret = []
        tempidx = 0
        lang = 'hotkeys'
        for idx, line in enumerate(lines):
#            logger.info(f'QR Data Line: {line}')
            type = line[:2] #first 2 chars is type
            if (len(line) > 3 and line[0] == '<' and line[1] == '<' and line[-2] == '>' and line[-1] == '>'):
                #lang command
                lang = line[2:-2]
            if (type == '> '):
                #command line internal command
                if (currentcmd != ""):
                    #store previous command before starting new one.
                    ret.append({'type': type, 'lang': lang, 'cmd': currentcmd, 'vars': vars, 'timestamp': time.time()})
                currentcmd = line[2:]
                sp = currentcmd.find('[')
                ep = currentcmd.find(']')
                if (sp != -1 and ep != -1 and ep > sp):
                    #has embedded variable, parse out and add to vars.
                    varstr = currentcmd[sp+1:ep]
                    currentcmd = currentcmd[:sp-1] #remove assumed white space
                    seq = varstr.split(',')
                    vars['SEQ'] = seq


            if (type == '$$'):
                #special trey data line
                if (len(line) == 2):
                    #execute command
                    if (currentcmd != ""):
                        type = '> '
                    vars['KLANG'] = lang
                    ret.append({'type': type, 'lang': lang, 'cmd': currentcmd, 'vars': vars, 'timestamp': time.time()})
#                    logger.info(f'Adding QR {type}: {currentcmd}')
                    currentcmd = ""
                    vars = {}

                else:
                    parts = line[2:].split('=')
                    if (len(parts) >= 2):
                        key = parts[0]
                        value = ''.join(parts[1:])
                        value = value.replace('\t', '\n')
                        vars[key] = value
            if (type == '~~'):
                #end of command
                w = line[2:].split('|')
                vars['KLANG'] = lang
                if (len(w) == 2):
                    word = w[0]
                    keys = w[1].split(',')
                    ret.append({'type': type, 'lang': lang, 'index': tempidx, 'word': word, 'keys': keys, 'timestamp': time.time()})
                    tempidx += 1
#                    logger.info(f'Adding QR {type}: {word}')
                if (len(w) == 3):
                    idx = w[0]
                    word = w[1]
                    keys = w[2].split(',')
                    ret.append({'type': type, 'lang': lang, 'index': idx, 'word': word, 'keys': keys, 'timestamp': time.time()})

        if (currentcmd != ""):
            #store last command if exists.
            ret.append({'type': type, 'lang': lang, 'cmd': currentcmd, 'vars': vars, 'timestamp': time.time()})                

        return ret
    
    # Snip...
    def runQRThread(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = QRWorker(self.queue)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

    def runQRInThread(self):
        # Step 2: Create a QThread object
        self.inthread = QThread()
        # Step 3: Create a worker object
        self.inworker = QRInWorker(self.inqueue, None, self)
        # Step 4: Move worker to the thread
        self.inworker.moveToThread(self.inthread)
        # Step 5: Connect signals and slots
        self.inthread.started.connect(self.inworker.run)
        self.inworker.finished.connect(self.inthread.quit)
        self.inworker.finished.connect(self.inworker.deleteLater)
        self.inthread.finished.connect(self.inthread.deleteLater)
        self.inworker.progress.connect(self.reportProgressIn)
        # Step 6: Start the thread
        self.inthread.start()



    import pyrebase

    def set_feedback(self, feedback, vars = {}, rerun=False):
        try:
            db = self.firebase.database()

            data = {"feedback": feedback}
            date_str = time.strftime("%Y%m%d")
            time_str = time.strftime("%H%M%S")
            db.child("channels").child(self.myuser['localId']).child("feedback").child(date_str).child(time_str).child(self.myuser['localId']).set(data, self.myuser['idToken'])
        except Exception as e:
            #if fail
            if (rerun):
                return
            auth = self.firebase.auth()
            user = auth.refresh(self.myuser['refreshToken'])
            self.myuser = user
            self.set_feedback(feedback, vars, True)

    def start_record(self):
        try:
            db = self.firebase.database()

            data = {"status": "recording", "timestamp": time.time()}
            #get date YYYYMMDD
            date_str = time.strftime("%Y%m%d")
            time_str = time.strftime("%H%M%S")
            mydata = db.child("channels").child(self.myuser['localId']).shallow().get(self.myuser['idToken'])
            print(mydata.val())
            db.child("channels").child(self.myuser['localId']).update(data, self.myuser['idToken'])
            data = {"feedback": "test"}
            print(data)
            db.child("channels").child(self.myuser['localId']).child("feedback").child(date_str).child(time_str).child(self.myuser['localId']).set(data, self.myuser['idToken'])
        except Exception as e:
            #if fail
            auth = self.firebase.auth()
            user = auth.refresh(self.myuser['refreshToken'])
            self.myuser = user


    def login(self):
        auth = self.firebase.auth()
        email = self.cfg["trey"]["user"]
        password = self.cfg["trey"]["pwd"]
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            # Extract the UID (localId) from the user object
            self.myuser = user
#            uid2 = user['userId']
            print(f"Successfully signed in. User UID: {self.myuser['localId']} {self.myuser['idToken']}")
            logger.info(f'Firebase login successful for {email}, UID: {self.myuser['localId']}')
            self.start_record()
        except Exception as e:
            logger.error(f'Firebase login failed: {e}')
            print(f'Firebase login failed: {e}')


    def getColorFromSequence2(self, seqno, format="rgb"):
        wbarray = [0,1,0,1,0,0,1,0,1,0,1,0] #for now fixed from C
        seqno = seqno % len(wbarray)
        if wbarray[seqno] == 0:
            return "rgb(0,0,0)" if format == "rgb" else "#ffffff"
        else:
            return "rgb(255,255,255)" if format == "rgb" else "#000000"

        

    def getColorFromSequence(self, seqno, format="rgb"):
        NUM_COLORS = 6
        """
        Generates a color string (RGB or hexadecimal) based on a sequence number.
        """
        adjust = int(seqno / NUM_COLORS)  # Ensure adjust is an integer
        adjust = adjust % (NUM_COLORS / 2)
        r = 0
        g = 0
        b = 0

        if seqno % NUM_COLORS == 0:
            r = 255
        elif seqno % NUM_COLORS == 1:
            r = 255
            g = 127
        elif seqno % NUM_COLORS == 2:
            r = 255
            g = 255
        elif seqno % NUM_COLORS == 3:
            g = 255
        elif seqno % NUM_COLORS == 4:
            b = 255
        elif seqno % NUM_COLORS == 5:
            r = 148
            b = 211

        if adjust > 0:
            r = int(r * (1 - (adjust / NUM_COLORS)))
            g = int(g * (1 - (adjust / NUM_COLORS)))
            b = int(b * (1 - (adjust / NUM_COLORS)))

        if format == "hex":
            def toHex(c):
                return c.to_bytes(1, 'big').decode('hex')
            return "#" + toHex(r) + toHex(g) + toHex(b)
        else:
            return "rgba(" + str(r) + "," + str(g) + "," + str(b) + ",1)"

    def init_fb(self):
        databaseURL = self.cfg["firebase"]["fbconfig"]["databaseURL"]
            # Init firebase with your credentials
        import pyrebase
        self.firebase = pyrebase.initialize_app({'apiKey': self.cfg["firebase"]["fbconfig"]["apiKey"], 'authDomain': self.cfg["firebase"]["fbconfig"]["authDomain"], 'databaseURL':databaseURL, 'storageBucket': self.cfg["firebase"]["fbconfig"]["storageBucket"]})    
        self.login()


    def show_tray(self, qapp):
        # 2. Create the system tray icon
        image = QImage(64, 64, QImage.Format_ARGB32)
        image.fill(0x00ff0000) # Fill with transparent background

        # ... use QPainter to draw on the image if needed ...
        logger.info('Creating system tray icon')
        pixmap = QPixmap.fromImage(image)
        icon = QIcon(pixmap) # Use the pixmap as the icon
        tray = QSystemTrayIcon()
        tray.setIcon(icon)
        tray.setVisible(True)

        # 3. Create a context menu
        menu = QMenu()

        # Define menu actions
        # Action to show a message
        show_action = QAction("Show Message")
        show_action.triggered.connect(lambda: QMessageBox.information(None, "PyQt5 Systray", "Hello from the tray app!"))
        menu.addAction(show_action)

        # Add a separator
        menu.addSeparator()

        # Action to quit the application
        quit_action = QAction("Quit")
        quit_action.triggered.connect(qapp.quit)
        menu.addAction(quit_action)

        # 4. Add the menu to the tray icon
        tray.setContextMenu(menu)

        # Optional: Add a tooltip (hover text)
        tray.setToolTip("My PyQt5 Tray App")

        # Optional: Show a balloon message on launch (Windows/Linux)
        tray.showMessage("My PyQt5 Tray App", "Application started in the background", QSystemTrayIcon.Information, 2000)

    def __init__(self, q=None, inq=None, cfg=None, qapp=None):
        super().__init__()
        self.mk = None
        self.highlightrect = {'x': 100, 'y': 100, 'width': 200, 'height': 200}
        self.bboxes = [] #list of drawn boxes..
        self.highlighton = False
        self.startx = 0
        self.queue = q
        self.inqueue = inq
        self.qapp = qapp
        self.cfg = cfg
        self.myuser = None
        self.geo = None
        self._bbox = None
        self.qr_in = []
        self.qr_out = []
        self.ocrtext = ""
        self.windowlabels = {} #list of window details by pid
        self.windowcounter = 0
        self.screenshots = [] #list of screenshots per monitor
        self.topichistory = []
        self.bookhistory = []
        self.reading_topic = None
        self.filters = {}
        self.lagtracker = {} #track lag for each command, to detect slow commands and warn user.
        self.windows = {} #current windows by pid, updated by window thread.
        self.kg = None
        self.kgid = 0
        self.video_cache = [] #running list of files which were played..
        self.video_cache_index = 0
        self.qr_cache = [] #cache of QR data and structures.
        self.qr_cache_index = 0 #index for navigating through the QR cache.
        #allow for selection for any of the past n videos..{'_': img or video, '**': fname, '(': st, ')': et, '..': current_time}
        self.myactions = [] #list of current actions to display, updated by QR commands.
        self.trey_data = {} #current data to display, updated by QR commands and transcription.
        self.similar = [] #current similar items to display, updated by QR commands and transcription.
        self.startup_lag = time.time()
        #rerunning with this may require separate queue, or indicator for rerun in the data.  For now same..
        self.transcriber = transcriber.transcriber(self, mykeys.MyKeys(config.cfg), self.queue) #maybe want different queue..
        #need to load book to have same topics as _meta.. ugh..
        book = self.transcriber.read('book', self.transcriber.getTime(-180), None, './book/')

        #for now just fixed 30 days max info.  
        self.tmap = [] #current transcripts in time window, sorted by time.  
        self.aggmap = [] #aggregated info for current time window, updated as new transcripts come in.

        self.s = 0 #current start time of window
        self.e = 0 #current end time of window
        self.langs = ['hotkeys', 'video'] #read and show in main display
        self.currentsound = None #current sound being played.
        self.currentvideo = None #current video being played.
        self.speed = 1.0
        self.playback_speed = 1.0

        self.mylayout = QVBoxLayout()

        if (self.cfg is not None and 'firebase' in self.cfg):
            self.init_fb()
        # set the title



        color = "red" #for now just red, can use color sequence later. Not very visible with several colors..
        self.color = "red"

        self.setWindowOpacity(config.custom_settings.get('OPACITY', 0.8)) #default opacity, can be set by QR command as well.
        #Qt.WA_TransparentForMouseEvents | Qt.WindowTransparentForInput to make click-through
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WA_TransparentForMouseEvents | Qt.WindowTransparentForInput)
        screens = self.qapp.screens()
        logger.info('Listing available screens')
        primary_screen = self.qapp.primaryScreen()
        if len(screens) == 1:
            logger.info('Only one screen detected, add a second monitor to use trey overlay.')
        for i, s in enumerate(screens):
            logger.info(f'Screen {i}: {s.name()} - Size: {s.size()}')
            if (s.name() != primary_screen.name()):
                # This is a secondary screen
                logger.info(f'Screen {i} is secondary')
                geometry = s.geometry()
                # set the geometry of window
                # setting  the geometry of window
                #add window to second monitor if available
                self.setGeometry(geometry.x(), geometry.y(), geometry.width(), geometry.height())
                self.startx = geometry.x()
                self.geo = geometry
                self._bbox = [0,geometry.width(), 0,geometry.height()]

                print(f'Setting window to second monitor at {geometry.x()},{geometry.y()} size {geometry.width()}x{geometry.height()}')
                self.setWindowTitle("Trey - " + s.name())

#        self.setGeometry(60, 60, 600, 400)
        for i in range(100):
            self.windowlabels[str(i)] = QLabel(f'Label {i}', self)
        # creating a label widget


        self.video_widget = QVideoWidget(self)
        self.video_widget.setGeometry(0, 0, self.width(), self.height()) #set up location
#        self.video_widget.setGeometry(int(self.width()*0.2), int(self.height()*0.2), int(self.width()*0.5), int(self.height()*0.5)) #set up location
#        self.set_geometry(self.video_widget, 0.2, 0.2, 0.5, 0.5) #set up location
#        self.video_widget.hide() #hide by default
        self.video_widget.show()
        self.video_player = QMediaPlayer()
        self.video_player.setVideoOutput(self.video_widget)

        self.video_overlay = QPaintedLabel(self) 
        self.video_overlay.setGeometry(0, 0, self.width(), self.height())
        self.video_overlay.setStyleSheet(f"background-color: rgba(0, 0, 0, 0);color: {color};") #transparent overlay for text
        self.video_overlay.setAlignment(Qt.AlignCenter)
        self.video_overlay.setText("Hello Overlay")
        self.video_overlay.show()


        #left mid
        #BBOX(0,0.2,0.2,0.7)

        self.label_filter_info = []
        for i in range(25): #info 0-3, and addl potential filter/param labels
            self.label_filter_info.append(QLabel("transparent ", self))
            self.init_label(self.label_filter_info[i], 0, 0.2+0.02*i, 0.2, 0.02, fontsize=8)


        #mid right
        #BBOX(0.8,0.1,0.2,0.6)
        self.label_info = QLabel("transparent ", self)
        # moving position
        self.init_label(self.label_info, 0.8, 0.1, 0.2, 0.6, fontsize=12)


        #mid mid
        #BBOX(0.3,0.2,0.7,0.7)
        self.label_main = []
        for i in range(3):
            self.label_main.append(QLabel("transparent ", self))
            self.init_label(self.label_main[i], 0.1+0.2*i, 0.2, 0.2, 0.5, fontsize=10)
#            self.label_main.append(QLabel("transparent ", self.video_widget))
#            self.init_label(self.label_main[i], 0.33*i, 0, 0.33, 1)
            # moving position
            self.label_main[i].setText("Main Label")
#            self.label_main[i].raise() #bring to front
        

        #bot right
        #BBOX(0.7,0.7,0.9,0.9)
        self.label_qr = QLabel(self)
        #move to bottom right corner
        self.init_label(self.label_qr, 0.7, 0.75, 0.2, 0.2)

        self.label_ps = []
        wbarray = [0,1,0,1,0,0,1,0,1,0,1,0] #for now fixed from C
        colorarray = [""]
        fullwidth = self.geo.width()
        pwidth = int(fullwidth/5)
        fontsize = 16
        for i in range(24): #assume 25 key range for now..
            self.label_ps.append(QLabel(self))
            color = self.getColorFromSequence2(i) #wb only for now..
            if (wbarray[i%len(wbarray)] == 0):
                self.label_ps[i].setStyleSheet(f"background-color: rgba(255, 255, 255, 1);color: {color};border: 1px solid black;")
            else:
                self.label_ps[i].setStyleSheet(f"background-color: rgba(63, 63, 63, 1);color: {color};border: 1px solid black;")
            font = QFont("Courier", fontsize-wbarray[i%len(wbarray)]*2) # Specify font family and size
            self.label_ps[i].setFont(font)
#            self.label_ps[i].setStyleSheet(f"background-color: rgba(255, 255, 255, 1);color: {color};")
            self.label_ps[i].move(int(pwidth*1.5+(i//12)*pwidth+wbarray[i%len(wbarray)]*20), int(self.geo.height() - (0.65*pwidth-(i%12)*fontsize)))
            self.label_ps[i].setFixedHeight(fontsize-wbarray[i%len(wbarray)]*2)
            self.label_ps[i].setFixedWidth(pwidth-wbarray[i%len(wbarray)]*40)
            self.label_ps[i].setTextFormat(Qt.PlainText)

        #bot left
        #BBOX(0,0.8, 0.2, 1)
        self.label_p = QLabel(self)
        # 2. Set a monospaced font
        font = QFont("Courier", fontsize-2) # Specify font family and size
        font.setFixedPitch(True)    # Ensure it uses the fixed pitch version if available
        self.label_p.setFont(font)    # Apply the font to the label        
        self.label_p.setStyleSheet(f"background-color: rgba(255, 255, 255, 1);color: {self.color};border: 1px solid black;")
        self.label_p.move(0, self.geo.height() - pwidth)
        self.label_p.setFixedHeight(pwidth)
        self.label_p.setFixedWidth(pwidth)
        self.label_p.setWordWrap(True)
#        self.label_p.setTextFormat(Qt.PlainText)
#        self.label_p.setStyleSheet("background-image: url(path/to/your/image.png); border: 2px solid blue;")

        metrics = QFontMetrics(font)
        # Using boundingRect is generally more accurate than width() or horizontalAdvance()
        w = metrics.boundingRect("X").width()
        h = metrics.boundingRect("X").height()
        self.pwidth = self.geo.width()/w
        self.pheight = 200/h
        logger.info(f'MyWindow {self.pwidth} X {self.pheight} loaded')

#        QFontDatabase.addApplicationFont("../fonts/FRBCistercian.otf")
#for now no custom fun font.. 
#just use UTF-8 characters and a monospaced font.

        #bot mid
        #BBOX(0.2,0.01, 0.02, 0.6, 0.06)
        self.label_times = []
        for i in range(2):
            #show event types for each time point.

            t = QLabel(f'Time{i}', self)
            t.setFont(font)    # Apply the font to the label        
            t.move(int(self.geo.width()*0.2), int(self.geo.height()*0.02*(i*1.6+1.5)))
            t.setFixedHeight(h+2)
            w = metrics.boundingRect(chr(0x2160)).width()
            t.setFixedWidth(int(w*60*1.5)) #60 char of time info.. 36-96 ? 
            t.setStyleSheet(f"background-color: rgba(255, 255, 255, 1);color: {self.color};")
            #some reason <pre> makes formatting a bit nicer..
            ltext = ""
            startchar = 0x2160 #start of roman numeral characters, just to have some unique chars to test with for now.
            startchar = 0x30A1 #start of katakana characters, just to have some unique chars to test with for now.
            for j in range(60):
                ltext += chr(startchar+j) #white square as placeholder for now.
#            t.setText('<pre>\u2160\u2160\u2160\u2160\u2160</pre>') #roman numeral 1 as placeholder for now.
            t.setText(f'<pre>{ltext}</pre>')

            t.adjustSize()

            self.label_times.append(t)

        #top left
        #BBOX(0,0.01, 0.02, 0.1, 0.1)
        self.label_timeinfo = []
        for i in range(4):
            self.label_timeinfo.append(QLabel(self))
            self.label_timeinfo[i].setStyleSheet(f"background-color: rgba(255, 255, 255, 1);color: {self.color};border: 1px solid black;")
            font = QFont("Courier", fontsize-4) # Specify font family and size
            self.label_timeinfo[i].setFont(font)
            self.label_timeinfo[i].move(int(self.geo.width()*0.08), int(self.geo.height()*0.02*(i+1.5)))
            self.label_timeinfo[i].setFixedHeight(fontsize-2)
            self.label_timeinfo[i].setFixedWidth(int(self.geo.width()*0.12))
            self.label_timeinfo[i].setTextFormat(Qt.PlainText)


        self.label_topic_info = []
        for i in range(2):
            self.label_topic_info.append(QLabel(self))
            self.label_topic_info[i].setStyleSheet(f"background-color: rgba(255, 255, 255, 1);color: {self.color};border: 1px solid black;")
            font = QFont("Courier", fontsize-4) # Specify font family and size
            self.label_topic_info[i].setFont(font)
            self.label_topic_info[i].move(int(self.geo.width()*0.1), int(self.geo.height()*(0.08+0.02*(i+1))))
            self.label_topic_info[i].setFixedHeight(int(self.geo.height()*(0.02+(0.06*i)))) #larger height for context info..
            self.label_topic_info[i].setFixedWidth(int(self.geo.width()*0.6))
#            self.label_topic_info[i].setTextFormat(Qt.PlainText)

        # show all the widgets
        self.move(self.startx, 0) #why we need to do this again?  
        self.show()
        self.showQR("Starting Trey Overlay")
        #hide after a few seconds
        #workaround, something wrong with the PyQt if we hide this immediately
        import extensions.trey.trey as trey

        
        t2 = threading.Timer(20, trey._get_window_info, args=(self,))
        t2.start()  # Start the timer in a new thread
        t = threading.Timer(15, trey._hide, args=(self, "Hello from Timer!"))
        t.start()  # Start the timer in a new thread
        logger.info('Window created')
        self.read(self.langs, None, None) #initial read of all data, can be filtered by time later.

        self.runQRThread() #
        self.runQRInThread() #start thread to detect incoming QR data from other apps or locations..


#        self.show_tray(self.qapp) #show system tray icon for quick access to some functions.

        #start internal thread to check the queue for updates.  
        #and update the window when there is new data.  


    def on_click(self, x, y, button, pressed):

        if pressed:
            temp = win32gui.WindowFromPoint((x, y))
            if (self.in_trey((x,y))): #only capture second monitor clicks
                action = {'button': str(button), 'x': x, 'y': y, 'hwnd': temp, 'act': 'click'}
        #        action = f'Mouse clicked at ({x}, {y}) with {button}'
                self.update_actions(temp, action)

    def update_actions(self, hwnd, action):

        """Update the actions for the given window handle."""
        threadid, procid = win32process.GetWindowThreadProcessId(hwnd)
        action['threadid'] = threadid
        action['procid'] = procid
        if (hwnd in self.windows):
            if 'actions' not in self.windows[hwnd]:
                self.windows[hwnd]['actions'] = []
            self.windows[hwnd]['actions'].append(action)
            if (len(self.windows[hwnd]['actions']) > 100):
                logger.debug(f'Removing oldest action from {hwnd} actions list')
                self.windows[hwnd]['actions'].pop(0)

        logger.info(f'{action}')
        self.myactions.append(action)  # Append to global actions list
        #remove if too many actions
        if len(self.myactions) > 100:
            logger.debug('Removing oldest action from global actions list')
            self.myactions.pop(0)


    def update_window_data(self, hwnd, title, rect, initobj=None):

        if (hwnd not in self.windows):
            self.windows[hwnd] = {}
            if (initobj is not None):
                self.windows[hwnd] = initobj

        self.windows[hwnd]['title'] = title
        self.windows[hwnd]['rect'] = rect
        self.windows[hwnd]['hwnd'] = hwnd
        logger.info(f'{title} at {rect}')


    def window_list_callback(self, hwnd, extra):
        if win32gui.GetWindowText(hwnd) != "":
            # Get window title
            title = win32gui.GetWindowText(hwnd)
            # Get window position and size (left, top, right, bottom)
            try:
                rect = win32gui.GetWindowRect(hwnd)
                if (title.startswith("Trey - ")):
                    #get the rect we need to be aware of.  
                    #expand rect some windows have odd borders.  
                    logger.info(f"Found Trey window: {title} at {rect}")
                    x, y, right, bottom = rect
                    x -= 8  # Adjust for window borders
                    y -= 8
                    right += 8
                    bottom += 8
                    rect = (x, y, right, bottom)
                    self.trey_data['rect'] = rect
                    self.trey_data['hwnd'] = hwnd
                    self.trey_data['title'] = title

                trect = (0,0,0,0)
                if ('rect' in self.trey_data):
                    trect = self.trey_data['rect']
        #            trect[0] += 50 #some margin for overlapping windows.  


                # Check if the window is fully within the trey window
                if ((self.in_trey(rect) and win32gui.IsWindowVisible(hwnd) and title !='PopupHost') 
                        or ('mrroboto' in title.lower())): #only monitor visible windows.. and ignore popuphost..
                    threadid, procid = win32process.GetWindowThreadProcessId(hwnd)
                    self.update_window_data(hwnd, title, rect, {'threadid': threadid, 'procid': procid, 'hwnd': hwnd})
                    x, y, right, bottom = rect
                    width = right - x
                    height = bottom - y
                    action = {'title': title, 'rect': rect, 'hwnd': hwnd, 'procid': procid, 'threadid': threadid, 'act': 'init'}
                    self.update_actions(hwnd, action)
            except Exception as e:
                logger.error(f'Error processing window {hwnd} {title}: {e}')
        return True # Continue enumeration    

    def in_trey(self, rect):
        """Check if the rectangle is within the trey window."""
        if ('rect' in self.trey_data):
            trect = self.trey_data['rect']
#            logger.debug(f"Checking if {rect} is in {self.trey_data['rect']}")
    #        print(f"Checking if {rect} is in {self.trey_data['rect']}")
            if (len(rect) == 4 and len(trect) == 4):
                return (rect[0] >= trect[0] and rect[1] >= trect[1] and rect[2] <= trect[2] and rect[3] <= trect[3])
            elif (len(rect) == 2 and len(trect) == 4): #allow for point check
                return (rect[0] >= trect[0] and rect[1] >= trect[1] and rect[0] <= trect[2] and rect[1] <= trect[3])
        return False


    def get_top_z(self): #this also initializes z_index for self.windows
        hwnd = win32gui.GetTopWindow(0)
        z_index = 0
        topz = None
        logger.debug("Starting z-index enumeration of windows in trey area")
        while hwnd:
            threadid, procid = win32process.GetWindowThreadProcessId(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            if (self.in_trey(rect)):
                if (topz is None and hwnd in self.windows and win32gui.IsWindowVisible(hwnd)):
                    topz = hwnd
                if (hwnd in self.windows):
                    logger.debug(f"Found window in trey at z index {z_index}: {self.windows[hwnd]['title']} with rect {rect}")
                    self.windows[hwnd]['z_index'] = z_index
            hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
            z_index += 1   
        if (topz is not None):
            logger.debug(f"Got top z window: {topz} at index {self.windows[topz]['z_index']}")     
        return topz
    
    def get_window_info(self):
        self.windows = {} #reset windows, will be updated by callback.  This is to remove windows that are closed or no longer in trey area.
        if ('rect' not in self.trey_data): #initialize trey..
            win32gui.EnumWindows(self.window_list_callback, None)    

        win32gui.EnumWindows(self.window_list_callback, None)    

        self.active_window = self.get_top_z() #get top z window in trey area, not necessarily active window.
        self.send_window_info()
        self.updateLabels(self.windows) #gives info for all windows


    def get_kg_img(self, nn):
        img = Image.new("RGB", (120, 20), "blue")
        draw = ImageDraw.Draw(img)                
        #add custom text here for selection info..
        font = ImageFont.truetype("arial.ttf", size=36)
        position = (10, 10)  # Position to draw the text
        text_content = f"{nn}"
        text_color = (255, 255, 255)  # White color in RGB

        draw.text(position, text_content, fill=text_color, font=font)
        return img

    def add_to_kg(self, kg, n, l):
        if (len(n) > 3): #only add entities with length > 3 to avoid clutter
            if (not kg.has_node(n)):
                kg.add_node(n, count=0, myid=self.kgid, label=l)
                self.kgid += 1
            else:
                kg.nodes[n]['count'] = kg.nodes[n].get('count', 0) + 1 #increment count if already exists
                kg.nodes[n]['label'] = l
        else:
            return False
        return True
    
    def make_kg(self, graph, entities, topic=""):
        if (topic == ""):
            topic = self.transcriber.current_topic
        if not graph:
            return None
        if not isinstance(graph, list):
            return None
        logger.info(f'{graph}')

        if (isinstance(entities, list)):
            if (self.kg is None):
                self.kg = nx.Graph(name=topic) 
            kg = self.kg
            for ent in entities:
                if ('text' not in ent):
                    logger.info(f'!!--make_kg\nent={ent}')
                    continue
                e = ent['text']
                l = ent['label']
                #images too much overhead, find different way to customize..
#                img = self.get_kg_img(sel)
#                img2 = self.get_kg_img(sel+1)
#                kg.add_node(s, image=img) #param for image?  
#                kg.add_node(o, image=img2) 
                self.add_to_kg(kg, e, l)
    
        if (isinstance(graph, list)):
            if (self.kg is None):
                self.kg = nx.DiGraph(name=topic) 
            kg = self.kg
            for rel in graph:
                if ('head' not in rel or 'tail' not in rel or 'relation' not in rel or 'score' not in rel):
                    logger.info(f'!!--make_kg\nrel={rel}')
                    continue
                s = rel['head']['text']
                ls = rel['head']['type']
                o = rel['tail']['text']
                lo = rel['tail']['type']
                if (len(s) < 3 or len(o) < 3): #only add entities with length > 3 to avoid clutter
                    continue
                r = rel['relation']                
                score = rel['score']


                #images too much overhead, find different way to customize..
#                img = self.get_kg_img(sel)
#                img2 = self.get_kg_img(sel+1)
#                kg.add_node(s, image=img) #param for image?  
#                kg.add_node(o, image=img2) 
                if (self.add_to_kg(kg, s, ls) and self.add_to_kg(kg, o, lo)):
                    kg.add_edge(s, o, type=r)
        #kg.remove_nodes_from(list(nx.isolates(kg))) #remove isolated nodes.. never shown anyway..
        return kg
    

    def visualize_kg(self, kg, topic="ALL"):
        #dpi 96 assume..
        #why we cant pass in pixels?  


        width_inches = self.geo.width() / 96
        height_inches = self.geo.height() / 96

        if (topic == "ALL" or topic not in kg):
            node1 = list(kg.nodes())[random.randint(0, len(kg.nodes())-1)]
            logger.info(node1)
            fname = f"./temp/kg/{node1}.png"
            logger.info(f'Topic {topic} not found in KG, visualizing entire graph with {len(kg.nodes())} nodes and {len(kg.edges())} edges')
            subgraph = nx.ego_graph(kg, node1, radius=3) #get subgraph around first node with radius 1, can adjust as needed.
        else:
            fname = f"./temp/kg/{topic}.png"
            subgraph = nx.ego_graph(kg,topic, radius=3) #get subgraph around topic with radius 2, can adjust as needed.
            if (subgraph.number_of_nodes() < 5): #if too small, just use entire graph
                subgraph = nx.ego_graph(kg,topic, radius=4) #larger..
            elif (subgraph.number_of_nodes() > 100): #if too large, just use entire graph
                subgraph = nx.ego_graph(kg,topic, radius=2) #smaller..
        logger.info(f'--{fname}')
        if (os.path.exists(fname) and os.path.getmtime(fname) > time.time() - 86400): #if file exists and is less than 1 day old, use it instead of regenerating
            self.play_video(fname) #for now just use video player to show image, can adjust later for better performance if needed.
            return
        else:
            
            directory_path = os.path.dirname(fname)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

        logger.info(f'Visualizing knowledge graph for topic: {topic} with {len(subgraph.nodes())} nodes and {len(subgraph.edges())} edges')

        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'] #7-loop
        color_map = {label: colors[i % len(colors)] for i, label in enumerate(self.cfg["kg"]["entity_labels"])} if self.cfg and "kg" in self.cfg and "entity_labels" in self.cfg["kg"] else {}
        edge_color_map = {label: colors[i % len(colors)] for i, label in enumerate(self.cfg["kg"]["relation_labels"])} if self.cfg and "kg" in self.cfg and "relation_labels" in self.cfg["kg"] else {}

        node_colors = [color_map[subgraph.nodes[n]["label"]] for n in subgraph.nodes]
        edge_colors = [edge_color_map[subgraph.edges[e]["type"]] for e in subgraph.edges]
#        print(subgraph)
        plt.rc('text', usetex=False) # Ensure global setting is False
        fig, ax = plt.subplots(figsize=(width_inches, height_inches), dpi=96)
#        nx.draw(subgraph, with_labels=True)
        # 2. Compute layout positions
        pos = nx.spring_layout(subgraph)

        nx.draw(subgraph, pos, with_labels=True, node_color=node_colors, node_size=500, edge_color=edge_colors, font_size=10)

        # 4. Extract and draw the relationship labels if not too many edges just to avoid cluttering the graph
        if (subgraph.number_of_edges() < 500):
#            ax.set_aspect('equal')
            edge_labels = nx.get_edge_attributes(subgraph, "type")
            nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels, rotate=True, node_size=500, font_size=8, font_color='blue') 

#        graph_text = nx.write_network_text(subgraph, sources=[topic])
#        ax.text(0.5, 0.01, graph_text, transform=ax.transAxes, fontsize=8, verticalalignment='bottom', horizontalalignment='center', wrap=True)
        # 3. Save the figure to a file
        plt.savefig(fname, format="png")
#        print(f"Graph saved as {fname}")
        #show png result as overlay..
        self.play_video(fname) #for now just use video player to show image, can adjust later for better performance if needed.




    #not used..
    import pyqtgraph as pg
    def visualize_networkx_pyqtgraph(self, graph):
        # 1. Calculate node positions using a NetworkX layout algorithm
        # fruchterman_reingold_layout is a common "spring layout"
        pos = nx.fruchterman_reingold_layout(graph)

        # 2. Format positions for PyQtGraph: an Nx2 numpy array of (x, y)
        # The order of positions must match the order of nodes in the graph
        nodes_list = list(graph.nodes())
        positions = np.array([pos[node] for node in nodes_list])

        # 3. Format edges for PyQtGraph: an Mx2 numpy array of (node_index_1, node_index_2)
        # PyQtGraph requires zero-based indices corresponding to the position array
        node_to_index = {node: i for i, node in enumerate(nodes_list)}
        edges = np.array([(node_to_index[u], node_to_index[v]) for u, v in graph.edges()])

        mw = self.video_overlay
        view = pg.GraphicsLayoutWidget()
        mw.setCentralWidget(view)
        p = view.addPlot(title="Graph Visualization")

        # Create the GraphItem
        graph_item = pg.GraphItem(nodeSymbols='o', symbolSize=10, pxMode=False)
        p.addItem(graph_item)

        # Set the graph data
        graph_item.setData(pos=positions, edges=edges,
                        # Optional: set colors or other properties
                        edgePen=pg.mkPen(color=(200, 200, 200), width=1),
                        symbolBrush=(50, 50, 150, 200))

        # Optional: adjust view to fit the graph
        p.autoRange()

        mw.show()

    def init_label(self, label, x, y, w, h, color='red', fontsize=10):
        label.setTextFormat(QtCore.Qt.RichText)
        label.setStyleSheet(f"background-color: rgba(255, 255, 255, 1);color: {color};border: 2px solid black;font-size: {fontsize}pt;")
        label.setAlignment(Qt.AlignTop)
        label.adjustSize()
        label.setWordWrap(True)
        self.set_geometry(label, x, y, w, h)


    def set_geometry(self, widget, x, y, w, h):
        widget.adjustSize()
        widget.move(int(self.geo.width()*x), int(self.geo.height()*y))
        widget.setFixedWidth(int(self.geo.width()*w))
        widget.setFixedHeight(int(self.geo.height()*h))

    def save_screenshot(self, lang='hotkeys', fname='', bbox=None, ocr=False):
        """Save a screenshot of the current window."""
        screen = self.qapp.primaryScreen()
        screens = self.qapp.screens()
        logger.info('saving screenshot')
        screenshot = None
        for i, s in enumerate(screens):

            screenshot = s.grabWindow( 0 ) # 0 is the main window, you can specify another window id if needed


        self.screenshots.append(screenshot)
        logger.info('Capturing Screen')

        now = datetime.now()
        if (fname == ''):
            fname = f'{now.strftime("%Y%m%d_%H%M%S")}.png'
        folder = f'../transcripts/{lang}/' 
        if not os.path.exists(folder):
            os.makedirs(folder)
        geometry = self.geometry()

        screenshot.save(folder + fname, 'png')
        logger.info(f'Screenshot saved as {folder + fname}')
        ocrtext = ""
        if (ocr):
            #do OCR on screenshot
            img = Image.open(folder + fname)
            #get bbox area
            if (bbox is not None):
                bbox = bbox.split(',')
                bbox = [int(b) for b in bbox]
                bbox = self.format_bbox(bbox)
                img = img.crop((bbox[0]-self.geo.x(), bbox[2]-self.geo.y(), bbox[1]-self.geo.x(), bbox[3]-self.geo.y()))
                logger.info(f'Cropping image to bbox: {bbox}')

            ocrtext = pytesseract.image_to_string(img)

        return ocrtext, folder + fname
        
    def format_bbox(self, bbox):
        if (bbox[0] > bbox[1]):
            x1 = bbox[0]
            bbox[0] = bbox[1]
            bbox[1] = x1
        if (bbox[2] > bbox[3]):
            y1 = bbox[2]
            bbox[2] = bbox[3]
            bbox[3] = y1
        return bbox


    def get_qr_cache(self, cacheno):
        # Implement the logic to retrieve the video from cache using cacheno
        self.qr_cache_index = self.qr_cache_index + cacheno

        logger.info(f'Getting QR from cache with cacheno: {self.qr_cache_index}')
        if (self.qr_cache_index < 0):
            self.qr_cache_index = 0
        elif (self.qr_cache_index >= len(self.qr_cache)):
            self.qr_cache_index = len(self.qr_cache) - 1
        if (len(self.qr_cache) > 0 and self.qr_cache_index >= 0 and self.qr_cache_index < len(self.qr_cache)):
            logger.info(f'Retrieving QR from cache at index: {self.qr_cache_index}')
            result = self.qr_cache[self.qr_cache_index]
            logger.info(f'{result["data"]}')
            self.showQR(result['data'], result['struct'])
            return result
        return None

    def get_video(self, cacheno):
        # Implement the logic to retrieve the video from cache using cacheno
        cacheno = abs(cacheno)  # Ensure cacheno is non-negative actual value is -12-12
        self.video_cache_index = self.video_cache_index + cacheno

        if (self.video_cache_index < 0):
            self.video_cache_index = 0
        elif (self.video_cache_index >= len(self.video_cache)):
            self.video_cache_index = len(self.video_cache) - 1
        if (len(self.video_cache) > 0 and self.video_cache_index >= 0 and self.video_cache_index < len(self.video_cache)):
            result = self.video_cache[self.video_cache_index]
            if result:
                fname = result["**"]
                self.play_video(fname)
            else:
                logger.info(f'No video found in cache for cacheno: {cacheno}')

    def play_video(self, fname):
        """Play a video file on the overlay."""
        logger.info(f'Playing video: {fname}')
        for i in range(3):
            self.label_main[i].hide() #hide main labels when playing video, can adjust as needed.
        self.label_qr.hide()
        for l in self.label_ps:
            l.hide()
        for l in self.label_filter_info:
            l.hide()
        self.label_info.hide()
        self.label_topic_info[0].hide()
        self.label_topic_info[1].hide()
        self.label_p.hide()
        self.video_overlay.hide()


        ext = os.path.splitext(fname)[1].lower()
        if (self.currentvideo == fname):
            logger.info('Video already playing')
#            self.video_player.setMedia(QMediaContent(QUrl.fromLocalFile(fname)))
            self.video_widget.show()
            self.video_player.play()
            #just restart..
        elif (ext in ['.png']): #screenshot image..
            self.video_overlay.setPixmap(QPixmap(fname).scaled(self.video_overlay.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.video_overlay.show()
            #search for existing video cache entry for this file and update timestamp
            found = False
            result = next((item for item in self.video_cache if item["**"] == fname), None)
            if result:
                result['('] = time.time() #update timestamp']
                self.video_cache.remove(result) #remove old entry
                self.video_cache.insert(0, result) #insert at front of list
            else:
                self.video_cache.insert(0, {'_': 'png', '**': fname, '(': time.time(), ')': None, '..': 0})
        else:
            self.video_player.setMedia(QMediaContent(QUrl.fromLocalFile(fname)))
            self.video_widget.show()
            self.video_player.play()
            self.currentvideo = fname
            result = next((item for item in self.video_cache if item["**"] == fname), None)
            if result:
                result['('] = time.time() #update timestamp']
                self.video_cache.remove(result) #remove old entry
                self.video_cache.insert(0, result) #insert at front of list
                self.video_player.setPosition(result['..']) #resume from last position
            else:
                self.video_cache.insert(0, {'_': 'mpg', '**': fname, '(': time.time(), ')': None, '..': 0})
    
    def pause_video(self, hideme = True):
        """Pause the video playback."""
        logger.info('Pausing video')
        self.highlighton = False #turn off highlight when pausing video, can adjust as needed.
        #update video cache
        if (len(self.video_cache) > 0):
            if (self.video_cache[0]['_'] == 'png'):
                self.video_cache[0]['..'] = time.time() - self.video_cache[0]['('] #update duration played
            else:
                self.video_cache[0]['..'] = self.video_player.position()
            self.video_cache[0][')'] = time.time()
            
        self.video_player.pause()
        self.video_widget.hide()
#        self.video_player.setMedia(QMediaContent()) #clear media to stop playback and release resources.
        self.video_overlay.hide()

        for i in range(3):
            self.label_main[i].show() #show main labels when pausing video, can adjust as needed.
        self.label_qr.show()
        for l in self.label_ps:
            l.show()
        for l in self.label_filter_info:
            l.show()
        self.label_info.show()
        self.label_topic_info[0].show()
        self.label_topic_info[1].show()
        self.label_p.show()

    def draw_screen_box(self, bbox=""):
        """Draws a box around the screen."""
        if (self.highlighton):
            logger.info('Highlight already on, skipping draw_screen_box')
        else:
            ocrtext, fname = self.save_screenshot('hotkeys', 'screenshot.png')
            self.play_video(fname)
            self.highlighton = True

        #get geometry of the highlight rectangle.  
        if (bbox !=""): #xxyy
            bbox = bbox.split(',')
            bbox = [int(b) for b in bbox]
            bbox = self.format_bbox(bbox)
            self.highlightrect = {'x': bbox[0], 'y': bbox[2], 'width': bbox[1]-bbox[0], 'height': bbox[3]-bbox[2]}
            self.video_overlay.set_overlay_bbox(self.highlightrect)
#            self.video_widget.update()
            logger.info(f'Screen box drawn: {self.highlightrect}')
        else:
            geometry = self.geometry()
            self.highlightrect = {'x': geometry.x()+100, 'y': geometry.y()+100, 'width': geometry.width()-100, 'height': geometry.height()-100}

        
        self.update()  # Trigger a repaint to show the box
        
    def hideme(self):
        """Method to close the window."""
        self.hide()

        logger.info('Window hidden')
        logger.info(f'!!STARTUP LAG: {time.time() - self.startup_lag} seconds')


    def play(self, fname):
        """Play a media file."""
        logger.info(f'Playing file: {fname}')
        #add actual playback logic here, e.g. open file with default app, or send command to other app, etc.
        #for now just log it.
        #get file type from extension
        ext = os.path.splitext(fname)[1].lower()
        if (ext in ['.mp4', '.avi', '.mkv']):
            logger.info(f'Playing video file: {fname}')
            #play on Qt video widget..
            self.play_video(fname)



        elif (ext in ['.mp3', '.wav', '.ogg']):
            logger.info(f'Playing audio file: {fname}')
            absolute_path = os.path.abspath(fname)
            self.currentsound = playsound(absolute_path, block=False) #non-blocking play, may need to adjust for different file types and playback needs.
        else:
            logger.info(f'Unknown file type for playback: {fname}')
        

    def pause_tmap(self, hideme=True):
        logger.info('Pausing playback')
        #add actual pause logic here, e.g. pause video widget, or send command to other app, etc.
        self.pause_video(hideme=hideme)

        if (self.currentsound is not None and self.currentsound.is_alive()):
            self.currentsound.stop() #stop current sound, may need to adjust for different playback needs.

    def play_tmap(self, no=0):
        logger.info(f'Playing next item in time map: {self.tmapindex} + {no}')
        #find next item in tmap based on current time, and play it.  
        #for now just log it, can add actual playback logic later.
        if (len(self.tmap) == 0):
            logger.info('Time map is empty, nothing to play.')
            return
        else:
            if (self.tmapindex + no >= len(self.tmap)):
                #time jump..?
                #just play indicator?  
                self.tmapindex = len(self.tmap) - 1
            elif (self.tmapindex + no < 0):
                #time jump back..?
                #just play indicator?  
                self.tmapindex = 0
            else:
                self.tmapindex += no

            t = self.tmap[self.tmapindex]
            print(t)
            if (t.get('timestamp', None) is not None):
                timestamp = t["timestamp"]
                logger.info(f'Playing item with timestamp: {timestamp} {self.tmapindex}')
                self.set_time(timestamp) #jump to time of item, can adjust as needed.
                self.show_tmap(timestamp) #update time map display to show current item, can adjust as needed.
            try:
                if (t["vars"].get('fname', None) is not None):
                    logger.info(f'Playing file: {t["vars"]["fname"]}')
                    #add actual playback logic here, e.g. open file with default app, or send command to other app, etc.
                    #assume video..
                    self.play(t["vars"]["fname"]) #non-blocking play, may need to adjust for different file types and playback needs.
                elif (t["vars"].get('FILE', None) is not None):
                    logger.info(f'Playing file: {t["vars"]["FILE"]}')
                    #add actual playback logic here, e.g. open file with default app, or send command to other app, etc.
                    #for now assume audio..
                    self.play(t["vars"]["FILE"]) #non-blocking play, may need to adjust for different file types and playback needs.
                elif (t['type'] == '> ' and t['cmd'] == 'Add Bookmark'):
                    #read in this and start playwrighty 
                    self.inqueue.put('<<hotkeys>>\n' + '\n'.join(t['lines']))
                else:
                    if (t['type'] == "**"):
                        if (t['topic'] != self.reading_topic):
                            self.reading_topic = t['topic']
                            logger.info(f"Topic changed to {t['topic']}")
                            text = t['topic']
                            import extensions.trey.trey as trey

                            trey.speak('**' + text)
                        #if we have further commands, continue..
                    
                    logger.warning(f"Unknown command in time map item, no file to play. \nData: {t}")
                    if (self.tmapindex != 0 and self.tmapindex != len(self.tmap)-1):
                        #get word from dictionary.  
                        if (no > 0):
                            speech.play_synth([48,53], 12, 0.05) #tick
                        else:
                            speech.play_synth([48,54], 12, 0.05) #tock
                        self.play_tmap(no) #play next item to get to useful command..                            
#                    text = self.transcriber.write(t['lang'], t['cmd'], t['vars'], t['topic'], False)

            except Exception as e:
                logger.error(f'Error playing file from time map: {e}\nData: {t}')

#            self.tmapindex += 1 #move to next item for next play command, can adjust as needed.
            #time jump to next entry?
#               next_time = self.tmap[self.tmapindex]['timestamp']
#               self.set_time(next_time) #jump to time of next item, can adjust as needed.
                #this will reread if necessary..



    def show_tmap(self, current_time, secs=0):
        logger.info('Updating time map display')
        if (secs == 0):
            secs = self.e - self.s #use full time range if secs not specified, can adjust as needed.
        startchar = chr(0x30A1)
        cnttext = ""
        typecnttext = ""
        sumval = 0
        selected = []
        maintimes = []
        maintext = []

        for i in range(60):
            val = self.aggmap[i]['cnt']
            sumval += val
            cnttext += f'{chr(ord(startchar)+val)}'
            val2 = len(self.aggmap[i]['cnts'])

            typecnttext += f'{chr(ord(startchar)+val2)}'
            if (i%20 == 0):
                cnttext += ' ' #add space every 20 chars for readability, can adjust as needed.
                typecnttext += ' '
                maintimes.append(current_time - secs/2 + (i/60)*secs) #calculate time for each bucket, can adjust as needed.
                maintext.append({'&&': '&&', '..': maintimes[-1], '**': '**'}) #placeholder for main text display, can adjust as needed.

        maintimes.reverse() #reverse to have most recent time on right, can adjust as needed.
        print(f"Current time: {current_time}, Time window seconds: {secs}")
        sorted_tmap = sorted(self.tmap, key=lambda x: current_time - x['..'])
#        print(f"Sorted tmap: {sorted_tmap}")
        sorted_indices = sorted(range(len(self.tmap)), key=lambda i: abs(current_time - self.tmap[i]['..']))
        print(f"Sorted indices: {sorted_indices}")
        ctxtdic = {}
        if (len(sorted_indices) > 0):
            self.tmapindex = sorted_indices[0] #index of closest item in tmap to current time, can use this to select items to display or play etc.
#            print(sorted_tmap[-10:]) #get last 10 items in sorted tmap for debugging, can adjust as needed.
            print(sorted_tmap[:10]) #get first 10 items in sorted tmap for debugging, can adjust as needed.
            skipped = 0
            for i in range(len(sorted_tmap)): #check closest 10 items in tmap, can adjust as needed.
                #compare to current time, and select if within current time window.  
                #show one from each time window..
                if (sorted_tmap[i]['..'] <= current_time - secs/2 or sorted_tmap[i]['..'] >= current_time + secs/2):
                    skipped += 1
                    if (skipped > 10):
                        break #stop checking after skipping 10 items outside of time window, can adjust as needed.
                    continue #skip items outside of time window, can adjust as needed.

                for j in reversed(range(3)): #check most recent 3 time buckets, can adjust as needed.
#                    if (maintext[j]['**'] == '**'):
                        if (maintimes[j] <= sorted_tmap[i]['..'] < maintimes[j] + secs/3): #if item is within time bucket, can adjust bucket size as needed.
    #                    if (sorted_tmap[i]['timestamp'] >= maintimes[j] and sorted_tmap[i]['timestamp'] < maintimes[j] + secs/20): #if item is within time bucket, can adjust bucket size as needed.
                            if (sorted_tmap[i]['type'] == '> '): #only show commands for now.. no topic selection
                                maintext[j]['**'] = sorted_tmap[i]['**']
                                maintext[j]['..'] = sorted_tmap[i]['..']

                                #really want a specific key here..
                                mytime = sorted_tmap[i]['$$'].get('TIME', "_")
                                ctxtkey = sorted_tmap[i]['$$']['URL'] if (sorted_tmap[i]['$$'].get('URL', None) is not None) else "_"
                                if (ctxtkey == "_"):
                                    ctxtkey = mytime #use text as fallback if no URL, can adjust as needed.

                                if (mytime == self.tmap[self.tmapindex]['$$'].get('TIME', None)):
                                    print(f'Currently playing item: {sorted_tmap[i]} from {mytime}')
                                    maintext[j]['&&'] = maintext[j]['&&'] + '\n>>>>\n' #indicator for currently playing item, can adjust as needed.

                                if (ctxtdic.get(sorted_tmap[i]['&&'] + '_' + ctxtkey, None) is None):
                                    newentry = self.transcriber.write(sorted_tmap[i]['<<'], sorted_tmap[i]['&&'], sorted_tmap[i]['$$'], sorted_tmap[i]['**'], False, shortform=True)
                                    maintext[j]['&&'] = maintext[j]['&&'] + newentry
                                    ctxtdic[sorted_tmap[i]['&&'] + '_' + ctxtkey] = newentry
                                else:
                                    if (sorted_tmap[i]['$$'].get('TEXT', None) is not None):
                                        #display shortened context key
                                        shortkey = ctxtkey[:20]
                                        if (len(ctxtkey) > 20):
                                            shortkey += '...'
                                            shortkey += ctxtkey[-20:] #last 20 chars
                                        shorttext = sorted_tmap[i]['$$']['TEXT'][:100] #shorten text for display, can adjust as needed.
                                        maintext[j]['&&'] = maintext[j]['&&'] + '#' + shortkey + '\n' + shorttext + '\n'
#                                maintext[j] = {'**': sorted_tmap[i]['**'], '..': sorted_tmap[i]['..'], '&&': self.transcriber.write(sorted_tmap[i]['<<'], sorted_tmap[i]['&&'], sorted_tmap[i]['$$'], sorted_tmap[i]['**'], False)}

#                if (len(maintext) < 3 and sorted_tmap[i]['type'] == '> ' and sorted_tmap[i]['timestamp'] >= maintimes[len(maintimes)-1]): #only show commands for now.. no topic selection
#                    self.transcriber.current_topic = sorted_tmap[i]['cmd'] #dont need topic to be updated..
#                    maintext.append({'topic': sorted_tmap[i]['topic'], 'timestamp': sorted_tmap[i]['timestamp'], 'text': self.transcriber.write(sorted_tmap[i]['lang'], sorted_tmap[i]['cmd'], sorted_tmap[i]['vars'], sorted_tmap[i]['topic'], False)})

            maintext = sorted(maintext, key=lambda x: x['..'])            
            print(maintext)
            for i in range(len(maintext)):
#                if (temptext[0:2] != '**'):

                temptext = f'{maintext[i]["&&"]}' #add topic as header if not already included, can adjust formatting as needed.
                currentpos = temptext.find('\n>>>>')
                if (currentpos != -1):

                    temptext = '<b>>>>></b>' + temptext[currentpos:]

                self.label_main[i].setText(temptext.replace('\n', '<br>'))
                self.label_main[i].update()



        if sumval > 0:            
            logger.info(f"Data found {sumval} total commands in current time window.")

        typecnttext = typecnttext.replace(startchar, '_')
        cnttext = cnttext.replace(startchar, '_')

        st = datetime.fromtimestamp(self.s).strftime('%Y%m%d %H%M%S')
        et = datetime.fromtimestamp(self.e).strftime('%Y%m%d %H%M%S')

        self.label_times[0].setText(f'<pre>{typecnttext}   {st}</pre>')
        self.label_times[0].update()
        self.label_times[1].setText(f'<pre>{cnttext}   {et}</pre>')
        self.label_times[1].update()

    def set_tmap(self, tmap = [], current_time=None):
        logger.info(f'Updating time map display {len(tmap)}')
        #allcommands..
        self.tmap = tmap
        startchar = chr(0x30A1)
        startchar = chr(0x0041) #start with A for testing, can use other unicode chars as needed.
        #need better than this, but..
        self.aggmap = [{'cnt': 0, 'cnts': {} } for i in range(60)] #reset aggmap
        max = 0
        start_time = datetime.fromtimestamp(self.s)
        end_time = datetime.fromtimestamp(self.e)            
        secs = (self.e - self.s)
        if (len(tmap) > 0):
            if (current_time is None):
                #mid of start/end                
                current_time = start_time + timedelta(seconds=int(secs/2))
                current_time = current_time.timestamp()

            start_time = start_time.timestamp()
            end_time = end_time.timestamp()
            total_seconds = end_time - start_time
            quantize_seconds = total_seconds / 60 #quantize into 60 time points for display
            for i,cmd in enumerate(tmap):
                t = cmd['timestamp']
                if (t < start_time or t > end_time):
                    continue #skip out of range
                pos = int((t - start_time) / quantize_seconds)
                self.aggmap[pos]['cnt'] += 1 #for now just count number of commands in each time bucket, can add more info later about types of commands etc.
                self.aggmap[pos]['cnts'][cmd['type']] = self.aggmap[pos]['cnts'].get(cmd['type'], 0) + 1 #count by type as well.
                if (self.aggmap[pos]['cnt'] > max):
                    max = self.aggmap[pos]['cnt']
            
            if (max > 24):
                for i in range(60):
                    if (self.aggmap[i]['cnt'] > 0):
                        self.aggmap[i]['cnt'] = math.ceil(self.aggmap[i]['cnt'] / max * 24) #scale to 24 for display purposes, can adjust as needed.

            

        self.show_tmap(current_time, secs)





    def read(self, langs=None, start_time=None, end_time=None):
        if (langs is None):
            langs = self.langs
        combined = []

        for lang in langs:
            data = self.transcriber.read(lang, start_time, end_time)
            logger.info(f'Reading data for {lang} from {start_time} to {end_time}: {len(data)} entries')
            #combine all data into single array sorted by timestamp
            combined.extend(data)
        combined.sort(key=lambda x: x['timestamp'])
        return combined
    
            
    

    def set_time(self, t, s=0, e=0, w=0, langs=None):
        if (langs is None):
            langs = self.langs

        localt = datetime.fromtimestamp(t)
        formattedt = localt.strftime('%Y%m%d %H%M%S')
        print(f"Setting time to {formattedt} with start {s}, end {e}, window {w}")
        if (s == 0):
            s = self.s
        if (e == 0):
            e = self.e
        if (w == 0):
            w = e - s

        st = datetime.fromtimestamp(s).strftime('%Y%m%d %H%M%S')
        et = datetime.fromtimestamp(e).strftime('%Y%m%d %H%M%S')
        self.s = s
        self.e = e

        #do we need to reread
        self.label_timeinfo[0].setText(f'$${formattedt}')
        self.label_timeinfo[1].setText(f'$$ST={st}')
        self.label_timeinfo[2].setText(f'$$ET={et}')
        for i in range(3):
            self.label_timeinfo[i].update()

        #only read if start/end change..
        if (datetime.fromtimestamp(s) < self.transcriber.allcmds[langs[0]]['start_time'] or datetime.fromtimestamp(e) > self.transcriber.allcmds[langs[0]]['end_time']):
            logger.info(f'Time range {datetime.fromtimestamp(s)} to {datetime.fromtimestamp(e)} is out of bounds for available data.')
            b = self.read(langs, datetime.fromtimestamp(s), datetime.fromtimestamp(e))
            self.set_tmap(b, t)
            logger.info(b)
            self.transcriber.read_midi(datetime.fromtimestamp(s), datetime.fromtimestamp(e)) #only when starttime or endtime is out of bounds, otherwise we are just filtering existing data in memory, so no need to reread midi data.

        elif (datetime.fromtimestamp(s) > self.transcriber.allcmds[langs[0]]['start_time'] or datetime.fromtimestamp(e) < self.transcriber.allcmds[langs[0]]['end_time']):
            logger.info(f'Time range {datetime.fromtimestamp(s)} to {datetime.fromtimestamp(e)} is within bounds for available data.')
            #just filter by updated start/end
            b = self.read(langs, datetime.fromtimestamp(s), datetime.fromtimestamp(e))

            self.set_tmap(b, t)
        else:
            logger.info(f'Time range {datetime.fromtimestamp(s)} to {datetime.fromtimestamp(e)} is the same as available data, no need to reread.')
            #just update display with existing data in memory
            self.show_tmap(t, e-s)

        

    def set_speed(self, speed, adjust=1.0, lang='_meta', spoken_lang=""):
        #pass none to load default..
        if speed is None:
            speed = self.get_setting('SPEED', 1.0, lang)
        if (lang == '_meta'):
            self.speed = speed
            self.label_timeinfo[3].setText(f'$$S={speed}')
            return speed
        elif (lang == 'video'):
            self.playback_speed *= adjust
            self.video_player.setPlaybackRate(self.playback_speed)
            self.label_timeinfo[3].setText(f'$$VS={self.playback_speed}')
            self.label_timeinfo[3].update()
            return self.playback_speed
        elif (lang =='_lang'):
            speech.SPEED *= adjust
            return speech.SPEED
        elif (lang == 'hotkeys'):
            i = 0
            speed = config.cfg['trey']['player']['speed']['default']
            if (spoken_lang):
                if (spoken_lang not in config.cfg['trey']['player']['speed']):
                    config.cfg['trey']['player']['speed'][spoken_lang] = speed
                config.cfg['trey']['player']['speed'][spoken_lang] *= adjust
                speed = config.cfg['trey']['player']['speed'][spoken_lang]
            else:
                speed *= adjust
                config.cfg['trey']['player']['speed']['default'] = round(speed, 1)
            self.label_timeinfo[3].setText(f'$$AS={speed}')
            self.label_timeinfo[3].update()

            #adjust reader speed..



    def update_topic_history(self):
        #update topic history with current topic from transcriber, and show in filter info area.  
        self.show_filter_info()

    def remove_filler(self, text):
        text = text.replace('http://', '#')
        text = text.replace('https://', 's#')
        text = text.replace('www.', '')
        return text
    
    def short_display(self, text, maxlen=28):
        if (len(text) > maxlen):
            text = self.remove_filler(text)
            return text[0:int(maxlen/2)] + ".." + text[-int(maxlen/2):]
        else:
            return text
        
    def show_filter_info(self):
        idx = 0
        for k, v in self.filters.items():
            self.label_filter_info[idx].setText(f'$${k}={v}')
            self.label_filter_info[idx].update()
            idx += 1    
        if (idx < len(self.label_filter_info)):
            self.label_filter_info[idx].setText(f'$$') #clear next line for new filter info
            self.label_filter_info[idx].update()
            idx += 1
        for i in range(idx, len(self.label_filter_info)):
             t = self.short_display(self.topichistory[i-idx]['topic']) if i-idx < len(self.topichistory) else ""
             self.label_filter_info[i].setText(f'{i-idx}=**{t}') #clear remaining filter info
             self.label_filter_info[i].update()



    def show_p(self, struct=[]):
      """Method to show a QR code."""
      #{'type': type, 'lang': lang, 'cmd': currentcmd, 'vars': vars, 'timestamp': time.time()}
      varsperline = 2
      fulltext = ""
      nextline = ""
      cnt = 0

      wbarray = [0,1,0,1,0,0,1,0,1,0,1,0] #for now fixed from C
      
      
      #clear for now..

      for i, l in enumerate(struct):
        type = l['type']
        if (type == '> '):
          if (l['cmd'] == 'Click Link_' or l['cmd'] == 'Select Book_' or l['cmd'] == 'Select Topic_' 
              or l['cmd'] == 'Select Tab_' or l['cmd'] == 'Time Zoom_' or l['cmd'] == 'Read Link_' 
              or l['cmd'] == 'Select Window_' or l['cmd'] == 'ask_' or l['cmd'] == 'Define_'):
            for i2, l2 in enumerate(self.label_ps):
                self.label_ps[i2].setText("")            
            cnt = 0       
            for k, v in l['vars'].items():
#                if (wbarray[i%len(wbarray)] == 0):
#                    fulltext += "\t"
#                else:
#                    fulltext += "\t\t\t"
                #find number in key
                n = k

                if (n.isdigit()):
#                    for j in range(int(n)%12):
#                        fulltext += " "
                    color = self.getColorFromSequence(int(n))
                    self.label_ps[int(n)%len(self.label_ps)].setText(self.short_display(f'{n}={v}'))

                else:
                    fulltext += self.short_display(f" {n} = {v}")
                    fulltext += "\n"

                cnt += 1
            context = l['vars'].get('context', None)
            if (context is not None):
                fulltext += f"\n{context}\n"
          elif (l['cmd'] == 'ask'):
            if 'ANSWER' in l['vars']:
                
                fulltext += f"\nAnswer: {self.format_ptext(l['vars']['ANSWER'])}\n"
                answertext =f'@@{l["vars"]["QUERY"]}\n<br>==\n<br>{l["vars"]["ANSWER"].replace("\n", "\n<br>")}\n\n$$\n'
                lines = answertext.splitlines()
                div = [0,20,40,60]
                textlen = 0
                #better calculation needed here..
                j = 0
                for i in range(0, len(lines), 1):
                    textlen += len(lines[i])
                    if (textlen > 1600): #~ 80*40 - white space..
                        j+=1
                        div[j] = i
                        textlen = 0

                for i in range(0, len(div)-1, 1):
                    answertext = ''.join(lines[div[i]:div[i+1]]) + "\n...\n$$\n"
                    mktxt = markdown.markdown(answertext) #convert to HTML
                    self.label_main[i].setText(mktxt)

            for i2, l2 in enumerate(self.label_ps):
                self.label_ps[i2].setText("")            
            cnt = 0

        elif (type == '~~'):
            test = ''

      if (fulltext != ""):
        self.label_p.setText(fulltext.replace('\n', '<br>'))
        self.label_p.adjustSize()
        self.label_p.update()
        logger.info(f'$$PTEXT={fulltext}')
        


    def format_ptext(self, fulltext):
        #find places for CR.  
        import textwrap        
        wrapped = textwrap.fill(fulltext, width=60)
        return wrapped
    
    def is_complete_cmd(self, struct):
      for i, l in enumerate(struct):
        type = l['type']
        if (type == '> ' and l['cmd'][-1] != '_'):
          return True
      return False
    
    def update_info(self, data):
        data = data.replace('\t', '<br>') #sometimes just have data in var entries..
        data = data.replace('\n', '<br>')
        self.label_info.setText(data)
        self.label_info.adjustSize()
        self.label_info.update()

    def showQR(self, data, struct=[]):
        """Method to show a QR code."""
#        logger.info('Showing QR code')
        #adjust readable text first..
        #check for last last command is it list_bookmarks.  
        self.qr_cache.insert(0, {'data': data, 'struct': struct})
        if (self.qr_cache_index != 0):
            self.qr_cache_index +=1

        self.show_p(struct)
        self.update_info(data)

        qrdata = data
        #if we need to truncate
        print(f'QR data length: {len(qrdata)}')
        print(qrdata[0:100] + "...\n")


        
        if (self.is_complete_cmd(struct)): #only display if completion
            #truncate this command to show everything but suggestions.  
            lines = data.split('\n')
            for (i, l) in enumerate(lines):
                if (l.startswith('<<meta>>')):
                    qrdata = '\n'.join(lines[0:i]) #only show lines before suggestions, can adjust as needed.
                    break
            if (len(qrdata) > 600):
                qrdata = qrdata[0:600] #truncate to 1000 bytes max for QR code.
                qrdata += "\n...\n$$\n"
            import extensions.trey.trey as trey

            qr_image = trey.create_qr_code(qrdata)
    #        qr_image = Image.open("qrcode.png")
    #        qr_image.show()
            pixmap = QPixmap('qrcode.png')
            self.label_qr.setPixmap(pixmap)
            self.label_qr.adjustSize()

        logger.info('QR code displayed')

    def findLabel(self, hwnd):
        if (hwnd in self.windowlabels):
            return self.windowlabels[hwnd]
        elif (self.windowcounter < 100):
            label = self.windowlabels[str(self.windowcounter)]
            self.windowlabels[hwnd] = label
            self.windowcounter += 1
            return label
        else:
            return None
        
    def updateWords(self, pwords):
        y = 100
        for idx, pw in enumerate(pwords):
            word = pw['word']
            keys = pw['keys']
            label = self.findLabel(f'word{idx}')
            if (label is not None):
                label.setText(f'Word: {word}\nKeys: {",".join(keys)}\n')
                label.setStyleSheet("background-color: rgba(255, 255, 255, 1);color: black;")
                label.move(self.geo.width() - 500, y)
                label.adjustSize()
                label.update()
                y += label.height() + 10

    def get_text_color(self, rect, screenshot):
        """Get the color of the text at the given coordinates."""
        total_luminance = 0
        pixel_count = 1    
        img = screenshot.toImage()
        for x in range(rect[0], rect[2]):
            for y in range(rect[1], rect[3]):
                color = img.pixelColor(x, y)
                r, g, b, _ = color.getRgb()
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                total_luminance += luminance
                pixel_count += 1  

        average_luminance = total_luminance / pixel_count

        # Choose text color based on average luminance
        if average_luminance < 0.5:  # Threshold can be adjusted
            return "white"
        else:
            return "black"

    def updateLabels(self, allwindows):
        print(f"Updating labels for windows: {len(allwindows)}")
        for hwnd, w in allwindows.items():
            label = self.findLabel(hwnd)
            #title, rect, other
            if (label is not None):
                label.setText(f'HWND: {hwnd}\nTitle: {w["title"]}\nRect: {w["rect"]}\n')
                textcolor = "black"
                if (len(self.screenshots) > 0):
                    #get average color of window area
                    textcolor = self.get_text_color(w['rect'], self.screenshots[-1])
                    if (textcolor == "white"):
                        label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);color: white;")
                    else:
                        label.setStyleSheet("background-color: rgba(255, 255, 255, 1);color: black;")
                #label.setWordWrap(True)
                #Need an overlay window on top of our overlay.. otherwise can only display in certain locations..
                #not sure this is actually needed..
                label.move(w['rect'][0]-self.startx, w['rect'][1])
                #label.resize(w['rect'][2]-w['rect'][0], w['rect'][3]-w['rect'][1])
                label.adjustSize()
                label.update()


    def paintEvent(self, event):
        super().paintEvent(event)
        if (self.highlighton):
            self.video_overlay.update() #update the video overlay to draw the highlight box on top of the video widget.
#            self.video_widget.paintEvent(event) #call paint event of video widget to draw video frame first, then we will draw highlight box on top.
            """
            painter = QPainter(self) # Create a QPainter instance, passing 'self' (the widget) as the paint device.
            pen = QPen(Qt.red, 5, Qt.SolidLine)
            painter.setPen(pen)
            rect = self.highlightrect
#            painter.drawRect(rect['x']-self.geo.x(), rect['y']-self.geo.y(), rect['width'], rect['height'])
#            painter.drawRect(rect['x'], rect['y'], rect['width'], rect['height'])
            painter.drawRect(50, 150, 100, 100)
#            painter.drawRect(self.geo.x()+100, self.geo.y()+100, self.geo.width()-100, self.geo.height()-100)
            painter.setFont(painter.font()) # Use default font or set a custom one
            painter.drawText(50, 200, "Hello QPainter!")
            painter.end()
            """        
        # You can also draw text, ellipses, images, etc.
