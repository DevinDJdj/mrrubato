from torch import nn, optim
import torch.nn.functional as F
import numpy as np

MAXNGRAM = 10

def primes(n): # simple sieve of multiples 
  odds = range(3, n+1, 2)
  sieve = set(sum([list(range(q*q, n+1, q+q)) for q in odds], []))
  return [2] + [p for p in odds if p not in sieve]

def genmap(p):
  cnt = 0
  mymap = []
  for i in range(176):
    mymap.append(p[i])
  return mymap

primemap = genmap(primes(1070))

def getprime(n):
  return primemap[n]

  
    
  
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
    #this is previous ngram
    self.ngrams = [0]*MAXNGRAM #keep this integer so I can use standard ML functions, but not great right now.  
    self.fngrams = [0]*MAXNGRAM
    self.ngramstensor = None #ngrams pytorch
    self.ngramsp = None #P*P methodology
    self.nextmsg = None
    self.signs = 0
    
    
  def getSeqNGram(self, words):
    #get sequence ngram identifier
    #just order and then use order indexes.  
    #for now just use decimal and 10 ngrams to make it easier.  
    #0-9 10 digit number.  
    indexes = np.argsort(words)
    digits = 9
    ret = 0
    for i in indexes:
      ret += i*(10**digits)
      digits -= 1
#    print(words)
#    print(indexes)
    return ret

#thought of this twice, deserves a new name
  def getPGram(self, words):
#  def getNGram(self, words):
    #get relative ngram from all entries
    #primorial representing all of the 
    ret = 1
    for w in words:
      ret *= w
    return ret

  def getSigns(self, words):
    bits = 0
    for w in words:
      tmp = 0
      if w > 0:
        tmp = 1
      bits = bits << 1
      bits |= tmp
    return bits
    
  def getWords(self):
    i = 0
    words = []
    i = i+1
    while (i < MAXNGRAM):
      temp = self.ngrams[i] - self.ngrams[i-1]
      temp = abs(temp)
      #0, 1, -1, 2, -2, etc map.  
      #we need a negative property and positive property here.  
      #otherwise there are several possibilities.  
      #this reminds me of some nice mathematics like Bernouli
      #for now, lets just leave as is, we have one of 
      #several possibilties ngram
      #3, 1, 2, 4, -3, -1, 2, 4
      #4PICK2+4PICK4+4PICK0
      #ugh, defining this relationship why anyway.  
      #for now live with the multiple possibilities?  
      #we need this with all the signs.  
      #thats all.  
      if (self.ngrams[i] - self.ngrams[i-1] > 0):
        temp = temp * 2 - 1
      else:
        temp = -temp * 2
      
      p = getprime(temp)
      words.append(p)
      i = i+1
    return words
    
  def simpleprint(self):
    print('{0},{1},{2},{3}'.format(str(self.note), str(self.prevmsg), str(self.nextmsg), str(self.currentTime)))
    
    
  def print(self, iteration, song, group, videoid, midilink):
    shortenedmidilink = midilink.split('/')[-1]
    i = 0
    tempmsg = self.msg
    ng = ''
    startword = self.ngrams[0]
    prevword = startword
    words = []
    i = i+1
    totalmovement = 0
    abstotalmovement = 0
    while (i < MAXNGRAM):
      ng = ng + str(self.ngrams[i]) + ' '
      temp = self.ngrams[i] - self.ngrams[i-1]
      totalmovement += temp
      temp = abs(temp)
      abstotalmovement += temp
      #0, 1, -1, 2, -2, etc map.  
      if (self.ngrams[i] - self.ngrams[i-1] > 0):
        temp = temp * 2 - 1
      else:
        temp = -temp * 2
      p = getprime(temp)
      words.append(p)
#      words.append(temp)
      i = i+1
    
    #NGRAM, 
    #use approximate calculated time here.  
    print('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}'.format(str(self.startmsg.note), str(totalmovement), str(abstotalmovement), str(self.getPGram(words)), str(self.getSeqNGram(words)), str(iteration), song, group, videoid, str(self.startmsg.currentTime), str(self.currentTime), shortenedmidilink))
    
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

    