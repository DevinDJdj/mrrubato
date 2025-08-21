#pip install pystray Pillow mss PyQt5
#pip install pynput
#pip install qrcode
#pip install mido python-rtmidi

#standard libraries
import logging
import os
import time
import sys
import threading

#Screen capture, QR code generation
import mss
import qrcode
from pynput import keyboard

#MIDI libraries
import mido


#UI components
import pystray
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt


#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
import config 
import mykeys


logger = logging.getLogger(__name__)
global window

global qapp
global midiout
global midiin

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

def get_screen():

    logger.info('Getting Screen')
    screen = qapp.primaryScreen()
    screens = qapp.screens()
    for i, s in enumerate(screens):
        logger.info(f'Screen {i}: {s.name()} - Size: {s.size()}')
        logger.info('Capturing Screen')

        screenshot = s.grabWindow( 0 ) # 0 is the main window, you can specify another window id if needed
        screenshot.save('shot' + str(i) + '.jpg', 'jpg')

def draw_overlay():

    #creating the main window
    logger.info('Opening main window')
    window.show()
    #add environment info needed.  
    window.showQR("https://missesroboto.com")

    draw_screen_box()

def draw_screen_box():
    """Draws a box around the screen."""
    geometry = window.geometry()
    #get geometry of the highlight rectangle.  
    window.highlighton = True
    #set details here.  
    window.highlightrect = {'x': geometry.x()+100, 'y': geometry.y()+100, 'width': geometry.width()-100, 'height': geometry.height()-100}
    window.update()  # Trigger a repaint to show the box
    logger.info('Screen box drawn')


def on_deactivate_overlay():
    """Function to be executed when the hotkey is pressed."""

    logger.info('Deactivating overlay')
    window.hideme()
    
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
    logger.info('Hiding window after delay')
    window.hideme()
    
class MyWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        self.highlightrect = {'x': 100, 'y': 100, 'width': 200, 'height': 200}
        self.highlighton = False

        # set the title
        self.setWindowTitle("Python")

        self.setWindowOpacity(0.5)
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

#        self.setGeometry(60, 60, 600, 400)

        # creating a label widget
        self.label_1 = QLabel("transparent ", self)
        # moving position
        self.label_1.move(100, 100)

        self.label_1.adjustSize()

        self.label_2 = QLabel(self)
        #move to bottom right corner
        self.label_2.setStyleSheet("background-color: rgba(255, 255, 255, 1);")
        self.label_2.move(self.width() - 400, self.height() - 300)

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

def stop_midi():
    midi_stop_event.set()  # Signal the MIDI thread to stop
    midi_thread.join()  # Wait for the MIDI thread to finish
#    time.sleep(10)  # Give some time for the thread to exit
    midiin.close()  # Close the MIDI input port
    midiout.close()  # Close the MIDI output port


def start_midi(midi_stop_event):
    global midiout, midiin
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
    mk = mykeys.MyKeys(config.cfg)
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
                    else:
                        print("Message does not have a note attribute")
        logger.info('Stopping MIDI thread')



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
window = MyWindow()

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



