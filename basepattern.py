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

def getCurrentStartTime():
    return starttime
    
def setCurrentStartTime(st):
    global currentstarttime
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
    #adjust the speed here.  
    global currentspeed, currentamplitude, currentfrequency, currentinstrument, currenttime, currentscale, retarray, currentstarttime
    beats = currenttime - currentsttarttime
    lens = len(speedvector)
    for row in retarray:
        if (row[1] < currenttime and row[1] > currentstarttime):
        #adjust here the currenttime and duration row[2]
            ret = ""
    return ret
    
def adjustAmplitude(amplitudevector):
    #adjust the speed here.  
    global currentspeed, currentamplitude, currentfrequency, currentinstrument, currenttime, currentscale, retarray, currentstarttime
    beats = currenttime - currentstarttime
    lena = len(amplitudevector)
    for row in retarray:
        if (row[1] < currenttime and row[1] > currentstarttime):
        #adjust here the amplitude row[3]
            #getampmultiplier
            multiplier = (row[1]-currentstarttime)/(currenttime-currentstarttime)
            multiplier *= lena
            row[3] = row[3]*amplitudevector[int(multiplier)]
            ret = ""
    return ret

def addPattern(rythm, melody, speedvector, amplitudevector, relative=True, track=1):
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
            fre = currentfrequency*2**(melody[i]/currentscale)
        #calculate the midi note to output.  
        
        retarray.append([currentinstrument, currenttime, dur, amp, fre, dur/10, track])
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

setScale(12)
setStart(4, 0, 1, 10000, 440)
r = [0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25]
m = [1,-1,-1,1,-1,-1,1,1]
s = [1,1.1,1]
a = [1,1.1,1]

#see if this works.  
sco4 += addPattern(r,m,s,a, True, 1)
currenttime = 0
r = [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5]
m = [1,-1,-1,1,-1,-1,1,1]
s = [1,1,1]
a = [1,1.1,1]
sco4 += addPattern(r,m,s,a, True, 2)


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

c.setMIDIFileOutput("testing.midi")

c.start()             # When compiling from strings, this call is necessary before doing any performing

# The following is our main performance loop. We will perform one block of sound at a time 
# and continue to do so while it returns 0, which signifies to keep processing.  

while (c.performKsmps() == 0):
  pass

c.stop()