# Example 5 - Generating Score
# Author: Steven Yi <stevenyi@gmail.com>
# 2013.10.28
#
# Adapted for Python 3 by François Pinot, July 2021
#
# In this example, we will look at three techniques for generating our Score. 
# 
# The first is one we have already seen, which is to just write out the score
# by hand as a String.
#
# Knowing that we pass strings into Csound to pass note events, we can also
# generate the string.  In the second example, sco2 starts as an empty string.
# Using a for-loop, we append to sco2 note strings using a string formatting
# string that has its replacement values replaced.  The replace values are 
# calculated using the i value, and the result is an ascending note line. 
#


#how to save to midi?  not sure.  
#c.setMIDIOutput(midioutputdevicename/number)
#c.setMIDIFileOutput(testing.midi)
#https://csound.com/download
#https://git-scm.com/
#have to use CSCORE input for that I guess.  
#https://flossmanual.csound.com/midi/midi-output
#ok we have midi out, we have to adjust it to what it should be, it is the last 3 parameters.  
#have to calculate the key, and velocity
#0-127 range.  
#here is the frequency lookup https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
#so lets generate midi file at the same time.  
#then we can use the midi patterns and make some music.  
#check two patterns, make two tracks with midi, make sure it works.  
#can use the same instrument, but we distinguish tracks how exactly?  
#FrequencyToMidi, AmplitudeToMidi conversion functions
#devinjacobsondj/mrrubato project to store this code.  Point to this from youtube and vice versa.  
#financial world is morally bankrupt, and the moral world is financially bankrupt
#maybe eventually make it accessible/document.  
#https://docs.github.com/en/get-started/importing-your-projects-to-github/importing-source-code-to-github/adding-locally-hosted-code-to-github
#git init -b main
#git init && git branch -m main
#git add .
#git commit -m "First commit"
#git remote add origin  https://github.com/DevinDJdj/mrrubato.git
#git push --set-upstream origin main


import ctcsound
import sys
import math
import numpy
from functools import reduce
from random import randint

def printf(format, *args):
    sys.stdout.write(format % args)
    
# Our Orchestra for our project
orc = """
sr=44100
ksmps=32
nchnls=2
0dbfs=1
instr 1 
ipch = cps2pch(p5, 12)
kenv linsegr 0, .05, 1, .05, .7, .4, 0
aout vco2 p4 * kenv, ipch 
aout moogladder aout, 2000, 0.25
outs aout, aout
endin"""

# Example 1 - Static Score
sco = "i1 0 1 0.5 8.00"

f = open("../music/instruments/newage.orc", "r")
orc = f.read()
c = ctcsound.Csound() # create an instance of Csound
c.setOption("-odac")  # Set option for Csound
c.compileOrc(orc)     # Compile Orchestra from String

# Example 2 - Generating Score string with a loop
sco2 = ""
for i in range(13):
    sco2 += "i1 %g .25 0.5 8.%02g\n"%(i * .25,i)
#print sco2


# Example 3 - Generating Score using intermediate data structure (list of lists),
#             then converting to String.
vals = []           #initialize a list to hold lists of values 
for i in range(13): #populate that list
    vals.append([1, i * .25, .25, 0.5, "8.%02g"%(randint(0,15))])

# convert list of lists into a list of strings
vals = ["i" + " ".join(map(str,a)) for a in vals] 

# now convert that list of strings into a single string
sco3 = "\n".join(vals)
#print vals
#print sco3

sco4 = """
;---------------------------------------------------------------------------
; New Age Bull
; Copyright 1998 Hans Mikelson
;---------------------------------------------------------------------------
;  Sta   Dur
;a0 0     40      ; advance
;a0 86.8  140    ; advance
;a0 106.0  140    ; advance

; Sine Wave
f1  0 16384  10 1
f2 0   8192   7  -1  4096 1 4096 -1 ; Triangle Wave 1

; Mixer Tables
; 3=FadeIn, 5=FadeOut, 6=Const1, 7=Const.5
f3  0 1024 -7 0  1024 1           ; UpSaw/FadeIn/PanRL
f4  0 1024 -7 0  512 1 512 0      ; Tri/Pan RLR/Fade In&Out
f5  0 1024 -7 1  1024 0           ; DnSaw/FadeOut/PanLR
f6  0 1024 -7 1  1024 1           ; Const1/PanL
f7  0 1024 -7 .5 1024 .5          ; Const.5/PanC
f8  0 1024 -7 0  1024 0           ; Const0/PanR
f9  0 1024 -7 0  256 1  768 1      ; Voice Amp
f10 0 1024 -7 .5 256 .2 768 .8    ; Voice Pan CRL
f11 0 1024 -7 .5 256 .8 768 .2    ; Voice Pan CLR
f12 0 1024 -7 0  256 1  512 1 256 0 ; FadeIn-Hold-FadeOut
f13 0 1024  7 1  1024 -1            ; DownSaw2
f19 0  1024  19 .5 .5 270 .5



;---------------------------------------------------------------------------
; New Age Pluck
;---------------------------------------------------------------------------
;    Sta  Dur   Amp    Fqc    Func  Attack  OutCh  Sus
;i4  0  .2    10500  440   0     .040    10      0

;need to adjust duration here as applicable.  
;but we can generate the i4 anywhere, so lets do at the end.  
;I am not interested in the instruments at the moment.  
; so lets just generate the rythm and frequency and amplitude patterns we want with 
;this instrument.  
;then we can change the instrument.  
;this chorus and reverb is fine.  


"""

mixer = """
;---------------------------------------------------------------------------
; Clear ZAK
;---------------------------------------------------------------------------
; Clear Channels
i110 0  DUR

; Lorenz Oscillator for Chorus
;   Sta  Dur    Amp   X    Y    Z     S    R   B      h(rate)  OutKCh Offset
i8  0  DUR     4     7.8  1.1  33.4  10   28  2.667  1        1      25
i8  0  DUR     4    14.1 20.7  26.6  10   28  2.667  1        2      26
; Guitar Chorus
;   Sta  Dur   Mix  InCh  OutCh  InKCh 
i35 0  DUR    .5   10     2      1
i35 0  DUR    .5   10     3      2
; Mixer 3=FadeIn, 5=FadeOut, 6=Const1, 7=Const.5, 8=Const0
;    Sta  Dur  Amp  Ch  Pan  Fader  OutCh
i100 0  DUR   .8   2   6    6      20
i100 0  DUR   .8   3   8    6      .

; Large Room Reverb
;    Sta  Dur  Amp  InCh1 Gain1 InCh2 Gain2 InCh3 Gain3  
i105 0    DUR   0.4  20    1     23    1     25    1


"""

currentspeed = 1 #beats per second
currentstarttime = 0  #seconds
currentamplitude = 10000  #what is measurement here
currentfrequency = 20 #Hz

currentinstrument = 4
currenttime = 0
currentscale = 12

retarray = []
#allow speed vectors and amplitude vectors which will increase/decrease speed/amplitude
#over a certain time frame

#we can just adjust the speed if necessary

def setScale(s):
    global currentscale
    currentscale = s
    
def getCurrentSpeed():
    return currentspeed

def setCurrentSpeed(speed, multiplier=False):
    global currentspeed
    if (multiplier):
        currentspeed = getCurrentSpeed()*speed
    else:
        currentspeed = speed

def getCurrentTime():
    global currenttime
    return currenttime
    
def setCurrentTime(t, relative=False):
    global currenttime
    if (relative):
        currenttime += t
    else:
        currenttime = t

def getCurrentStartTime():
    global currentstarttime
    return currentstarttime
    
def setCurrentStartTime(st, relative=False):
    global currentstarttime
    if (relative):
        currentstarttime += st
    else:
        currentstarttime = st
    
def getCurrentAmplitude():
    return currentamplitude

def setCurrentAmplitude(amplitude, multiplier=False):
    global currentamplitude
    if (multiplier):
        currentamplitude = getCurrentAmplitude()*amplitude
    else:
        currentamplitude = amplitude

def getCurrentFrequency():
    return currentfrequency

def setCurrentFrequency(frequency, multiplier=False):
    global currentfrequency
    if (multiplier):
        currentfrequency = getCurrentFrequency()*frequency
    else:
        currentfrequency = frequency
        
def adjustFrequency(steps):
    global currentscale, currentfrequency
    currentfrequency = currentfrequency*2**(steps/currentscale)
    return currentfrequency

#if multiplier is true, it will multiply current values    
def setStart(instr, starttime, speed, amplitude, frequency, multiplier=False):
    global currenttime, currentstarttime, currentinstrument, currentspeed, currentamplitude, currentfrequency
    currentstarttime = starttime
    currenttime = starttime
    currentinstrument = instr
    if (multiplier):
        currentspeed = getCurrentSpeed()*speed
        currentamplitude = getCurrentAmplitude()*amplitude
        currentfrequency = getCurrentFrequency()*frequency
    else:
        currentspeed = speed
        currentamplitude = amplitude
        currentfrequency = frequency
        

def showNotes(melody, relative=True): #absolute or relative
    #reverse calculate the notes which we are playing from frequencies.  
    global currentscale, currentfrequency    
    return currentfrequency

def FrequencyToMidi(f):
    print(f)
    n = 12*(math.log(f/220)/math.log(2)) + 57
    #return 70
    return round(n)
    
def AmplitudeToMidi(a):
    #return 100
    return round(a/100)  

#=(1 chromatic, 2 major, 3, minor)
#need much more than this, but this is a start.  

def addscale(numofnotes, rythmspeed, scaletype, direction, speedvector, amplitudevector, startpos=0, relative=True, track=1):
    r = []
    m = []
    
    tmp = startpos+numofnotes*direction
    while (tmp < 0):
        tmp += 7
        startpos +=7
        
    if (direction < 0):
        rng = reversed(range(tmp, startpos))
    else:
        rng = range(startpos, tmp)
    r.append(rythmspeed)
    m.append(direction*0)
    for n in rng:
        r.append(rythmspeed)
        if (scaletype==1):
            m.append(direction*1)
        elif (scaletype==2):
            if (n%7==6 or (n%7)==2):
                m.append(direction*1)
            else:
                m.append(direction*2)
        elif (scaletype==3):
            if (n%7==4 or (n%7)==1):
                m.append(direction*1)
            else:
                m.append(direction*2)
        
    return addPattern(r, m, speedvector, amplitudevector, relative, track)


def isprime(n):
    for i in range(2, int(n/2)+1):
        if (n % i) == 0:
            return False

    return True
        
        
def getFactors(n):
    ret = []
    
    for i in range(1, int(n/2) + 1):
        if n % i == 0 and isprime(i):
            ret.append(i)
    if (ret is None):
        ret = [n]
    return ret

def getpascal(prime):
    ret = []
    current = 1
    num = prime
    denom = 1
    for i in range(0, prime+1):
        ret.append(current)
        current *= num/denom
        num -=1
        denom +=1
    
    print(ret)
    return ret        

def getFibonacci(num):
    ret = []
    current = 1
    ret.append(current)
    c1 = 1
    ret.append(c1)
    for i in range (1, num+1):
        ret.append(current+c1)
        temp = c1
        c1 = current+c1
        current = temp
        
    print(ret)
    return ret

def addDurationArray(row, i, mydur, ret=[], offset=0, current=1, basefre=440):
    a = []
    
    a.append(1)
    t = getCurrentTime()
    setCurrentStartTime(t)
    ret = numpy.empty(row[i])
    dur = getDurationArray(row, i, mydur, ret, 0, 1)
    print(dur)
    r = dur
    setCurrentTime(t)
    retm = numpy.empty(row[i])
    
    setCurrentFrequency(basefre*row[i])

    m = getFrequencyArray(row, i, basefre, retm, 0, 1)
    
    print(m)
    
    addPattern(r, m, s, a, False, i, 2)


def getDurationArray(row, i, mydur = 1, ret=[], offset=0, current = 1):
    start = row[i]
    if (i > 1 and current < 4):
        second = row[i-1]
        first = row[i-2]
        getDurationArray(row, i-1, mydur/2, ret, offset+first, current+1)    
        getDurationArray(row, i-2, mydur/2, ret, offset+0, current+2)
        addDurationArray(row, i-2, mydur/2, [], 0, 1)
        
        
    else:
        for j in range(offset, offset+start):
          #  print(j)
          #  print(mydur/start)
            ret[j] = mydur/start
            
    return ret


def getFrequencyArray(row, i, myfre = 1, ret=[], offset=0, current=1):
    start = row[i]
    if (i > 1 and current < 4):
        second = row[i-1]
        first = row[i-2]
        getFrequencyArray(row, i-1, myfre*row[i-1], ret, offset+first, current+1)    
        
        getFrequencyArray(row, i-2, myfre*row[i-2], ret, offset+0, current+2)
        
        
    else:
        for j in range(offset, offset+start):
            
            f = myfre*(row[current])/(row[current-1])
            while (f > 2000):
                f /= 2
            while (f < 100):
                myfre *= 2
            #print(j)
            #print(myfre)
            ret[j] = f
            
    return ret
        
def getArp(prime):
    if (prime == 2):
        if (getCurrentFrequency() <1760):
            return [0, 12]
        else:
            return [0,-12]
    if (prime == 3):
        return [-7, 7, -7]
    if (prime == 5):
        return [-5, -3, -4, 4, 3]
    if (prime == 7):
        return [-3, -3, -3, -3, 3, 3, 3]
    if (prime == 11):
        return [-2, -2, -2, -2, -2, -2, 2, 2, 2, 2, 2]
    if (prime == 13):
        return [-1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1]
    if (prime == 17):
        return [-1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1]
    else:
        ret = []
        for i in range(0, prime):
            if (i < prime/2):
                ret.append(-1)
            else:
                ret.append(1)
        return ret
#addarpeggio(#notestobeplayed, endnote, scaletype=(1 chromatic, 2 major, 3 minor), speedvector, amplitudevector, relative=True, track=1)
#how many notes to be played and the end note relative to starting note.  
#just randomly generate.  
#=(1 chromatic, 2 major, 3, minor)
def addarpeggio(numofrepetitions, rythm, scaletype, direction, speedvector, amplitudevector, startpos=0, relative=True, track=1):
    r = []
    m = []
    for bars in range(startpos, numofrepetitions+startpos):
        total = 0
        n = 3
        direction = -direction
        if (direction > 0):
            rng = range(0, len(rythm))
        else:
            rng = reversed(range(0, len(rythm)))
            
        r.append(rythm[0])
        m.append(direction*0)
        for i in rng:
            if (scaletype==1):
                total += direction*n
            elif (scaletype==2):
                if (i%3==0):
                    n = 4
                if (i%3==1):
                    n = 3
                if (i%3==2):
                    n = 5
            elif (scaletype==3):
                if (i%3==0):
                    n = 3
                if (i%3==1):
                    n = 4
                if (i%3==2):
                    n = 5

            r.append(rythm[i])
            m.append(direction*n)                
        
    return addPattern(r, m, speedvector, amplitudevector, relative, track)

#addfullness(
#include multiple notes in the scale whatever we are in.  Right now no way to know so just add 5th and octave.  


#function to crescendo for instance.  
#we want a multi-array which holds all values until the end?  

#what mathematical functions do we want to do?  
#add avg note between all notes for instance.  
#add rythm to all notes.  

#have a base pattern, and then add some random stuff.  
#have symetry and asymetry patterns.  
#need to have an object to know what notes go with what Patterns.  




def adjustSpeed(speedvector):
    #try this.  See if it works.  Havent tested.  
    #adjust the speed here.  
    global currentspeed, currentamplitude, currentfrequency, currentinstrument, currenttime, currentscale, retarray, currentstarttime
    beats = currenttime - currentsttarttime
    lens = len(speedvector)
    spsumtotal = sum(speedvector)
    spsum = 0
    spv = 0
    for idx, sp in enumerate(speedvector):
        speedvector[idx] = sp*(currentbeats/spsumtotal)
    
    spsumtotal = currentbeats
    for rowi, row in enumerate(retarray):
        
        if (row[1] < currenttime and row[1] > currentstarttime):
             c = 0
             spsum = 0
             while (row[1] < speedvector[c]):
                 c += 1
                 spsum += speedvector[c]
        
        
        #adjust here the currenttime and duration row[2]
        #duration adjustment will be speedvector[c]/(spsumtotal/lens)
        adj = speedvector[c]/(spsumtotal/lens)
        retarray[rowi][2] *= adj
        if (c > 0):
            #starttime adjustment will be (spsum/c)/(spsumtotal/lens)
            adj = (spsum/c)/(spsumtotal/lens)
            retarray[rowi][1] *= adj
        #make a time map of what goes where?  
        #this should be an easy mathematical transformation.  
        #just adjust to equal to 1, but where do we adjust
            ret = ""
    return ret
    
def adjustAmplitude(amplitudevector):
    #adjust the speed here.  
    global currentspeed, currentamplitude, currentfrequency, currentinstrument, currenttime, currentscale, retarray, currentstarttime
    beats = currenttime - currentstarttime
    lena = len(amplitudevector)
    ret = ""
    for idx, row in enumerate(retarray):
        if (row[1] < currenttime and row[1] > currentstarttime):
        #adjust here the amplitude row[3]
            #getampmultiplier
            multiplier = (row[1]-currentstarttime)/(currenttime-currentstarttime)
            multiplier *= lena
            retarray[idx][3] = row[3]*amplitudevector[int(multiplier)]
            ret = ""
    return ret

def addPattern(rythm, melody, speedvector, amplitudevector, relative=True, track=1, durmodulation=1):
    #speedvector will be an array based on the currentspeed, once that time is reached
    #amplitudevector is the amplitude adjustment over the period of time it takes for this sequence
    #rythm is simply how many beats at the currentspeed we take
    #melody is the frequency adjustment per note
    #rythm and melody must be equal length
    #after the full length is calculated, the speedvector and amplitudevector will be 
    #adjusted to the notes which they need to be at.  
    global currentspeed, currentamplitude, currentfrequency, currentinstrument, currenttime, currentscale, retarray
    ret = ""
    #i4  12  2.2    10500  440   0     .040    10      0
    
    i = 0
    while i < len(rythm):
        dur = rythm[i]
        amp = currentamplitude
        if (relative):
            fre = adjustFrequency(melody[i])
        else:
            fre = melody[i]
            #fre = currentfrequency*2**(melody[i]/currentscale)
        #calculate the midi note to output.  
        
        dura = dur/10
        #this must be > 0
        if dura < 0.01:
            dura = 0.01
        retarray.append([currentinstrument, currenttime, dur/durmodulation, amp, fre, dura, track])
#        ret += "i{0}  {1}  {2}  {3}  {4:.2f}    0   {5:.2f}    10  0    {6}   {7}  {8}\r\n".format(currentinstrument, currenttime, dur, amp, fre, dur/10, track, FrequencyToMidi(fre), AmplitudeToMidi(amp)) 
        i += 1    
        currenttime += dur
    #adjust current to final value of the vector
    #not sure if we want to adjust the currentfrequency here or not.  Preference
    if (relative==False):
        adjustFrequency(melody[len(rythm)-1])
        
    return ret


def printResult():
    ret = ""
    for row in retarray:
        ret += "i{0}  {1}  {2}  {3}  {4:.2f}    0   {5:.2f}    10  0    {6}   {7}  {8}\r\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], FrequencyToMidi(row[4]), AmplitudeToMidi(row[3])) 
    return ret

setScale(24)
setStart(4, 0, 1, 10000, 440)
r = [0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25]
m = [1,-1,-1,1,-1,-1,1,1]
s = [1,1.1,1]
a = [1,1.1,1]

#see if this works.  
test = '''
sco4 += addPattern(r,m,s,a, True, 1)
currenttime = 0
r = [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5]
m = [1,-1,-1,1,-1,-1,1,1]
s = [1,1,1]
a = [1,1.1,1]
sco4 += addPattern(r,m,s,a, True, 2)
'''

test = '''
currenttime=5
setCurrentStartTime(5)
#up5down5
sco4 += addscale(3, 0.5, 1, 1, s, a)
sco4 += addscale(3, 0.5, 1, -1, s, a, 3)
#up6down6
currenttime=5
for i in range(0, 4):
    currenttime=10
    setCurrentStartTime(10)
    sco4 += addscale(7, 0.5, 2, 1, s, a)
    sco4 += addscale(7, 0.5, 2, -1, s, a, 7)
    r = [1, 1]
    m = [4, 3]
    sco4 += addPattern(r, m, s, a, True, 3)
'''

#fractal pattern:
# 
# use Entire song period as the initial period.  
# divide in half and add a second tone perhaps.  
# within each half, generate a pattern the same way.  
# randomly give first or second half the tone.  
# the tone frequency relationship is undetermined, but must also have an interesting mathematical relationship.  
# i.e. 
#C1 0, 60
#C2 30, 30
#C3 45, 15
#..
#within this perhaps take circle of fifths naturally going up.  
#G1 0, 30
#G2 30, 30
#D2 0, 15
#D3 15, 15
#A3 0, 7.5
#A4 7.5, 7.5

#not sure this should be the final pattern, but I think we should generate this.  

fractal = '''
s = [1,1,1]
a = [1,1,1]
setScale(12)
myamp = 12000
basefre = 55
basemultiplier = 1.5 #2
fifthmultiplier = 1.33333 #1.5
setStart(4, 0, 1, myamp, basefre)
totaldur = 64
mydur = 64
myampmult = 0.95
while (mydur > 0.5):
    setCurrentStartTime(0)
    setCurrentTime(0)
    r = [mydur]
    m = [0]
    rand = randint(1,4)
    while (getCurrentTime() < totaldur-mydur):
        rand = randint(1,4)
        if (rand < 3):
            addPattern(r, m, s, a, True, 1)
        setCurrentTime(mydur, True)
    mydur /= rand
    setCurrentFrequency(basemultiplier, True)
    setCurrentAmplitude(myampmult, True)
    setCurrentStartTime(mydur, True)


fifthfre = basefre * 2 * fifthmultiplier 
setStart(4, 0, 1, myamp, fifthfre)
setCurrentStartTime(0)
mydur = 32
while (mydur > 0.03125):
    setCurrentStartTime(0)
    setCurrentTime(0)
    r = [mydur]
    m = [0]
    rand = randint(1,4)
    while (getCurrentTime() < totaldur-mydur):
        setCurrentTime(mydur, True)
        rand = randint(1,4)
        if (rand < 3):
            addPattern(r, m, s, a, True, 2)
    
    mydur /= rand
    setCurrentAmplitude(myampmult, True)
    setCurrentFrequency(fifthmultiplier, True)
'''



#circular pattern
circular = '''
how can we create a circular pattern?  
many individual scales which represent individual circles perhaps.  
maybe an individual circle represents a frequency for the start of the scale.  
So maybe all the scales are the same size.  and frequency is the speed.  
So the higher the frequency the larger the circle.  
What circles do we chose?  

Lets use several rotating circles on a sphere.  
what do the different circles on the sphere represent?  
What is a frequency that is rotated?  It adjusts the frequency.  
If we do that, we need to use the csound library to make an instrument.  
not the midi sequence.  
maybe different size freqencies travelling down the same path of rythm using the base rythm as some multiple of the freqency.  
Kind of like this concept.  
i.e. 55Hz represents 55*PI*2
and the rhythm pattern represents [1,2,1,2,1,2]
then we would have a rythm pattern for 55Hz being 55*PI*2*1 = currenttime
and next note starts 55*PI*2*2
The frequency becomes correlated with the duration.  
Kind of like we did with the fractal.  
But lets see how many different rythms we can combine.  We need a PRIMORIAL maybe to be the base pattern.  
So lets try 210 to start as our PRIMORIAL
So lets use just 55*2, 55*3, 55*5, 55*7.  
Or we can just combine all of these patterns into the one circle.  divide the same circle into 2, 3, 5, 7
Roll those down time, and when the spokes touch, we create sound, but what sound?  
What is the relationship between the spokes and frequency?  
Roll the circles inside of each other.  
When they meet, they make a sound of the frequencies related.  
i.e. 2 is rolling inside of 3, and 5, and 7.  
3 is rolling inside of 5 and 7
5 is rolling inside of 7.  
When they meet at a multiple there is additional sound.  
This essentially becomes a pattern of the factors of numbers.  
This is not really circular, but lets go with it.  
all numbers represent the points in time.  
For now lets just use unique factors.  Exponent just increases the amplitude of that note.  

Now use a circle with radius 2 and run it down the number line.  
Then a circle with radius 3 and do the same.  
And only make a sound when it comes into contact with a whole number.  
Also make the sound of the circle radius perhaps?  or combine it with the number itself.  
The radius number should be the loudest and the actual number (chorrd) a different volume.  
And then make the sound of what that number represents.  
So what sound does a number represent?  
Using primes is ok I think.  
Multiple circles going down the number line.  
If they overlap we have a sound which correlates to the relationship between whichever two are overlapping.  
What is that frequency?  
If they are close to a number, we create a sound based on that frequency.  


'''

circular = '''
s = [1,1,1]
a = [1,1,1]
setScale(12)
baseamp = 12000
basefre = 440
setStart(4, 0, 1, baseamp, basefre)
totaldur = 420
mydur = 0.125

pr = [2,3,5,7]
primorial = numpy.prod(pr)
i = 0

#pattern 1 use amplitude to distinguish pattern.  
for p in pr:
    basefre = 55*(p)/2
    setCurrentStartTime(0)
    setCurrentTime(0)
    circ = math.pi*2*p
    i = 0
    while (i < totaldur):
        i += 1
        ct = getCurrentTime()
        for q in pr:
            setCurrentTime(ct)
            mynum = (circ/q)*i
            rem = abs(mynum - round(mynum))
            amp = (0.5-rem)*(0.5-rem)*baseamp*4
            
            r = [mydur]
            m = [0]
            if (rem < 0.06125):
                setCurrentAmplitude(amp)
                setCurrentFrequency(basefre*(q-1))
                addPattern(r, m, s, a, True, p)
            else:
                setCurrentAmplitude(0)
                addPattern(r, m, s, a, True, p)
                
    #set a separate pattern for each 

setCurrentTime(totaldur*mydur)
'''
#pattern 2 use rhythm to distinguish pattern.  

pattern2 = '''
for p in pr:
    basefre = 440*p/2
    setCurrentStartTime(0)
    setCurrentTime(0)
    circ = math.pi*2*p
    i = 0
    while (i < totaldur):
        i += 1
        for q in pr:
            mynum = (circ/q)*i
            rem = abs(mynum - round(mynum))
            amp = (0.5-rem)*(0.5-rem)*baseamp*4
            
            setCurrentTime(mynum)
            r = [mydur]
            m = [0]
            setCurrentAmplitude(amp)
            setCurrentFrequency(basefre*p/2)
            addPattern(r, m, s, a, True, p)
setCurrentTime(totaldur*mydur)
'''

            

#pattern3
pascal = '''

s = [1,1,1]
a = [0.75,1.25,0.75]
setScale(12)
baseamp = 8000
basefre = 440
setStart(4, 0, 1, baseamp, basefre)
numrows = 17
totaldur = (numrows+1)
mydur = 2

i = 0

for i in range(numrows):
    if (i%2 == 0):
        basefre *= (i/(i-1))
    elif (i>1):
        basefre *= (i-1)/i
    row = getpascal(i)
    a = []
    for r in row:
        a.append(numpy.log(r)/math.sqrt(numrows))
    for r in row:
        
        factors = getFactors(r)
        t = getCurrentTime()
        setCurrentStartTime(t)
        for fc, f in enumerate(factors):
            setCurrentTime(t)
#            setCurrentFrequency(calculation here)
            r = numpy.empty(f)
            r.fill(mydur/f)
            m = getArp(f)
            
            addPattern(r, m, s, a, True, fc, 2)
            adjustAmplitude(a)    
            
    #set a separate pattern for each 
'''


#lets try to do a rhythm pattern with pascal triangle.  
#the pattern will reflect the numbers in the triangle, and each number will represent a beat.  
#play the odd patterns on 2* the odd.  
#so overlap the 1st row onto the second.  
#then 4th row is just 4th row.  
#6th row then is a combination of 3rd and 6th row.  
#do we keep adding or some other way?  
#could add up to 4 or 5 rhythms I suspect and still be distinguishable.  
#go up to 16.  
#1, 2, 4, 8, 16
#3, 6, 9, 12, 15
#5, 10, 15
#7, 14
#11
#13
#pull the internal pattern, from that previous line.  
#What rhythm patterns to combine?  
#factor each number in the individual pascal row, and use the factors as the beat pattern for that 1 beat.  
#is just going up the triangle sequentially best?  
#do we also use the internal factors to create extra beat patterns like below?  
#do we make more familiar beat blocks of 4, 8, 12, 16 or not by combining (INTERNAL PATTERN)
#maybe this is not necessary, except for perfect squares maybe add this.  
#1,1
#2 (1,1)
#3,1
#4 (2, 2)
#5, 3
#6 (3, 3), 2 (1,1)
#7, 1
#8 (4, 4)
#9 (3, 3, 3), 3
#10 (5, 5), 2 (1, 1)
#11, 1
#12 (6, 6)
#13, 3
#14 (7, 7), 2
#15 (5, 5, 5), 1
#16 (8, 8)


#I think just use the pattern for the factors.  i.e. 1, 5, 10 (2, 5), 20 (2, 2, 5), 10 (2, 5), 5, 1
#not sure exactly how to do this, but divide evenly into the number of factors that we have.  
#do the pattern starting with separate notes.  
#if we have the same number twice or 3 times, we start at different octaves.  
#i.e. 20 will have 3 notes, 2 with pattern 2, and 1 with pattern 5.  
#if we have multiple factors we can use different tracks/instruments.  
#for now the track will equal the factor#, like if there are 3 factors, we have track 1, 2, 3 for those three factors.  
#start at same octave and go up/down if there are multiple.  
#then just for now sequentially use the factors as the rhythm.  Leave one beat space at the end to understand the pattern.  
#lets try also with one note per factor.  I think this will be better.  

#but what notes?  
#lets try an arpeggiation of some kind with the rhythm.  
#lets make it random arpeggiation of some kind (skip or not skip next step in arpeggiation is random).  
#up or down is random based on what frequency we are at.  
#what is the key though?  
#where do we start?  
#track will equal to the rhythm pattern.  
#lets just do a simple chord progression.  
#Use the middle of the pascal triangle to find the key, then work out from there.  
#1, 2, 3, 6, 10, 20, 35
#*2, *2/3, *6/3, *6/10, *20/10, *20/35, *70/35, etc.  
#I think this should be fine for initial starting range.  
#what is our frequency range?  lets say 220 to 220*16.  
#same way we go up or down based on the factor.  What do we do when we go out of range, just correct direction?  For now this is fine.  
#2 pattern is Base, Base*2 or Base/2
#3 pattern is Base, Base*3/2 *2/3
#5 pattern lets do Base, Base*5/4 *5/4, *4/5 *4/5?  
#7 pattern as well, Base, Base*7/6 *7/6 *7/6, *6/7 * 6/7 * 6/7.  



#how do we adjust amplitude?  each number has an amplitude adjustment.  
#row increases in amplitude and decreases back after the middle.  
#runs all decrease amplitude going up, and increase coming back down.  
#simple amplitude pattern.  
#I think this is everything for now.  




#1
#1 1
#1 2 1
#1 3 3 1




#fibonacci
#use the rhythm pattern here.  
#P = Previous
#1, 1, [1, 1], [[1,1],[1]], [[ [1,1], [1]], [1,1]], [[[ [1,1], [1]], [1,1]], [[1,1],[1]]], etc..  
#what frequency or chord pattern?  
#lets use chorrd progression here somehow.  
#how can we relate KEY to Fibonacci?  Use the fibonacci numbers themselves and/or factors?  to determine the chorrd relationships.  
#i.e. 1 = BASE*1, 2 = BASE*2, 3 = BASE*3, 5 = BASE*3, BASE*2, 8 = BASE*5, BASE*3, 13 = BASE*8, BASE*5, etc.  

#then bring it down the same way we bring down the speed.  
#so after 4, we reduce speed, and during that we bring down BASE one octave.  
#1, 1, (1,1), (2,1), BASE and SPEED /=2, (3,2), (5,3), (8, 5), (13,8), BASE and SPEED /=4, (21, 13), (34, 21), (55, 34), (89, 55), BASE and SPEED /=8, ....
#is this octave change appropriate?  
#same note or arpeggiation?  
#use one chord for the first half and the second for the second.  Yeah I think I like that.  
#how far do we go.  
#slow down the series after 4 or 8 by half and repeat and make it obvious we are slowing down
#use different instrument for that.  
#1, 1, [P, P-1], [P, P-1], etc.  

#fibonacci = '''

s = [1,1,1]
a = [0.75,1.25,0.75]
setScale(12)
baseamp = 8000
basefre = 440
setStart(4, 0, 1, baseamp, basefre)
numrows = 10
mydur = 2

i = 0
row = getFibonacci(numrows)


mydur = 4.0

for i in range(numrows):

    addDurationArray(row, i, mydur, [], 0, 1, basefre)

for i in reversed(range(numrows)):

    addDurationArray(row, i, mydur, [], 0, 1, basefre)

    originalfibonacci='''        


    a = []
    
    a.append(1)
        
#    while (row[i] > mydur*2):
#        mydur *=2
    t = getCurrentTime()
    setCurrentStartTime(t)
    ret = numpy.empty(row[i])
    dur = getDurationArray(row, i, mydur, ret, 0, 1)
    print(dur)
    r = dur
    setCurrentTime(t)
    #this should be in the getDurationArray.  We should adjust frequency and amplitude.  
    #start of the fibonacci pattern is louder.  And start of any sequence louder.  
    #also melody should start again at any sequence.  And just choose some easy notes.  
    #so we need the note also defined.  BASE, BASE*2, BASE*3, but need it to be additive.  
    #when we are playing the 3, we have 2, then 1, we use the BASE*3 along with whatever the notes were in the previous.  
    #same with 5, we build upon the notes, for 3 we have (1, 1), 1 and we can use BASE*1, BASE*2 and BASE*3
    #2 would be BASE*1*BASE*2
    #or make all frequencies the factor of N, so for instance we can use (1, 1) as BASE*2*BASE*1*(BASE*1.5), and then BASE*1*BASE*3
    #same for 5, we have 3 and 2, and so we have the same notes BASE*2*1*1.5*1.666, then BASE*1*2*2.5
    #so the frequencies we expierience are building.  
    #8 would be BASE*2*1*1.5*1.666*1.6
    #or just use the note which completes the series during that time period.  
    #how many notes do we want to include?  
    #1*2/1*3/2*5/3*8/5*13/8*21/13
    #perhaps make it additive throughout.  
    #for instance on 5 we use 

    #j = i
    #while (j > 0)
    #setCurrentTime(t)
    #setCurrentStartTime(t)
    #setCurrentFrequency(basefre*row[j])
    retm = numpy.empty(row[i])
    
    setCurrentFrequency(basefre*row[i])

    m = getFrequencyArray(row, i, basefre, retm, 0, 1)
    #ok now get multiple notes per...
    #if it has a number then we should add the frequency.  
    #so for each iteration through the recursive function, we need to add frequency.  
    
    print(m)
    #m = getArp(row[i])
    
          
#    addPattern(r, m, s, a, True, 1, 2)
    addPattern(r, m, s, a, False, 1, 2)
'''
    #so we would need multiple patterns here
    #but just using a different frequency and only part of the duration array.  
    
#    adjustAmplitude(a)    
            
    #set a separate pattern for each 

#'''


#NUMBER LINE 
numberline = '''
Each number represents the wavelength of the sound starting with 1.  
Wavelength of 1 will be middling (880Hz?), as this will be near the most played notes.  
Each multiple of 2 will switch to below or above the 880Hz.  
Every other number will have the pitch adjusted in some way.  
Each number only plays the sound of the Factors.  
With more factors, the amplitude is decreased for each note.  
Less factors, the amplitude is increased, and the length of note is increased, or repeated around the average number of factors.  
Rhythm is included based on the average number of factors for any number at that point.  
What rhythm we can make somewhat random, or based on the lowest prime numbers which were included in that set of notes.  
Have the set include the lowest prime number LATEST ENTRIES.  
Within that set you will have a lowest prime number and that is your next number of LATEST ENTRIES
Within that set, we generate rhythm based on all the prime factors which exist.  
Rhythm is just a tuplet of the lowest prime number for now.  
This should be expanded in some interesting fashion, but no good ideas yet.  
Which notes are included, use the lowest prime number as the base Hz, so for instance 880/5 = 176
Then all numbers above that lowest prime are calculated from this, and of course use 2 to decrease the frequency to an audible range.  
Not sure if we should use rhythm to represent the number of notes etc.  
We could use all of the frequencies of the prime numbers or the most used prime numbers as kind of a background beat.  
Tempo is slowed based on the number of factors as that increases.  

Dont worry about 2 switching, just divide by the highest multiple of 2, i.e. /8 or /16 etc.  
If we do this, perhaps we dont need the logic stated above.  
This is also easier to calculate.  
But higher numbers will get some large octave jumps.  
If it is inaudible, just leave it for now.  
All other factors divided by the 2^n.  
Amplitude increased for how many factors.  
i.e. 7, 8, 9 only use 3 items because 3 is the lowest factor.  
 = 3,3,7, so 3/8 Amplitude*2*amplitudefactor?  and 7/8
This will switch the octaves based on the notes anyway.  
8, 9, 10 = 3, 3, 5 so again 3/8 Amplitude*2*amplitudefactor and 5/8
9,10,11 = 3,3,11 and this is 3/2 Amplitude*2*amplitudefactor and 5/2 and 11/2
10,11,12 this will always be 3 numbers.  Just the factors and rhythm change.  
= 3,5,11  /4 
How could we increase the number of elements?  
Or do we want to?  
Many numbers will be inaudible.  Maybe start a bit lower.  440Hz?  

Frequency is fine, but I think rhythm needs to be something else than just the tuplets.  
Or do something the same like inlcude all fo the factor numbers, like include 3, 5, 11 again underneath.  
So 5 would be 5/4 and 3/4
3 would be 3/2
11 is 3/2, 5/2, 11/2
only do up to 3.  
SO all rhythms and notes of these will be included.  
Also do we continue the recursion?  I think so.  Basically we adjust the tempo for however many recursions occurred, or however many unique factors there are.  
This ends up just being octaves, but it will not always be the case.  

Dont take the lowest prime, take the lowest prime of the current number.  
So all primes will include all numbers up to that point which becomes all primes up to that point / largest 2^n.  
Go up to 210 perhaps.  
Maybe rhythm only used from the lowest prime number of elements.  
But harmony used from all?  No that's too busy.  Maybe just do the 3 elements.  And maybe recurse.  
This will work better musically.  Mathematically not so nice.  
What can we do other than tuplets for rhythm?  
Emphasize more the closer it is to the actual number we are on, or if it is a factor of the number we are on.  
Amplitude calculation here.  
If it is a factor of the number do the tuplet of the opposite from the largest prime.  i.e. 12 = 3/4, 6/4, 9/4, 12/4
10 = 5/2, 10/2
28 = 7/4, 14/4, 21/4, 28/4
56 = 7/8, 14/8, etc.  
All these overtones of the highest prime number.  
Or only pick some of these overtones based on the other primes which we have.  
Play these notes over and over in a tuplet of the prime?  
And then pick these notes of any other factors which exist.  
i.e. 60 = 5/4, 10/4, 15/4, 20/4, etc.  
and then pick each third.  15/4, 30/4 etc.  



Maybe this will make for more interesting harmony.  
Do the opposite for others which are not the number going down.  Maybe this will bring out some distinction.  

Primes are just one single note with all primes up to that point?  Or some of the primes up to that point 1/ln(p) perhaps.  
Every prime has this chance of being selected.  Primes will only have a chord.  


Further Details to be determined.  

'''




#up6down6
#currenttime=5
#sco4 += addscale(9, 0.5, 3, 1, s, a)
#sco4 += addscale(9, 0.5, 3, -1, s, a, 9)

#sco4 += addarpeggio(2, [0.5,0.5,0.5,0.5,0.5,0.5], 1, -1, s, a)
#sco4 += addarpeggio(2, [0.5,0.5,0.5,0.5,0.5,0.5], 2, -1, s, a)
#sco4 += addarpeggio(2, [0.5,0.5,0.5,0.5,0.5,0.5], 3, -1, s, a)

adjustAmplitude(a)
sco4 += printResult()

mixer = mixer.replace("DUR", "{}".format(currenttime))
sco4 += mixer
print(sco4)



#c.readScore(sco)      # Read in Score from pre-written String
#c.readScore(sco2)     # Read in Score from loop-generated String
#c.readScore(sco3)     # Read in Score from loop-generated String
c.readScore(sco4)

c.setMIDIFileOutput("./output/testing.midi")

c.start()             # When compiling from strings, this call is necessary before doing any performing

# The following is our main performance loop. We will perform one block of sound at a time 
# and continue to do so while it returns 0, which signifies to keep processing.  

while (c.performKsmps() == 0):
  pass

c.stop()