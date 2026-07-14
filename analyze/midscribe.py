#get pertinent info from midi file between iterations..
#read OLD language and new language if possible and transcribe..
#get all instrument changes and annotate all between iteration events.  

import datetime
import sys
 
# adding Folder_2/subfolder to the system path
sys.path.insert(0, 'c:/devinpiano/music/analyze')


from oauth2client.tools import argparser, run_flow
import firebase_admin
from firebase_admin import credentials, initialize_app, storage, firestore, db
# Init firebase with your credentials

import os
import requests

from mido import MidiFile
from mido import Message

import mymidi

import analyze

#assume default piano for now..
mymsb = 108
mylsb = 0
mypc = 1


#enough for sample..
#add as find likable sounds.. or bulk update with dictionary..
#https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2
instruments = {
    (108, 0, 1): "CFX Grand",
    (0, 122, 1): "CFX Grand (Natural)",
    (0, 123, 1): "Bright Piano",
    (0, 124, 3): "Rock Piano",
    (0, 123, 4): "Octave Piano",
    (104, 20, 4): "Cocktail Piano",
    (104, 19, 4): "Ambient Piano"
}

def instrumentChange():
    global mymsb, mylsb, mypc, instruments
    if (mymsb, mylsb, mypc) in instruments:
        return instruments[(mymsb, mylsb, mypc)]
    else:
        print("Unknown instrument change: MSB: " + str(mymsb) + " LSB: " + str(mylsb) + " PC: " + str(mypc))
        return "Unknown Instrument"
    
def printNote(msg, midiTime, startTimes, endTimes, iteration):
    global mymsb, mylsb, mypc
#    print(str(iteration) + " " + str(msg.msg.time) + " " +   str(midiTime) + " ")
 #   print(startTimes)

    print(msg.msg)
    if (msg.msg.type == 'program_change'):
        print("Program change: " + str(msg.msg.program) + " on channel: " + str(msg.msg.channel))
        mypc = msg.msg.program + 1 #0 indexed, but doc is 1 indexed..
        #https://data.yamaha.com/files/download/other_assets/8/1345698/dgx670_en_dl_b0.pdf

        instrument = instrumentChange()
        print("Instrument: " + instrument)

    if (msg.msg.type == 'control_change'):
#        print("Control change: " + str(msg.msg.control) + " value: " + str(msg.msg.value))
        if (msg.msg.control == 64):
            if (msg.msg.value > 0):
                print("Pedal on")
            else:
                print("Pedal off")
        if (msg.msg.control == 1):
            print("Mod wheel: " + str(msg.msg.value))
        if (msg.msg.control == 11):
            print("Expression: " + str(msg.msg.value))
        if (msg.msg.control == 7):
            print("Volume: " + str(msg.msg.value))
        if (msg.msg.control == 32):
            #instrument change LSB
            print("Instrument change: " + str(msg.msg.value))
            mylsb = msg.msg.value
            instrument = instrumentChange()
            print("Instrument: " + instrument)
        if (msg.msg.control == 0):
            #instrument change MSB
            print("Instrument change: " + str(msg.msg.value))
            mymsb = msg.msg.value
            instrument = instrumentChange()
            print("Instrument: " + instrument)
        
    if (msg.msg.type == 'note_on'):
        print("Note on: " + str(msg.msg.note) + " velocity: " + str(msg.msg.velocity))

if __name__ == '__main__':
    argparser.add_argument("--midi", help="Midi Link", default="")
    argparser.add_argument("--videoid", help="Video ID", default="")
    argparser.add_argument("--localfile", help="Local filename", default="None")
    argparser.add_argument("--force", help="Force reanalyze", default="false")
    args = argparser.parse_args()

    videoid = args.videoid
    midilink = args.midi
    localfile = args.localfile
    force = args.force == "true"
    cwd = os.getcwd()
    print(cwd)
    print("Start midscribe!")
    print(midilink)
    print(datetime.datetime.now())
    
    cred = credentials.Certificate("c:\\devinpiano\\misterrubato-test.json")
    databaseURL = "https://misterrubato-test-default-rtdb.firebaseio.com/"
    initialize_app(cred, {'storageBucket': 'misterrubato-test.appspot.com', 
                          'databaseURL': databaseURL})
        

    midilink = midilink.replace("\r", "")
    midiname = os.path.basename(midilink)
    midiname = os.path.splitext(midiname)[0]
    midiname = midiname.replace('%20', ' ')
    filename = midiname + '.txt' #not sure if we want specific extension here.  

    toignore = 540 #dependent on mkv or mp4
    #cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture("C:\\Users\\devin\\Videos\\2023-08-03 15-38-56.mkv")
    inputpath = 'C:\\Users\\devin\\Videos\\'
    sys.path.insert(0, 'C:\\Users\\devin\\Videos\\')
    #mkv saved locally already
    path = './output/'
        
    #dont redo this.  Live with the analysis of the time for now.  
#    if (os.path.exists(os.path.join(path , filename))):
#        print("Skipping " + filename)
#        print("Already exists")
#        sys.exit(0)

    #use the file from analyze.py
    #should change local name
#    midiname = midiname.replace('%20', ' ')
    if (os.path.exists(inputpath + midiname + ".mid") and not force):
        print("Skipping midscribe " + midilink)
        sys.exit(0)
    else:

        r = requests.get(midilink)
        print(len(r.content))
        midisize = len(r.content)
        if (len(r.content) < 200): #not sure why this is here.  Change 500->200
            print(r.content)
            sys.exit(0)
        
        with open(inputpath + midiname + ".mid", "wb") as f:
            f.write(r.content)

    mid = MidiFile(inputpath + midiname + ".mid")
        
    print("midscribe " + midiname)
    mid = MidiFile(inputpath + midiname + ".mid")
    #ok with this midi file
    #after use 
    t = analyze.getControl(mid) #get between iteration changes..
    starttimes, endtimes = analyze.getTrackTimesControl(t) #control times starttimes = should be time between end/start of iterations..
    mid2 = MidiFile(inputpath + midiname + ".mid")
    t2 = analyze.enhanceMidi(mid2) #dont screw up other msgs
    starttimes2, endtimes2 = analyze.getTrackTimes(t2) #note times, should be time between end/start of iterations..
    print("controlstart/controlend/itstart2/itend2 times: ")
    print(starttimes)
    print(endtimes)
    print(starttimes2)
    print(endtimes2)

#    img = analyze.midiToImage(t, midilink)
#    cv2.imshow("MIDI", img) 
    #uploadanalyze(filename, os.path.join(path, filename))
    
    
    notecnt = 0
    ctrlcnt = 0
    midiTime = 0.0
    prevTime = 0.0
    i = 0
    on = 0
    f = open(path + filename, "w")
    
    previteration = 0
    
    lag = 100
    prevnote = 21
    startnote = 0
    for mymsg in t.notes:
        # Read each frame from the webcam
        #which do we move forward, next note or next frame?  
        notecnt += 1
        if (prevnote in [21,22,105,106,107,108] or mymsg.note in [21,22,105,106,107,108] ):
            printNote(mymsg, midiTime, starttimes, endtimes, iteration=i)
            #did we not get rid of this?  

        midiTime += mymsg.msg.time
        i = analyze.getIteration(midiTime, starttimes, endtimes)
        #not very efficient, but good enough for now.  
        if (i < -1):
            printNote(mymsg, midiTime, starttimes, endtimes, iteration=i)
#                f.write(str(midiTime) + ' ' + str(mymsg.note) + '\n')
        if (i != previteration):
            print("note count for iteration " + str(previteration) + ": " + str(notecnt))
            print("control count for iteration " + str(previteration) + ": " + str(ctrlcnt))
            print(str(previteration) + " midscribe completed ")
            previteration = i
            notecnt = 0
            ctrlcnt = 0

        if (mymsg.msg.type=='note_on'):
            on = analyze.isOn(mymsg.note, on)
        elif mymsg.msg.type == 'control_change':
            ctrlcnt += 1
        prevnote = mymsg.note
        
        
    # release the webcam and destroy all active windows
    f.close()
    print("midscribe completed")

