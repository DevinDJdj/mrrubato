#git config http.postBuffer 524288000
#git reset --soft HEAD^1
#pip install google-api-python-client
#npm install -g firebase-tools
#https://misterrubato-test.web.app
#https://console.firebase.google.com/u/1/project/misterrubato-test/hosting/sites?hl=en-US
#category 10 is music
#python ./upload.py --file="./input/test.mp4" --title="Test Upload" --description="Wow this should be easy" --keywords="music, piano" --category="10" --privacyStatus="private"
#ffmpeg -i "2022-12-13 12-32-17.mkv" -codec copy "2022-12-13 12-32-17.mp4"
#python ./upload.py --file="./input/2022-12-13 12-32-17.mkv" --title="Test Upload" --description="Wow this should be easy" --keywords="music, piano" --category="10" --privacyStatus="private"
#python ./upload.py --file="./input/2022-12-12_13-46-58.mkv" --title="Test Upload" --description="Wow this should be easy" --keywords="music, piano" --category="10" --privacyStatus="private"
#python ./upload.py --file="./output/testmidi/2022-12-22 20-43-48.mkv" --title="Test Upload" --description="Wow this should be easy" --keywords="music, piano" --category="10" --privacyStatus="private"


#!/usr/bin/python
#getting stuff for image processing.  
#pip install opencv-python

#pip install mido
#pip install rtmidi
#pip install py-midi
#pip install python-rtmidi
#install vc++ redistributable.  

#from midi file get start times and stop times.  
#for now just use the next note after the start video/stop video (21/22)
#and the pause/unpause (108?)
#use note prior to pause to indicate end.  
#use note after unpause to indicate next iteration.  
#use note before stop video to indicate end.  
#1st (), 1st end ()
#2nd (), 2nd end ()


#import httplib
import httplib2
import os
import glob
import random
import sys
import time
import cv2
import pytesseract
from PIL import Image
import numpy as np
import string

import mido
from mido import Message, MidiFile, MidiTrack

from mido.ports import MultiPort


#midiIn = MidiIn()
 
#def printNote(eventType, channel, data1, data2):
#   print ("pitch =", data1, "volume =", data2)
 
#midiIn.onNoteOn(printNote)
 
# since we have established our own way to process incoming messages,
# stop printing out info about every message
#midiIn.hideMessages()
    
if __name__ == '__main__':
#    mido.set_backend('mido.backends.portmidi')   
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    inputs = mido.get_input_names()
    print(mido.get_input_names()) 
    with mido.open_input(inputs[1]) as inport:
        for msg in inport:
            if msg:
                print(msg)
                track.append(msg)
                if hasattr(msg, 'note') and msg.note == 22:
                    break
    list_of_files = glob.glob('C:/Users/devin/Videos/*.mkv') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    fn = latest_file.split('.')
    mid.save(fn[0] + '.mid')
    
    