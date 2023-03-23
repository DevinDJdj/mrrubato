MAXNGRAM = 15

class MyTrack:
  def __init__(self, trk, length):
    self.notes = []
    self.length = length
    self.track = trk

class MyMsg:
  def __init__(self, msg, prev, pedal):
    self.msg = msg
    self.note = msg.note
    self.prevmsg = prev
    self.pedal = pedal
    self.ngrams = [0]*MAXNGRAM
    self.ngramstensor = None #ngrams pytorch
    self.ngramsp = None #P*P methodology
    self.nextmsg = None