#pip install pystray Pillow mss PyQt5
#pip install pynput

#pip install qrcode
#pip install mido python-rtmidi
#pip install pywin32


#standard libraries
import logging
import os
import time
import sys
import threading
import psutil

from queue import Queue

#Screen capture, QR code generation
import mss
import qrcode
from pynput import keyboard, mouse


#MIDI libraries
import mido


#UI components
import pystray
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt
import win32gui
import win32process
import winsound

#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
import config 
import mykeys


#from kokoro import KPipeline
#from IPython.display import display, Audio
#import soundfile as sf
#import torch

#pip install playsound
from playsound3 import playsound
from pydub import AudioSegment
from pydub.playback import play

import simpleaudio as sa
import pygame
import edge_tts


logger = logging.getLogger(__name__)
global mywindow
global active_window
global qapp
global midiout
global midiin
global speech_pipe
audio_stop_events = []  # List to hold stop events for audio threads
audio_skip_events = []  # List to hold skip events for audio threads
audio_skip_queue = []
audio_location_queue = []

speech_pipe = None
active_window = None  # Global variable to store the active window handle

global windows
windows = {}

global trey_data
trey_data = {}

mouse_listener = None
global myactions
myactions = []  # Global list to store sequential actions

def on_click(x, y, button, pressed):

    if pressed:
        temp = win32gui.WindowFromPoint((x, y))
        if (in_trey((x,y))): #only capture second monitor clicks
            action = {'button': str(button), 'x': x, 'y': y, 'hwnd': temp, 'act': 'click'}
    #        action = f'Mouse clicked at ({x}, {y}) with {button}'
            update_actions(temp, action)

def stop_mouse_listener():
    """Stop the mouse listener."""
    global mouse_listener
    if mouse_listener is not None:
        mouse_listener.stop()
        mouse_listener = None
        logger.info('Mouse listener stopped')
    else:
        logger.info('Mouse listener was not running')

def start_mouse_listener():
    """Get mouse actions by listening to mouse clicks."""
    global mouse_listener
    if mouse_listener is not None:
        mouse_listener.stop()
    mouse_listener = mouse.Listener(on_click=on_click)
    if not mouse_listener.running:
        logger.info('Starting mouse listener')
        mouse_listener.start()

def update_actions(hwnd, action):
    global myactions
    global windows
    """Update the actions for the given window handle."""
    threadid, procid = win32process.GetWindowThreadProcessId(hwnd)
    action['threadid'] = threadid
    action['procid'] = procid
    if (procid in windows):
        if 'actions' not in windows[procid]:
            windows[procid]['actions'] = []
        windows[procid]['actions'].append(action)
        if (len(windows[procid]['actions']) > 100):
            logger.info('Removing oldest action from {procid} actions list')
            windows[procid]['actions'].pop(0)

    logger.info(f'{action}')
    myactions.append(action)  # Append to global actions list
    #remove if too many actions
    if len(myactions) > 100:
        logger.info('Removing oldest action from global actions list')
        myactions.pop(0)



def update_window_data(procid, title, rect, other=None):

    if (procid not in windows):
        windows[procid] = {}


    windows[procid]['title'] = title
    windows[procid]['rect'] = rect
    if (other is None):
        other = {}
    else:
        windows[procid]['other'] = other


def in_trey(rect):
    """Check if the rectangle is within the trey window."""
    if ('rect' in trey_data):
        trect = trey_data['rect']
        logger.debug(f"Checking if {rect} is in {trey_data['rect']}")
#        print(f"Checking if {rect} is in {trey_data['rect']}")
        if (len(rect) == 4 and len(trect) == 4):
            return (rect[0] >= trect[0] and rect[1] >= trect[1] and rect[2] <= trect[2] and rect[3] <= trect[3])
        elif (len(rect) == 2 and len(trect) == 4): #allow for point check
            return (rect[0] >= trect[0] and rect[1] >= trect[1] and rect[0] <= trect[2] and rect[1] <= trect[3])
    return False

def window_list_callback(hwnd, extra):

    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != "":
        # Get window title
        title = win32gui.GetWindowText(hwnd)
        # Get window position and size (left, top, right, bottom)
        rect = win32gui.GetWindowRect(hwnd)
        if (title.startswith("Trey - ")):
            #get the rect we need to be aware of.  
            #expand rect some windows have odd borders.  
            print(f"Found Trey window: {title} at {rect}")
            x, y, right, bottom = rect
            x -= 8  # Adjust for window borders
            y -= 8
            right += 8
            bottom += 8
            rect = (x, y, right, bottom)
            trey_data['rect'] = rect
            trey_data['hwnd'] = hwnd
            trey_data['title'] = title

        trect = (0,0,0,0)
        if ('rect' in trey_data):
            trect = trey_data['rect']
#            trect[0] += 50 #some margin for overlapping windows.  

        # Check if the window is fully within the trey window
        if (in_trey(rect)):
            threadid, procid = win32process.GetWindowThreadProcessId(hwnd)
            update_window_data(procid, title, rect, {'threadid': threadid, 'hwnd': hwnd})
            x, y, right, bottom = rect
            width = right - x
            height = bottom - y
            action = {'title': title, 'rect': rect, 'hwnd': hwnd, 'procid': procid, 'threadid': threadid, 'act': 'init'}
            update_actions(hwnd, action)

    return True # Continue enumeration    

def create_image(width, height, color1, color2):
    """Generates a simple image for the icon."""
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

def on_quit_action(icon, item):
    """Callback function for the 'Quit' menu item."""
    logger.info('Stopping icon')
    icon.stop()
    logger.info('Stopping MIDI thread')
    stop_midi()
    logger.info('Quitting application')
    qapp.quit()


def on_show_message(icon, item):
    """Callback function to display a notification."""
    icon.notify("Hello from pystray!", "Sample Notification")
    draw_overlay()

def on_get_screen(icon, item):
    """Callback function to capture the screen."""
    get_screen()


def play_in_background(text, links=[], stop_event=None, skip_event=None, q=None, q2=None):
    sound_file = "0.mp3"
    VOICE = "en-US-AriaNeural"
#    tts_file = "TTS.txt"
#    with open(tts_file, "w") as f:
#        f.write(text)
#    communicate = edge_tts.Communicate(text, VOICE)
#    communicate.save(sound_file)
#    os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{text}\" --rate=\"-10%\"")

    lines = text.split('\n')
    skip = 0

    total_read = 0
    link_loc = 0
    while (link_loc < len(links) and 'offset' in links[link_loc] and links[link_loc]['offset'] == -1):
        link_loc += 1
        #skip all links with no offset

    for idx, l in enumerate(lines):
        if (stop_event.is_set()):
            logger.info('Audio stop event set, stopping playback')
            print('Audio stop event set, stopping playback')
            break
        if (skip_event.is_set()):
            logger.info('Audio skip event set, skipping this line')
            print('Audio skip event set, skipping next several lines')
            lines_to_skip = q.get()
            skip += lines_to_skip    #skip next 3 lines
            skip_event.clear()

        if (skip > 0):
            skip -= 1
            total_read += len(l) + 1 #include newline
            continue

        print(f'Line: {l}')
        sound_file = f"./temp/{idx}.mp3"
        if (len(l) > 5):
            try:
    #            communicate = edge_tts.Communicate(text, VOICE)
    #            await communicate.save(sound_file)
                os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --text \"{l}\" --rate=\"-10%\"")
                playsound(sound_file, block=True) # Ensure this thread blocks for its sound
#                time.sleep(0.5) #short pause between lines
            except Exception as e:
                logger.error(f'Error in TTS playback: {e}')
                print(f'Error in TTS playback: {e}')
                continue

        total_read += len(l) + 1 #include newline
        for i in range(0, len(l)+1, 5): #check every 5 characters
            #not sure if we want to beep for skipped lines or not.  
            #maybe problematic.  
            if (link_loc < len(links) and 'offset' in links[link_loc] and links[link_loc]['offset'] != -1 and links[link_loc]['offset'] <= total_read):
                print(f'At link: {links[link_loc]}')
                winsound.Beep(1000, 100) #short beep to indicate link
                link_loc += 1
            
            time.sleep(0.4) #simulate reading time. 0.4 seconds per 5 characters estimate.  
            #shouldnt have to be too exact.  

        if (q2 is not None):
            q2.put(total_read)
#    os.system(f"edge-tts --voice \"{VOICE}\" --write-media \"{sound_file}\" --file \"{tts_file}\" --rate=\"-10%\"")
#    time.sleep(2) #wait for file to be written
#    seg = AudioSegment.from_mp3(sound_file)

    # Export as WAV
#    wav_file =  "1.wav" 
#    seg.export(wav_file, format="wav")

#    playsound(sound_file)
    sys.exit() # Exit the thread when done

#    pygame.mixer.init() 

    # Replace 'your_audio_file.wav' with the actual path to your audio file
#    sound = pygame.mixer.Sound(wav_file)
#    sound.play() 
#    pygame.mixer.music.load(sound_file)
#    pygame.mixer.music.play()


#    wave_obj = sa.WaveObject.from_wave_file(sound_file)
#    play_obj = wave_obj.play()
#    play_obj.wait_done()

#    playsound(sound_file, block=True) # Ensure this thread blocks for its sound
#    time.sleep(1) # Wait for a short duration
#    os.remove(sound_file) # Clean up the sound file
#    sys.exit() # Exit the thread when done

def speak(text, links = []):
    global audio_stop_events
    """Speak the given text using the speech pipeline."""
    print(f'Speaking: {text}')

    audio_stop_event = threading.Event()  # Event to signal stopping
    audio_stop_events.append(audio_stop_event)  # Store the event in the global list
    audio_skip_event = threading.Event()  # Event to signal skipping
    audio_skip_events.append(audio_skip_event)  # Store the event in the skip list as well
    q = Queue()
    audio_skip_queue.append(q)
    q2 = Queue()
    audio_location_queue.append(q2)
    print(audio_stop_events)
    audio_thread = threading.Thread(target=play_in_background, args=(f'{text}',links, audio_stop_event, audio_skip_event, q, q2))
    audio_thread.start()
    return q2, audio_stop_event #communicate how much we have read.  

"""
def speak(text):
    global speech_pipe
    print(f'Speaking: {text}')
    if (speech_pipe is not None):
        generator = speech_pipe(text, voice='af_heart')
        for i, (gs, ps, audio) in enumerate(generator):
            print(i, gs, ps)
#            display(Audio(data=audio, rate=24000, autoplay=i==0))
            with sf.SoundFile(f'{i}.wav', mode='w', samplerate=24000, channels=1, subtype='PCM_16') as f:
                f.write(audio)
                f.close()
                pass
#            sf.write(f'{i}.wav', audio, 24000)
#            song = AudioSegment.from_wav(f'{i}.wav')
#            play(song)

            thread1 = threading.Thread(target=play_in_background, args=(f'{i}.wav',))
            thread1.start()


    else:
        logger.error('Speech pipeline is not initialized.')

"""

def get_screen():


    logger.info('Getting Screen')
    text = '''
    [Kokoro](/kˈOkəɹO/) is an open-weight TTS model with 82 million parameters. Despite its lightweight architecture, it delivers comparable quality to larger models while being significantly faster and more cost-efficient. With Apache-licensed weights, [Kokoro](/kˈOkəɹO/) can be deployed anywhere from production environments to personal projects.
    '''
    text = "This is a test of text to speech using edge-tts on Windows."
    speak(text)

    screen = qapp.primaryScreen()
    screens = qapp.screens()
    for i, s in enumerate(screens):
        logger.info(f'Screen {i}: {s.name()} - Size: {s.size()}')
        logger.info('Capturing Screen')

        screenshot = s.grabWindow( 0 ) # 0 is the main window, you can specify another window id if needed
        screenshot.save('shot' + str(i) + '.jpg', 'jpg')

def get_screen_qrinfo():
    """Capture the screen and generate a QR code with the information."""
    # Generate a QR code with the screenshot information
    qr_image = create_qr_code("Screenshot captured: screenshot.png")
    qr_image.show()

def create_qr_text(text, hwnd):
    """Create a QR code with the given text."""
    threadid, procid = win32process.GetWindowThreadProcessId(hwnd)
    name = psutil.Process(procid).name()
    ret = ""
    if 'Path' in os.environ:
        ret += "$$Path=" + os.environ['Path'] + "\n"
    if 'HOME' in os.environ:
        ret += "$$HOME=" + os.environ['HOME'] + "\n"
    ret += "$$PID=" + str(procid) + "\n"
    ret += "$$ThreadID=" + str(threadid) + "\n"
    ret += "$$ProcessName=" + name + "\n"
    ret += text
    return ret

def draw_overlay():
    global active_window

    #creating the main window
    logger.info('Opening main window')
    mywindow.show()
    #add environment info needed.  
    logger.info('Getting Screen info')
    #need to initialize trey_data first.
    if ('rect' not in trey_data):
        win32gui.EnumWindows(window_list_callback, None)    

    win32gui.EnumWindows(window_list_callback, None)    


    temp = win32gui.GetForegroundWindow()
    rect = win32gui.GetWindowRect(temp)
    qrdata = ""
    if (in_trey(rect)):
        active_window = temp

    if (active_window is not None):
        title = win32gui.GetWindowText(active_window)
        logger.info(f'Active window: {title} at {rect}')
        logger.info('Showing QR code')
        qrdata = f'$$BBOX={rect}\n$$TITLE={title}'
        qrdata = create_qr_text(qrdata, active_window)
        mywindow.showQR(qrdata)

    mywindow.activateWindow() # Bring to front
    draw_screen_box()

    #hiding in 3 seconds
    logger.info('Hiding window after 3 seconds')
    t = threading.Timer(3, _hide, args=["Hello from Timer!"])
    t.start()  # Start the timer in a new thread

    start_mouse_listener()  # Start the mouse listener



def draw_screen_box():
    """Draws a box around the screen."""
    geometry = mywindow.geometry()
    #get geometry of the highlight rectangle.  
    mywindow.highlighton = True
    #set details here.  
    mywindow.highlightrect = {'x': geometry.x()+100, 'y': geometry.y()+100, 'width': geometry.width()-100, 'height': geometry.height()-100}
    mywindow.update()  # Trigger a repaint to show the box
    logger.info('Screen box drawn')


def on_deactivate_overlay():
    """Function to be executed when the hotkey is pressed."""

    logger.info('Deactivating overlay')
    mywindow.hideme()
    stop_mouse_listener()  # Stop the mouse listener
    
    print("Hotkey deactivated!")
    # Here you can implement logic to hide or deactivate the overlay
    logger.info('Hotkey deactivated!')

def on_activate_overlay():
    """Function to be executed when the hotkey is pressed."""
    print("Hotkey activated!")
    draw_overlay()
    logger.info('Hotkey activated!')

def setup_hotkey_listener():

    # Define the hotkey combination and the function to call
    # The format for hotkeys uses angle brackets for special keys (e.g., <ctrl>, <alt>)
    # and literal characters for regular keys.
    hotkeys = {
        '<ctrl>+<shift>+h': on_activate_overlay,
        '<ctrl>+<shift>+g': on_deactivate_overlay,
        # You can add more hotkeys here, e.g.:
        # '<shift>+a': another_function,
    }

    # Create a GlobalHotKeys listener
    listener = keyboard.GlobalHotKeys(hotkeys)

    # Start the listener in a non-blocking way
    listener.start()

    return listener



def create_qr_code(data):    
    """Generates a QR code from the given data.
    600 bytes of info max. 
     Dont need good error correction as we are just passing immediately to a QR code reader.
     """
    logger.info('Creating QR code')
    qr = qrcode.QRCode(
        version=15,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=2,
        border=10,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrcode.png")
    logger.info('QR code created and saved as qrcode.png')
    return img

def _hide(data):
    """Function to hide the window after a delay."""
#    global speech_pipe
#    logger.info('Initializing speech pipeline')
#    speech_pipe = KPipeline(lang_code='a')
    logger.info('Hiding mywindow after delay')
    mywindow.hideme()
    mk.set_startx(mywindow.startx)

    
class MyWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        self.highlightrect = {'x': 100, 'y': 100, 'width': 200, 'height': 200}
        self.highlighton = False
        self.startx = 0

        # set the title

        self.setWindowOpacity(0.4)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        screens = qapp.screens()
        logger.info('Listing available screens')
        primary_screen = qapp.primaryScreen()
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
                print(f'Setting window to second monitor at {geometry.x()},{geometry.y()} size {geometry.width()}x{geometry.height()}')
                self.setWindowTitle("Trey - " + s.name())

#        self.setGeometry(60, 60, 600, 400)

        # creating a label widget
        self.label_1 = QLabel("transparent ", self)
        # moving position
        self.label_1.move(100, 100)

        self.label_1.adjustSize()

        self.label_2 = QLabel(self)
        #move to bottom right corner
        self.label_2.setStyleSheet("background-color: rgba(255, 255, 255, 1);")
        #not sure best size.  
        self.label_2.move(self.width() - 500, self.height() - 400)

        # show all the widgets
        self.show()
        self.showQR("Starting Trey Overlay")
        #hide after a few seconds
        #workaround, something wrong with the PyQt if we hide this immediately
        t = threading.Timer(3, _hide, args=["Hello from Timer!"])
        t.start()  # Start the timer in a new thread
        logger.info('Window created')


    def hideme(self):
        """Method to close the window."""
        self.hide()
        logger.info('Window hidden')
    def showQR(self, data):
        """Method to show a QR code."""
        logger.info('Showing QR code')
        qr_image = create_qr_code(data)
#        qr_image = Image.open("qrcode.png")
#        qr_image.show()
        pixmap = QPixmap('qrcode.png')
        self.label_2.setPixmap(pixmap)
        self.label_2.adjustSize()
        logger.info('QR code displayed')

    def paintEvent(self, event):
        if (self.highlighton):
            painter = QPainter(self) # Create a QPainter instance, passing 'self' (the widget) as the paint device.
            pen = QPen(Qt.red, 5, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(100, 100, 200, 200)
        #    painter.drawRect(geometry.x()+100, geometry.y()+100, geometry.width()-100, geometry.height()-100)
    #        painter.setFont(painter.font()) # Use default font or set a custom one
    #        painter.drawText(50, 200, "Hello QPainter!")
            painter.end()
        
        # You can also draw text, ellipses, images, etc.

def stop_audio():
    #called from hotkeys to stop all audio threads.
    global audio_stop_events
    print('Stopping all audio threads')
    print(audio_stop_events)
    for audio_stop_event in audio_stop_events:
        print('Stopping audio thread')
        audio_stop_event.set()  # Signal the audio thread to stop

def skip_lines(n):
    #called from hotkeys to skip n lines of audio.
    global audio_skip_events
    print(f'Skipping {n*3} lines of audio')
    for i, audio_skip_event in enumerate(audio_skip_events):
        print('Skipping lines in audio thread')
        audio_skip_queue[i].put(n*3)
        audio_skip_event.set()

def page(n):
    #called from hotkeys to skip n lines of audio.
    #stop audio, or just page down, and start reading from there.  
    stop_audio()
    
    if (n > 0):
        print(f'Page Down {n}')
        i = 0
        for i in range(n):
            keyboard.Controller().press(keyboard.Key.page_down)
        
    else:
        print(f'Page Up {-n}')
        for i in range(-n):
            keyboard.Controller().press(keyboard.Key.page_up)



def stop_midi():
    midi_stop_event.set()  # Signal the MIDI thread to stop
    midi_thread.join()  # Wait for the MIDI thread to finish
#    time.sleep(10)  # Give some time for the thread to exit
    midiin.close()  # Close the MIDI input port
    midiout.close()  # Close the MIDI output port


def start_midi(midi_stop_event):
    global midiout, midiin
    global mk
    logger.info('Starting MIDI input/output')
    inputs = mido.get_input_names()
    print(mido.get_input_names())
    logger.info(f'Available MIDI inputs: {inputs}')
    outputs = mido.get_output_names()
    print(mido.get_output_names())
    logger.info(f'Available MIDI outputs: {outputs}')

    #Portable Grand-1 2
    #should really have some config selection here.  
    midiout = mido.open_output(outputs[1]) #open first output for now.  
    mk = mykeys.MyKeys(config.cfg, qapp, mywindow.startx)
    cont = keyboard.Controller()    
    midiin = mido.open_input(inputs[0]) #open first input for now.
    with midiin as inport:
        while (not midi_stop_event.is_set()):
            for msg in inport.iter_pending():
                if msg.type == 'note_on' or msg.type == 'note_off':
                    print(msg)
                    logger.info(f'Received MIDI message: {msg}')
                    if hasattr(msg, 'note'):
                        note = msg.note
                        if hasattr(msg, 'velocity'):
                            velocity = msg.velocity
                        else:
                            velocity = 0
                        #add key to sequence and check for any actions.  
                        a = mk.key(note, msg, callback=None)
                        if (a == -1):
                            #error or reset
                            winsound.Beep(2000, 500) # Beep at 2000 Hz for 500 ms
                    else:
                        print("Message does not have a note attribute")
        logger.info('Stopping MIDI thread')



def main():
    global qapp
    global mywindow
    global active_window
    global midi_thread
    global midiout, midiin
    global midi_stop_event
    global speech_pipe

    # Create an icon image
    icon_image = create_image(64, 64, 'blue', 'yellow')

    # Define the menu for the icon
    menu = (
        pystray.MenuItem('Capture Screen', on_get_screen),
        pystray.MenuItem('Show Message', on_show_message),
        pystray.MenuItem('Quit', on_quit_action)
    )

    # Create the pystray Icon instance
    icon = pystray.Icon(
        'my_trey_icon',  # Name of the icon
        icon=icon_image,  # The icon image
        title='Trey',  # Title displayed on hover
        menu=menu  # The menu associated with the icon
    )

    # Run the icon (this call is blocking)
    logging.basicConfig(filename='trey.log', 
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    logger.info('Started')
    logger.info('Setting up hotkey listener')
    hotkey_listener = setup_hotkey_listener()
    logger.info('Hotkey listener set up')

    logger.info('Creating Qapplication object')
    # Create the application object
    qapp = QApplication(sys.argv)
    logger.info('Creating application window')
    # Create the main application window
    mywindow = MyWindow()

    logger.info('Running icon')
    #icon.run()
    icon.run_detached()


    # Create a Thread object to listedn for MIDI messages
    # Create an event
    midi_stop_event = threading.Event()
    midi_thread = threading.Thread(target=start_midi, args=(midi_stop_event,))
    midi_thread.start()



    logger.info('Executing application')

    sys.exit(qapp.exec_())
    #hiding window as we only want it on hotkey
    #window.hide()





if __name__ == "__main__":
    main()
