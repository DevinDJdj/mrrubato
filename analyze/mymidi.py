from torch import nn, optim
import torch.nn.functional as F

MAXNGRAM = 15

class MyTrack:
  def __init__(self, trk, length, maxtime):
    self.notes = []
    self.length = length
    self.track = trk
    self.maxtime = maxtime

class MyMsg:
  def __init__(self, msg, prev, pedal):
    self.msg = msg
    self.note = msg.note
    self.currentTime = 0
    self.startmsg = None
    self.prevmsg = prev
    self.pedal = pedal
    self.ngrams = [0]*MAXNGRAM #keep this integer so I can use standard ML functions, but not great right now.  
    self.ngramstensor = None #ngrams pytorch
    self.ngramsp = None #P*P methodology
    self.nextmsg = None
    
  def print(self, iteration, song, group, videoid, midilink):
    i = 0
    tempmsg = self.msg
    ng = ''
    while (i < MAXNGRAM):
      ng = ng + str(self.ngrams[i]) + ' '
      i = i+1
    
    #NGRAM, 
    #use approximate calculated time here.  
    print('{0},{1},{2},{3},{4},{5},{6},{7}'.format(ng, str(iteration), song, group, videoid, str(self.startmsg.currentTime), str(self.currentTime), midilink))
    
class NgramModel(nn.Module):
    def __init__(self, vocb_size, context_size, n_dim):
        super(NgramModel, self).__init__()
        self.n_word = vocb_size
        self.embedding = nn.Embedding(self.n_word, n_dim)
        self.linear1 = nn.Linear(context_size * n_dim, 128)
        self.linear2 = nn.Linear(128, self.n_word)

    def forward(self, x):
        emb = self.embedding(x)
        emb = emb.view(1, -1)
        out = self.linear1(emb)
        out = F.relu(out)
        out = self.linear2(out)
        log_prob = F.log_softmax(out)
        return log_prob

    