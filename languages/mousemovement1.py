from pynput import *
import logging
import win32gui
import win32con


logger = logging.getLogger(__name__)


class mousemovement1:
  #define action for some sequences.  
  def __init__(self, config, qapp=None, startx=0):
    self.config = config
    self.qapp = qapp
    self.startx = startx
    self.geo = None

    self.name = "mousemovement1"
    self.maxseq = 10 #includes parameters
    self.mouse = mouse.Controller()
    self.callback = None

  def unload(self):
    #unload language specific data
    return 0

  def act(self, cmd, words=[], sequence=[]):
    """ACT based on command and sequence."""
    if (len(sequence) == 0 and "_" + cmd in self.funcdict):
      #run prefix command
      func = self.funcdict["_" + cmd]
      if hasattr(self, func):
        return getattr(self, func)(sequence)
      
    elif cmd in self.funcdict:
      func = self.funcdict[cmd]
      #all require keybot at end.

      #this function called every time a key is pressed.
      if hasattr(self, func + "_"):
        return getattr(self, func + "_")(sequence)
      
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
      print("No Data defined for " + self.__class__.__name__)  
    return 0
  
  def load_data(self):

    #load language specific data into the config.  
    default = {
      "2": {
        "Left Click": [59,58],
        "Right Click": [62,63],
        "Mouse Move X": [60,62],
        "Mouse Move Y": [60,61]
      }
    }
    if (self.name in self.config['languages']):
      logger.info(f'Merging existing {self.name} config')
      default.update(self.config['languages'][self.name])
    else:
      logger.info(f'No existing {self.name} config found, creating new one')

    self.config['languages'][self.name] = default

    self.funcdict = {
      "Left Click": "left_click",
      "Right Click": "right_click",
      "Mouse Move": "mouse_move",

    }
    self.config['languages'][self.name] = default
    return 0
  
  def left_click(self, sequence=[]):
    mymouse = self.mouse
    mymouse.press(mouse.Button.left)
    mymouse.release(mouse.Button.left)
    return 0
  
  def right_click(self, sequence=[]):
    mymouse = self.mouse
    mymouse.press(mouse.Button.right)
    mymouse.release(mouse.Button.right)
    return 0
  

  def mouse_move(self, sequence=[], absolute=False):
    mymouse = self.mouse
    #move right and down
    if (len(sequence) < 2):
      return 1 #need more data
    else:
      #get direction and amount from last 2 keys.
      move_x = sequence[-2]
      move_y = sequence[-1]
      if (absolute):
        mymouse.position = (move_x+self.startx, move_y)
      else:
        mymouse.move(move_x+self.startx, move_y)
      return 0


  def get_current_cursor_type(self):
      cursor_info = win32gui.GetCursorInfo()
      # cursor_info returns (flags, handle, (x, y))
      # The 'handle' is what we need to identify the cursor type
      cursor_handle = cursor_info[1]
      print(f'Startx: {self.startx}')
      print(f'Cursor info: {cursor_info}')

      # You can then compare this handle with known system cursor handles
      # For example:
      hand = win32gui.LoadCursor(0, win32con.IDC_HAND)
      arrow = win32gui.LoadCursor(0, win32con.IDC_ARROW)
      if cursor_handle == arrow:
          return win32con.IDC_ARROW
      elif cursor_handle == hand:
          return win32con.IDC_HAND
      # Add more comparisons for other cursor types as needed
      else:
          return -1