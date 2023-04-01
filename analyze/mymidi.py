from torch import nn, optim
import torch.nn.functional as F

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

    