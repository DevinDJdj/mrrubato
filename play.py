notes = """
change instrument:
from mido import Message, MidiFile, MidiTrack
track = MidiTrack()
...
track.append(Message('program_change', program = 36,
                     time = 1234, channel = 0)
                     

track.append(Message('control_change', control =  0, value = 0x79, channel = 0, time = 1233))
track.append(Message('control_change', control = 32, value = 0x05, channel = 0, time = 1233))
track.append(Message('program_change', program = 0x7a,             channel = 0, time = 1234))

Playback on external:
Can we use this library?  
http://ajaxsoundstudio.com/pyodoc/index.html

Initial sample here:
https://natespilman.com/blog/playing-chords-with-mido-and-python/
"""


import mido
from time import sleep
from random import randint
from mido import Message, MidiFile, MidiTrack

def note(note,velocity = 64, time = 2):
    velocity_modification = randint(-20,20)
    return mido.Message('note_on',note=note,velocity = velocity + velocity_modification, time=time)

def note_off(note,velocity = 64, time=2):
    return mido.Message('note_off',note=note,velocity = velocity, time=time)



outputs = mido.get_output_names()
print(mido.get_output_names())

outport = mido.open_output(outputs[0])


mid = MidiFile('testing.midi')
for i, track in enumerate(mid.tracks):
    print('Track {}: {}'.format(i, track.name))
    for msg in mid.play():
        outport.send(msg)
    

def pause():
    sleep(randint(0,100) * .0005)

def majorChord(root ,duration):
    outport.send(note(root))
    pause()
    outport.send(note(root+4))
    pause()
    outport.send(note(root+7))
    pause()
    sleep(duration)
    outport.send(note_off(root))
    outport.send(note_off(root+4))
    outport.send(note_off(root+7))

def minorChord(root ,duration):
    outport.send(note(root))
    pause()
    outport.send(note(root+3))
    pause()
    outport.send(note(root+7))
    sleep(duration) 
    outport.send(note_off(root))
    outport.send(note_off(root+4))
    outport.send(note_off(root+7))
    
C = 60 
G = 55 
A = 57 
F = 53 


while True:
    majorChord(C,1)
    majorChord(G,1)
    minorChord(A,1)
    majorChord(F,1)
    majorChord(F,1)
    majorChord(G,1)
    majorChord(C,2)
    