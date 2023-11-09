#https://techvidvan.com/tutorials/hand-gesture-recognition-tensorflow-opencv/
#idea is to create something which recognizes which fingers are used with which notes with the midi file.  
#similar to analyze, but just testing if we can do this.  
#interesting cant use this while OBS is running for some reason.  
#anyway dont worry about real time for now.  
#looks like it will still display partial fingers?  Have to check with a MKV.  
#ok, seems ok, but Needed to add a little more space at the bottom of the piano.  
#I think thats fine.  This has some difficulty checking the thumb.  
#so check perhaps after some newer videos.  
#doesnt work great.  Really needs the arm it seems from this model.  
#so for us work back from the midi, and try to determine which finger it was.  
#maybe we can use this?  Yeah dont want to do this work myself so use something like this. 
#just combine intelligently with detection of the keys themselves, and correlate with midi.  
#what time was the button pressed?  Which finger was there at that time?  
#can we detect from the video pressed or not?  
#not sure if it is worth it if the midi timing is precise enough.  
#thumb detection is bad with low confidence.  
#check after some more videos.  
#--video videoid --midi midilink



#maybe it is an exclusive stream?  
#pip install mediapipe
#pip install tensorflow
#pip install protobuf==3.20.3

import datetime
import sys
 
# adding Folder_2/subfolder to the system path
sys.path.insert(0, 'c:/devinpiano/music/analyze')


import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model

from oauth2client.tools import argparser, run_flow
import firebase_admin
from firebase_admin import credentials, initialize_app, storage, firestore, db
# Init firebase with your credentials

import os


from mido import MidiFile
from mido import Message

import mymidi

import analyze


def getFingerNum(hand, idx):
    offset = 0
    if (hand=="Left"):
        offset = 5
    if (idx%4==0 and idx > 0): #this is all the fingertips 4, 8, 12, 16, 20
        if (offset == 0):
            return int(5 - (idx/4) + 1)
        else:
            return int(offset + idx/4)
    else:
        return -1


def getNoteCoord(msg, width):
    temp = msg.note - 21
    #roughly 1200/88 per note ~ 14 bits
    ret = ((temp)/88)*(width-20) + 10 #+10 for the piano location in frame
#    print(ret)
    return ret
    

def showKeys(landmarks, width):
    for idx in range(10):
        temp = landmarks[idx,0]
        key = ((temp-10)*88/(width-20)) + 21
        print("Finger " + str(idx) + " on " + str(key))
        
def getClosestFinger(notex, landmarks):
    closestidx = 0
    closestl = 1000
    closestl2 = 1000
    closestidx2 = 0
    for idx in range(10):
        temp = abs(landmarks[idx,0]-notex)
#        print(landmarks[idx,0])
        if (temp < closestl):
            closestl = temp
            closestidx = idx+1
        elif (temp < closestl2):
            closestl2 = temp
            closestidx2 = idx+1
    if (closestl > 30 and closestidx not in [1,5,6,10]):
        closestidx = -closestidx
    elif (closestl > 40):
        closestidx = -closestidx
    #maybe need more logic than this, but for now leave as is.  
    #i.e. if this is 1, 5, 6, 10, then forgive some.  
    
    return closestidx, closestl
    
def getFinger(msg, landmarks, width):
    notex = getNoteCoord(msg, width)
    fingeridx, fingerl = getClosestFinger(notex, landmarks)
  #  print("Note" + str(msg.note) + " Played with " + str(fingeridx) + " Distance " + str(fingerl))
    return fingeridx

def printNote(msg, startnote, midiTime, frameTime, startTimes, endTimes):
    print(str(msg.note) + " " +  str(msg.msg.time) + " " +   str(midiTime) + " " + str(frameTime) + " ")
    print(startTimes)

if __name__ == '__main__':
    argparser.add_argument("--midi", help="Midi Link", default="")
    argparser.add_argument("--videoid", help="Video ID", default="")
    argparser.add_argument("--localfile", help="Local filename", default="None")
    args = argparser.parse_args()

    videoid = args.videoid
    midilink = args.midi
    localfile = args.localfile
    cwd = os.getcwd()
    print(cwd)
    print("Start finger analysis!")
    print(midilink)
    print(datetime.datetime.now())
    
    cred = credentials.Certificate("c:\\devinpiano\\misterrubato-test.json")
    databaseURL = "https://misterrubato-test-default-rtdb.firebaseio.com/"
    initialize_app(cred, {'storageBucket': 'misterrubato-test.appspot.com', 
                          'databaseURL': databaseURL})
        
    # initialize mediapipe
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.3)
    mpDraw = mp.solutions.drawing_utils

    # Load the gesture recognizer model
    model = load_model('c:/devinpiano/music/analyze/mp_hand_gesture')

    # Load class names
    #f = open('./mp_hand_gesture/gesture.names', 'r')
    #classNames = f.read().split('\n')
    #f.close()
    #print(classNames)

    midilink = midilink.replace("\r", "")
    midiname = os.path.basename(midilink)
    midiname = os.path.splitext(midiname)[0]
    midiname = midiname.replace('%20', ' ')
    filename = midiname + '.fgt'

    toignore = 540 #dependent on mkv or mp4
    #cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture("C:\\Users\\devin\\Videos\\2023-08-03 15-38-56.mkv")
    inputpath = 'C:\\Users\\devin\\Videos\\'
    sys.path.insert(0, 'C:\\Users\\devin\\Videos\\')
    #mkv saved locally already
    path = './output/'
    cap = cv2.VideoCapture(inputpath + midiname + ".mkv")
    if not cap.isOpened():
       #mp4 is default download format.  So have to download before this.  
       #in general output to this different folder just in case we overwrite something
       #at some point accidentally.  
       #record owns the local folder.  
       #analyze has ./output/
       cap = cv2.VideoCapture(inputpath + midiname + ".mp4")
       if not cap.isOpened() and localfile !="None":
           cap = cv2.VideoCapture(localfile)
    else:
        toignore = 720
    if not cap.isOpened():
        print("No video exists for " + midilink)
        print("Exiting fingertest")
        sys.exit(0)
        
    #dont redo this.  Live with the analysis of the time for now.  
    if (os.path.exists(os.path.join(path , filename))):
        print("Skipping " + filename)
        print("Already exists")
        sys.exit(0)

    #use the file from analyze.py
    #should change local name
#    midiname = midiname.replace('%20', ' ')
    if not (os.path.exists(inputpath + midiname + ".mid")):
        print("No file available" + midiname)
        sys.exit(0)
        
    print("Finger Analysis getting midi" + midiname)
    mid = MidiFile(inputpath + midiname + ".mid")
    #ok with this midi file
    #after use 
    t = analyze.enhanceMidi(mid)
    starttimes, endtimes = analyze.getTrackTimes(t)

#    img = analyze.midiToImage(t, midilink)
#    cv2.imshow("MIDI", img) 
    #uploadanalyze(filename, os.path.join(path, filename))
    
    
    cnt = 1.0
    fps = cap.get(cv2.CAP_PROP_FPS)
    ret, frame = cap.read()
    y, x, c = frame.shape

    landmarks = np.zeros((10,2)) #keep previous locations if no/low confidence?  
    framecheck = 1 #check each 10th frame.  Too slow for testing.  
    frameTime = 1.0/fps
    midiTime = 0.0
    prevTime = 0.0
    i = 0
    on = 0
    f = open(path + filename, "w")
    
    fingerhit = 0
    fingermiss = 0
    previteration = 0
    
    lag = 100
    prevnote = 21
    startnote = 0
    for mymsg in t.notes:
        # Read each frame from the webcam
        #which do we move forward, next note or next frame?  
        if (on > 0):
            midiTime += mymsg.msg.time
            #not very efficient, but good enough for now.  
            i = analyze.getIteration(midiTime, starttimes, endtimes)
            if (i == -1):
                printNote(mymsg, startnote, midiTime, frameTime, starttimes, endtimes)
            if (i != previteration):
                previteration = i
                print(str(i) + " fingertest completed ")
                print("hit " + str(fingerhit) + " miss " + str(fingermiss))
                fingerhit = 0
                fingermiss = 0

        if (mymsg.msg.type=='note_on'):
#            if (on > 0 and i > -1):  
#                mymsg.msg.time = midiTime
            #simple calculation here, could be a problem, but the first instance is off already, so not the only problem.  
            on = analyze.isOn(mymsg.note, on)
            if (mymsg.note == 21):
                startnote = mymsg.msg.time
            
        
        
        while float(midiTime+lag)/1000 > frameTime and on > 0 and i > -1:
#            cap.set(cv2.CAP_PROP_POS_FRAMES, cnt)
            ret, frame = cap.read()
    #        if (cnt % 30 != 0):
    #            cnt = cnt + 1
    #            break
            if not ret:
                print("Bad Frame" + str(cnt))
                cnt = cnt + framecheck
                break

            # Flip the frame vertically
        #    frame = cv2.flip(frame, 1)
            keys = frame[toignore:y, 0:x]
            tempy = y - toignore
            #keys = frames[780:x, 0:y] #for some reason the mkv resolution and mp4 downloaded resolution different.  
            #read midi and match the fingers with midi times.  
            #first get time of the frame.  #and get the assumed key/finger combination
            framergb = cv2.cvtColor(keys, cv2.COLOR_BGR2RGB)

            # Get hand landmark prediction
            result = hands.process(framergb)

            # print(result)
            
            className = ''

            # post process the result
            if result.multi_hand_landmarks:
    #            print(result.multi_handedness) #this doesnt seem to work very well.  
        #or maybe just need to swap right for left.  
                for hidx, handslms in enumerate(result.multi_hand_landmarks):
        #            print(handslms)
                    lbl = result.multi_handedness[hidx].classification[0].label
        #            print(lbl) #ok so it is switched
                    for idx, lm in enumerate(handslms.landmark):
        #                print(lm)
                            
                        myidx = getFingerNum(lbl, idx)
                        if (myidx > 0):
    #                        print(myidx, lm)
                            lmx = int(lm.x * x)
                            lmy = int(lm.y * tempy)
                            landmarks[myidx-1, 0] = lmx
                            landmarks[myidx-1, 1] = lmy

                    # Drawing landmarks on frames
                    mpDraw.draw_landmarks(keys, handslms, mpHands.HAND_CONNECTIONS)

                    # Predict gesture
        #            prediction = model.predict([landmarks])
                    # print(prediction)
        #            classID = np.argmax(prediction)
        #            className = classNames[classID]
        
                #OK we have the fingertips in order and the current time of the frame.  
                #now compare with midi and see what note pressed with what hand.  
                #create a new midi file with that data, or some other easy to use format.  
                #better if we can edit the existing midi file, but anyway.  
            # show the prediction on the frame
        #    cv2.putText(keys, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
        #                   1, (0,0,255), 2, cv2.LINE_AA)

            cnt = cnt + framecheck
            frameTime = cnt/fps
            
                
#            if (cnt%100==0):
        
#            print(frameTime)
#            showKeys(landmarks, x)
#            print(landmarks)
            # Show the final output
        #    keys = frame[780:x, 0:y]
        # Add a red point to the center of the frame
            tempx = getNoteCoord(mymsg, x)
            cv2.circle(keys, (int(tempx), 100), 5, (0, 0, 255), -1)       
            font = cv2.FONT_HERSHEY_SIMPLEX

            fontScale = 1
            color = (0, 0, 255)
            thickness = 2

            cv2.putText(keys, str(mymsg.note), (int(tempx)+10, 50), font, fontScale, color, thickness)
            cv2.putText(keys, str(frameTime), (10, 50), font, fontScale, color, thickness)
            cv2.imshow("Output", keys) 

            if cv2.waitKey(1) == ord('q'):
                break


        if (prevnote in [21,22,105,106,107,108] or mymsg.note in [21,22,105,106,107,108] ):
            printNote(mymsg, startnote, midiTime, frameTime, starttimes, endtimes)
        prevnote = mymsg.note
        
        finger = getFinger(mymsg, landmarks, x)
        if (finger > 0):
            fingerhit += 1
        else:
            fingermiss += 1
       # print(str(midiTime) + ' ' + str(mymsg.note) + ' ' + str(finger))
        f.write(str(midiTime) + ' ' + str(mymsg.note) + ' ' + str(finger) + '\n')
        
    # release the webcam and destroy all active windows
    f.close()
    print("fingertest completed")
    print("hit " + str(fingerhit) + " miss " + str(fingermiss))
    
    showKeys(landmarks, x)
    
    cap.release()

    cv2.destroyAllWindows()

