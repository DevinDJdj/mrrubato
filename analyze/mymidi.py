class MyTrack:
  def __init__(self, trk, length):
    self.notes = []
    self.length = length

class MyMsg:
  def __init__(self, msg, prev, pedal):
    self.note = msg.note
    self.prev = prev
    self.pedal = pedal