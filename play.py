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
import os
import glob
from oauth2client.tools import argparser, run_flow


def note(note,velocity = 64, time = 2):
    velocity_modification = randint(-20,20)
    return mido.Message('note_on',note=note,velocity = velocity + velocity_modification, time=time)

def note_off(note,velocity = 64, time=2):
    return mido.Message('note_off',note=note,velocity = velocity, time=time)


def get_latest_file():
    list_of_files = glob.glob('C:/Users/devin/Videos/*.mid') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    return latest_file



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
    

if __name__ == '__main__':
    argparser.add_argument("--speed", help="Speed multiplier upload",
      default="1.0") #--rerun true perhaps add other options but right now this is all that really fails.  
    args = argparser.parse_args()

    outputs = mido.get_output_names()
    print(mido.get_output_names())

    #Portable Grand-1 2
    outport = mido.open_output(outputs[len(outputs)-1])


    mid = MidiFile(get_latest_file())
    
    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        for msg in track:
            if hasattr(msg, 'note'):
                msg.time = msg.time
                msg.time = float(msg.time) * float(args.speed)
            
    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        for msg in mid.play():
  #          msg.velocity = round(msg.velocity / 2)
            outport.send(msg)
            print(msg)
    

    test = """
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
    """