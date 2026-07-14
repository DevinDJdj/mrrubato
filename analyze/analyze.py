#get videos and create a DB of Data about all played.  
#link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
#for now just generate a csv file.  
#dont download the videos, just get the written description
#    subprocess.call('python ./analyze/analyze.py --title "' + args.title + '"')


#notesplayed


import sys

import datetime
import traceback
from unittest import case
# adding Folder_2/subfolder to the system path
#not great mechanism for config.  Maybe just make absolute path?
sys.path.insert(0, 'c:/devinpiano/')
sys.path.insert(1, 'c:/devinpiano/music')
#sys.path.append('../')
import config  

import os
#import cred
import pandas as pd
import requests
import json
from oauth2client.tools import argparser, run_flow

from mido import MidiFile
from mido import Message
import math

#generate image from midi
#import cv2
import numpy as np
#print(cred.APIKEY)

#try to use pytorch a bit
#pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

import torch
import torch.nn.functional as F
from torch import nn, optim
from torch.autograd import Variable

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import firebase_admin
from firebase_admin import credentials, initialize_app, storage, firestore, db
# Init firebase with your credentials
from collections import Counter
import webbrowser

#from subprocess import Popen
import subprocess

CONTEXT_SIZE = 2
EMBEDDING_DIM = 10

import mymidi

#> pip install qrcode
import qrcode

from PIL import Image, ImageDraw


itoffset = 0
mappgram = {} #map [ SIGNGRAM ] [PGRAM]
mapsgram = {} #map [seqngram][pgram]

gstarttimes = []
gendtimes = []
#cred.CHANNELID
channel_id = config.cfg["youtube"]["CHANNELID"] 
#cred.APIKEY
api_key = config.cfg["youtube"]["APIKEY"] 
def get_channel_stat() -> dict:
    url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}'

    r = requests.get(url)
    data = r.json()
    return data['items'][0]['statistics']
    

def get_pl_data_per_page(npt: str=None, limit: int=None) -> dict:

    url = f"https://www.googleapis.com/youtube/v3/playlists?key={api_key}&channelId={channel_id}&part=snippet,id&order=date"
    if limit is not None:
        url = f"{url}&maxResults={limit}"
    if npt is not None:
        url = f"{url}&&pageToken={npt}"

    r = requests.get(url)
    return r.json()
    
    

def get_playlists_data(limit: int=50):
    res = []
    nextPageToken = None
    while True:
        data = get_pl_data_per_page(nextPageToken)
        nextPageToken = data.get("nextPageToken", None)
        res.append(data)
        
        if nextPageToken is None: break
    return res




def get_pl_items_per_page(plid, npt: str=None, limit: int=None) -> dict:

    url = f"https://www.googleapis.com/youtube/v3/playlistItems?key={api_key}&playlistId={plid}&part=snippet,contentDetails&order=date"
    if limit is not None:
        url = f"{url}&maxResults={limit}"
    if npt is not None:
        url = f"{url}&&pageToken={npt}"

    r = requests.get(url)
    return r.json()
    
    
def search(title, limit: int=50) -> dict:
    #no longer using youtube internal DB, use our DB.  
    
    ref = db.reference(f'/misterrubato')
    snapshot = ref.order_by_child('snippet/title').equal_to(title).get()

    return snapshot.items()

#    channelId = "UC4dK3RpqBq2JpIkRmQn6HOA"

#    url = f"https://www.googleapis.com/youtube/v3/search?maxResults={limit}&channelId={channelId}&order=date&q={title}&key={api_key}&part=snippet"
#    r = requests.get(url)
#    return r.json()

def get_playlist_items(plid, limit: int=50):
    res = []
    nextPageToken = None
    while True:
        data = get_pl_items_per_page(plid, nextPageToken, limit)
        nextPageToken = data.get("nextPageToken", None)
        res.append(data)
        
        if nextPageToken is None: break
    return res

    
def outputMidi(mid):
    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        for msg in track:
            print(msg)


def isOn(note, on):
    if (note == 21):
        on = 1
    if (note == 22):
        on = 0
    if (note == 107):
        on = 0
    if (note == 108):
        on = 1
    return on


#we need to adjust to several images one per instance.  
#if prevMsg = 21 or 108 then this is start time.  
#if nextMsg = 22 or 107 then this is end time of the track.  

def getTrackTimesControl(mytrack):
    #skip between pauses and only start with the start signal.  
    currentTime = 0
    on = 0
    starttimes = []
    endtimes = []
    for mymsg in mytrack.notes:        
    #getting duplicates with multiple channels.  
        if hasattr(mymsg.msg, 'time'):
            currentTime += mymsg.msg.time
        if (mymsg.msg.type == 'note_on' and hasattr(mymsg.msg, 'velocity') and mymsg.msg.velocity > 0 and mymsg.msg.channel==0):
            if (mymsg.msg.note == 21 or mymsg.prevmsg.note == 108) and mymsg.msg.channel == 0:
                print(mymsg.msg)
                starttimes.append(currentTime)
            if mymsg is not None and (mymsg.note == 22 or mymsg.note == 107) and mymsg.msg.channel == 0:
                print(mymsg.msg)
                endtimes.append(currentTime)
                

#    mymsg.simpleprint()
#    mymsg.prevmsg.simpleprint()
    return starttimes, endtimes

def getTrackTimes(mytrack):
    #skip between pauses and only start with the start signal.  
    currentTime = 0
    on = 0
    starttimes = []
    endtimes = []
    for mymsg in mytrack.notes:        
    #getting duplicates with multiple channels.  
        if on > 0 and hasattr(mymsg.msg, 'time'):
            currentTime += mymsg.msg.time
        if (mymsg.msg.type == 'note_on' and mymsg.msg.channel==0):
            if mymsg.prevmsg is not None and (mymsg.prevmsg.note == 21 or mymsg.prevmsg.note == 108) and mymsg.msg.channel == 0:
                starttimes.append(currentTime)
            if mymsg is not None and (mymsg.note == 22 or mymsg.note == 107) and mymsg.msg.channel == 0:
                endtimes.append(currentTime)
        if (mymsg.msg.type == 'note_on' and mymsg.msg.channel==0):
            on = isOn(mymsg.msg.note, on)
                

#    mymsg.simpleprint()
#    mymsg.prevmsg.simpleprint()
    return starttimes, endtimes

def getTrackTime(track):
    #skip between pauses and only start with the start signal.  
    currentTime = 0
    on = 0
    for msg in track:        
        if on > 0 and hasattr(msg, 'time'):
            currentTime += msg.time
        if (msg.type == 'note_on'):
            on = isOn(msg.note, on)

    return currentTime

def getColor(timepassed, initialvelocity, pedal):
    #maybe look up the actual function here, just a placeholder function of time vs
    #also we really probably want to show this even when velocity is 0
    if (pedal > 0 or timepassed == 0):
        estimate = (initialvelocity**2/(math.log(timepassed+2)))
        if (estimate > initialvelocity):
            estimate = initialvelocity
        return int(estimate)
    else:
        return 0
    
def fillImage(midi_image, notes, currentTime, prevTime, pedal, iteration, starttime):
    #between prevTime and currentTime fill the image    
    a = prevTime
    while (a <= currentTime):
        for n in notes:
            if n.time <= a and n.velocity > 0:
                c = getColor(a - n.time, n.velocity, pedal)
                #note is on
                if (c > 0):
                    midi_image[iteration*88*2+(108-n.note)*2:iteration*88*2+(108-n.note)*2+1,int((a-starttime)/100)] = (0,n.velocity+c,n.velocity*2-c)      # (B, G, R)
        a += 100

def getIteration(currentTime, starttimes, endtimes):
    i = 0
    for i, st in enumerate(starttimes):
        if (i < len(endtimes) and starttimes[i] <= currentTime and currentTime <= endtimes[i]):
            return i
    for i, st in enumerate(starttimes):
        #catch the case where we are between iterations, this is important for the image generation.
        if (currentTime < starttimes[i]):
            return -i-1 #-1 for 0 index, -2 for 1 index, etc.
    print("getIterationError" + str(currentTime))
    print(starttimes)
    print(endtimes)

    return -1
    

def getRelativeTime(it, currentTime, starttimes, endtimes):
    if it < 0:
        return -1
    reltime = 0
    reltime = currentTime - starttimes[it]
    if reltime < 0:
        reltime = 0
    div = (endtimes[it] - starttimes[it])
    if div <= 0:
        return -1
    reltime /= div
    return reltime

def midiToImage(t, midilink, starttimes, endtimes):
    
    print('Track: {}'.format(t.track.name))
    notes = [Message('note_on', channel=0, note=60, velocity=0, time=0)] * 109
    pedal = 0
    height = 88*2
    iwidth = 1
    print(starttimes)
    print(endtimes)
    midi_image = None
    if len(starttimes) != len(endtimes) or len(starttimes) < 1:
        print("Incorrect data, please fix" + midilink)
    else:    
        for i, st in enumerate(starttimes):
            w = int((endtimes[i]-starttimes[i])/100)
            print(w)
            if w > iwidth:
                iwidth = w +1
        height = (i+1)*88*2
        if (iwidth > 40000):
            print("Width too large, skipping " + midilink)
            return None
        midi_image = np.ones((height,iwidth,3), np.uint8)
        midi_image = 255*midi_image
        currentTime = 0
        prevTime = currentTime
        i = 0
        on = 0
        for mymsg in t.notes:
            if (on > 0):
                #only do this once.  
                currentTime += mymsg.msg.time
                #not very efficient, but good enough for now.  
                i = getIteration(currentTime, starttimes, endtimes)
                if (i == -1):
                    print("!!--midiToImage " + str(currentTime) + "\n-$$" + str(starttimes) + "\n-$$" + str(endtimes))
            if (mymsg.msg.type=='note_on'):
                if (on > 0 and i > -1):  
                    mymsg.msg.time = currentTime
                    notes[mymsg.note] = mymsg.msg
                    fillImage(midi_image, notes, currentTime, prevTime, mymsg.pedal, i, starttimes[i])
                    prevTime = currentTime
                on = isOn(mymsg.note, on)
                
#            print(mymsg.msg)
    print(t.length)
    print(starttimes)
    print(endtimes)
    
    return midi_image


def ngramToImage(t, midilink, starttimes, endtimes):
    
    print('Track: {}'.format(t.track.name))
    notes = [Message('note_on', channel=0, note=60, velocity=0, time=0)] * 109
    pedal = 0
    height = 88*2
    iwidth = 1
    #calling this twice is a problem,
#    starttimes, endtimes = getTrackTimes(t)
    print(starttimes)
    print(endtimes)
    midi_image = None
    if len(starttimes) != len(endtimes) or len(starttimes) < 1:
        print("Incorrect data, please fix" + midilink)
    else:    
        for i, st in enumerate(starttimes):
            w = int((endtimes[i]-starttimes[i])/100)
            print(w)
            if w > iwidth:
                iwidth = w +1
        height = (i+1)*88*2
        if (iwidth > 40000):
            print("Width too large, skipping " + midilink)
            return None
        midi_image = np.ones((height,iwidth,3), np.uint8)
        midi_image = 255*midi_image
        currentTime = 0
        prevTime = currentTime
        i = 0
        on = 0
        #logic here to analyze ngrams.  

        for mymsg in t.notes:
            if (on > 0):
                #this is already set.  just get value.  
                currentTime = mymsg.msg.time
                #not very efficient, but good enough for now.  
                i = getIteration(currentTime, starttimes, endtimes)
                if (i == -1):
                    print("!!--ngramToImage " + str(currentTime) + "\n-$$" + str(starttimes) + "\n-$$" + str(endtimes))

            if (mymsg.msg.type=='note_on'):
                if (on > 0 and i > -1):  
#                    mymsg.msg.time = currentTime
                    notes[mymsg.note] = mymsg.msg

                    """wrds = mymsg.getWords()
                    #print(wrds)
                    pgram = mymsg.getPGram(wrds)
                    seqgram = mymsg.getSeqNGram(wrds)
                    signs = mymsg.getSigns() 
                    
                    mappgram[ signs ] [ pgram ]
                        
                    it = getIteration(currentTime, starttimes, endtimes)
                    reltime = getRelativeTime(it, currentTime, starttimes, endtimes)

                    #get relative time within this word and iteration.  
                    mappgram[ signs ] [ pgram ]['time'].sort()                                       
                    mappgram[ signs ] [ pgram ]['iteration'].sort()  
                    #count per iteration
                    it_counts = Counter(mappgram[ signs ] [ pgram ]['iteration'])     
                    #use prevmsg N times to get previous pgram/seqgram

                    mapsgram[ seqgram ] [ pgram ]['time'].sort()
                    mapsgram[ seqgram ] [ pgram ]['iteration'].sort()                    
                    #count per iteration
                    it_counts = Counter(mapsgram[ seqgram ] [ pgram ]['iteration'])
                    """


                    fillImage(midi_image, notes, currentTime, prevTime, mymsg.pedal, i, starttimes[i])
                    prevTime = currentTime
                on = isOn(mymsg.note, on)
                
#            print(mymsg.msg)
    print(t.length)
    print(starttimes)
    print(endtimes)
    
    return midi_image




def isInputMessage(msg):
  if (hasattr(msg, 'channel') and msg.channel < 3):
    return True
  else:
    return False

#continue here.  Need to further this.      
#from this I think we can generate N-grams of notes.  
#for now not focused on rhythm.  #lets just give the notes weights based on their msg.velocity
#not sure this strategy is good.  But we want to create N-grams and check the uniqueness vs. repitition at certain note intervals.  
#create some plots based on Notes, organize by octaves
#for now just do a simple note frequency and by velocity.  
#then try to find time patterns within these note patterns.  
#if there is significant repetition in any set of notes then we want to try to analyze this.  
#what is the rhythm of these repititions, is there one set, or multiple sets.  
#if the same note pattern is offset by X steps.  
#just add each N-gram to the MyMsg in the form
#this should be a function to iterate?  
#for now this is easier, but I think I need
#[MAXNGRAM][MAXNGRAM] array already built.  
#use some of the structures we have used before, just the P*P*P for now to define the note sequence.  Right now order not so important.  
#each P represents a key.  

def getControl(mid):
    prevMsg = None
    pedal = 0
    maxtime = 0
    
    print("Get Control Midi start")
    for i, track in enumerate(mid.tracks):
        print("Track number " + str(i))
        if i==0: #for now just using 1 track.  
            totalTime = getTrackTime(track)
            t = mymidi.MyTrack(track, totalTime, maxtime)
            on = 0
            othertime = 0
            for msg in track:
              #ignore feedback channels.  
              if isInputMessage(msg):
                if (msg.type=='note_on' or msg.type=='control_change' or msg.type=='program_change'):
                    if (on == 0 
                        or (msg.type=='control_change' and msg.control != 64) #control changes without pedal
                        or (msg.type == 'program_change') #all instrument changes
                        or (hasattr(msg, 'note') and msg.note in [21,22,105,106,107,108])):   #just get notes from between iterations..
                        m = mymidi.MyMsg(msg, prevMsg, pedal)
                        m.time += othertime
                        m.msg.time += othertime #keep real time here when we are skipping notes..
                        othertime = 0
                        t.notes.append(m)
                        if (m.prevmsg is not None):
                            m.prevmsg.nextmsg = m
                            if (maxtime < msg.time):
                                maxtime = msg.time
                        prevMsg = m
                    elif hasattr(msg, 'time'):
                        othertime += msg.time
                    if (hasattr(msg, 'note')):
                        on = isOn(msg.note, on)
                elif hasattr(msg, 'time'):
                    othertime += msg.time
                if (msg.type=='control_change'):
                    #https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2
                    if (msg.control == 64):  #assuming this is pedal, yep 
                        pedal = msg.value
               # print(msg)
    t.maxtime = maxtime                    
    return t
    
def enhanceMidi(mid):
    
    prevMsg = None
    pedal = 0
    maxtime = 0
    
    print("Enhance Midi start")
    for i, track in enumerate(mid.tracks):
        print("Track number " + str(i))
        if i==0: #for now just using 1 track.  
            totalTime = getTrackTime(track)
            t = mymidi.MyTrack(track, totalTime, maxtime)
            on = 0
            othertime = 0
            for msg in track:
              #ignore feedback channels.  
              if isInputMessage(msg):
                if (msg.type=='note_on'):
                    if (on > 0):  
                        m = mymidi.MyMsg(msg, prevMsg, pedal)
                        m.msg.time += othertime #why am I using msg.time here, probably screwing up the time..
                        m.time += othertime
                        #can we switch to m.time
                        othertime = 0
                        t.notes.append(m)
                        if (m.prevmsg is not None):
                            m.prevmsg.nextmsg = m
                            if (maxtime < msg.time):
                                maxtime = msg.time
                        prevMsg = m
                    on = isOn(msg.note, on)
                elif on > 0 and hasattr(msg, 'time'):
                    othertime += msg.time
                if (msg.type=='control_change'):
                    #https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2
                    if (msg.control == 64):  #assuming this is pedal, yep 
                        pedal = msg.value
               # print(msg)
    t.maxtime = maxtime                    
    return t

def getNoteQuant(notetime, maxtime=1000, maxquant=63):
    q = float(notetime)/float(maxtime)
    q *= maxquant
    if (q > maxquant):
        q = maxquant
    return int(q)
    
def printNgrams(t, title, GroupName, videoid, midilink):
    it = -1
    on = 0
    currentTime = 0
    prevTime = currentTime
    starttimes, endtimes = getTrackTimes(t)
    if (len(endtimes) > len(starttimes)):
        del endtimes[len(starttimes):]
    if (len(starttimes) != len(endtimes)) or len(starttimes) < 1:
        print("Incorrect data, please fix")
        print(starttimes)
        print(endtimes)
        return None, None
        
    else:    
        counter = 0
        for mymsg in t.notes:
            if (on > 0):
                currentTime += mymsg.msg.time
                counter += 1
                #not very efficient, but good enough for now.  
                it = getIteration(currentTime, starttimes, endtimes)
                if (i == -1):                    
                    print("!!--printNgrams " + str(currentTime) + "\n-$$" + str(starttimes) + "\n-$$" + str(endtimes))
                    traceback.print_exc()


                i = 0
                #too much printing.  
#                mymsg.print(it, title, GroupName, videoid, midilink)
                #for now return the random note based on probability distribution from this array
            if (mymsg.msg.type=='note_on'):
                if (on > 0 and it > -1):  
                    prevTime = currentTime
                on = isOn(mymsg.note, on)
                
    #this should have something
    print(mappgram)

def analyzeNgrams():
    #use mappgram and mapsgram to analyze patterns.
    global itoffset
    totalngrams = 0
    matches = 0
    nonmatches = 0
    for sign in mappgram:
        for pgram in mappgram[sign]:
            totalngrams += 1
            times = mappgram[ sign ] [ pgram ]['time']
            iterations = mappgram[ sign ] [ pgram ]['iteration']
            msgs = mappgram[ sign ] [ pgram ]['msgs']
            if (len(times) > 2):
#                print(f"Sign: {sign} Pgram: {pgram} Times: {times} Iterations: {iterations}")    
                #find match in relative time.  
                for t in range(1, len(times)):
                    dt = abs(times[t] - times[t-1])
                    if (dt < 0.05):
#                        print(f" MATCH: {iterations[t]} {iterations[t-1]} DT: {dt} ")
#                        print(f" {print(msgs[t-1].msg)} ")
                        matches += 1
                    else:
                        nonmatches += 1
    print(f"Iterations: {itoffset} Total Ngrams: {totalngrams} DT Matches: {matches} Others: {nonmatches}")



def lcs(X, Y): 
    #longest common subsequence, not necessarily contiguous, but in order.
    # find the length of the strings 
    m = len(X) 
    n = len(Y) 

    # declaring the array for storing the dp values 
    L = [[None]*(n + 1) for i in range(m + 1)] 

    """Following steps build L[m + 1][n + 1] in bottom up fashion 
    Note: L[i][j] contains length of LCS of X[0..i-1] 
    and Y[0..j-1]"""
    for i in range(m + 1): 
        for j in range(n + 1): 
            if i == 0 or j == 0 : 
                L[i][j] = 0
            elif X[i-1] == Y[j-1]: 
                L[i][j] = L[i-1][j-1]+1
            else: 
                L[i][j] = max(L[i-1][j], L[i][j-1]) 

    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1] 
    return L[m][n] 
# end of function lcs 

def getLCSMatrix(alliterations):

    #get the LCS matrix for this track.  
    matrix = np.zeros((len(alliterations), len(alliterations)), dtype=int)
    for i in range(len(alliterations)):
        for j in range(i+1, len(alliterations)):
            X = alliterations[i]
            Y = alliterations[j]
            m = len(X)
            n = len(Y)
            lcs_length = lcs(X, Y)
            print(f"LCS {i} and {j}: {lcs_length} // {m} and {n} ")
            print(f"{i} {j}: {lcs_length/(min(m,n)+1)}")
            matrix[i][j] = lcs_length
            matrix[j][i] = lcs_length

    #get rid of the diagonal for better visualization.  
#    for i in range(len(alliterations)):
#        matrix[i][i] = 0
    return matrix

def getNgrams(t):
    global itoffset
    it = -1
    on = 0
    currentTime = 0
    prevTime = currentTime
    starttimes, endtimes = getTrackTimes(t)
    if (len(endtimes) > len(starttimes)):
        del endtimes[len(starttimes):]
    if (len(starttimes) != len(endtimes)) or len(starttimes) < 1:
        print("Incorrect data, please fix")
        print(starttimes)
        print(endtimes)
        return None, None
    
    else:    
        notearray = np.zeros(len(t.notes), dtype=int)
        
        alliterations = [[] for i in range(len(starttimes))] #array of arrays of notes for each iteration.

        #create array of [iterations (10)][notes (88)][prevnote (88)]
        data = np.zeros((20, 88, 88), dtype=int)
        rythmdata = np.zeros((20, 64, 64), dtype=int)
        #create an array of [iterations (10][notes (88)][
        #only sum across [notes]
        
        #then create a plot of each 
        #calculated volume of each note like we have for the piano roll.  
        #then create histogram of this.  
        counter = 0
        maxit = -1
        for mymsg in t.notes:
            if (on > 0):
                currentTime += mymsg.msg.time
                notearray[counter] = mymsg.msg.note
                counter += 1
                #not very efficient, but good enough for now.  
                it = getIteration(currentTime, starttimes, endtimes)
                alliterations[it].append(mymsg.msg.note) #only note sequence info for now..

                i = 0
                tempmsg = mymsg
                while (i < mymidi.MAXNGRAM and tempmsg.nextmsg is not None):
                    tempmsg = tempmsg.nextmsg
                    mymsg.fngrams[i] = tempmsg.note
                    i = i+1

                i = 0
                tempmsg = mymsg
                while (i < mymidi.MAXNGRAM and tempmsg.prevmsg is not None):
                    tempmsg = tempmsg.prevmsg
                    i = i+1
                    mymsg.ngrams[mymidi.MAXNGRAM-i] = tempmsg.note
                mymsg.startmsg = tempmsg
                mymsg.currentTime = currentTime
                mymsg.ngramstensor = torch.tensor(mymsg.ngrams)
                #use this tensor for prediction
                #for now fill the array to do some statistics.  
                data[it][mymsg.prevmsg.msg.note-21][mymsg.msg.note-21] += 1
                
                #cant use t.maxtime here because of some issue probably with pauses etc.  
                #for now 2 seconds is max time
                rythmdata[it][getNoteQuant(mymsg.prevmsg.msg.time)][getNoteQuant(mymsg.msg.time)] += 1
                

                #for now return the random note based on probability distribution from this array
                wrds = mymsg.getWords()
                #print(wrds)
                pgram = mymsg.getPGram(wrds)
                seqgram = mymsg.getSeqNGram(wrds)
                signs = mymsg.getSigns() 
                
                #here can use seqgram as well.  
                #try to find the patterns.  
                #what sequences are the same, probably find more about playing quality than anything intrinsic to the piece.  
                if signs not in mappgram:
                    mappgram[signs] = {}
                if pgram not in mappgram[signs]:
                    mappgram[ signs ] [ pgram ] = { 'time': [], 'iteration': [], 'msgs': [] }
                    
                it = getIteration(currentTime, starttimes, endtimes)
                reltime = getRelativeTime(it, currentTime, starttimes, endtimes)
                mappgram[ signs ] [ pgram ]['time'].append( reltime)
                mappgram[ signs ] [ pgram ]['iteration'].append(it+itoffset)
                mappgram[ signs ] [ pgram ]['msgs'].append(mymsg)
                if (it> maxit):
                    maxit = it
                
                
                if seqgram not in mapsgram:
                    mapsgram[seqgram] = {}
                if pgram not in mapsgram[seqgram]:
                    mapsgram[ seqgram ] [ pgram ] = { 'time': [], 'iteration': [] }
                mapsgram[ seqgram ] [ pgram ]['time'].append(reltime)
                mapsgram[ seqgram ] [ pgram ]['iteration'].append(it+itoffset)

            if (mymsg.msg.type=='note_on'):
                if (on > 0 and it > -1):  
                    prevTime = currentTime
                on = isOn(mymsg.note, on)
        
        #increase itoffset for next time.
        itoffset += (maxit+1)


        return data, rythmdata, alliterations
        
def testNgramModel():

    # We will use Shakespeare Sonnet 2
    test_sentence = """When forty winters shall besiege thy brow,
    And dig deep trenches in thy beauty's field,
    Thy youth's proud livery so gazed on now,
    Will be a totter'd weed of small worth held:
    Then being asked, where all thy beauty lies,
    Where all the treasure of thy lusty days;
    To say, within thine own deep sunken eyes,
    Were an all-eating shame, and thriftless praise.
    How much more praise deserv'd thy beauty's use,
    If thou couldst answer 'This fair child of mine
    Shall sum my count, and make my old excuse,'
    Proving his beauty by succession thine!
    This were to be new made when thou art old,
    And see thy blood warm when thou feel'st it cold.""".split()

    trigram = [((test_sentence[i], test_sentence[i + 1]), test_sentence[i + 2])
               for i in range(len(test_sentence) - 2)]

    vocb = set(test_sentence)
    word_to_idx = {word: i for i, word in enumerate(vocb)}
    idx_to_word = {word_to_idx[word]: word for word in word_to_idx}



    ngrammodel = mymidi.NgramModel(len(word_to_idx), CONTEXT_SIZE, 100)
    criterion = nn.NLLLoss()
    optimizer = optim.SGD(ngrammodel.parameters(), lr=1e-3)

    for epoch in range(20):
        print('epoch: {}'.format(epoch + 1))
        print('*' * 10)
        running_loss = 0
        for data in trigram:
            word, label = data
            word = Variable(torch.LongTensor([word_to_idx[i] for i in word]))
            label = Variable(torch.LongTensor([word_to_idx[label]]))
            # forward
            out = ngrammodel(word)
            loss = criterion(out, label)
#            print(loss)
            running_loss += loss.item()
            # backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
#        print('Loss: {:.6f}'.format(running_loss / len(word_to_idx)))

    word, label = trigram[5]
    word = Variable(torch.LongTensor([word_to_idx[i] for i in word]))
    out = ngrammodel(word)
    _, predict_label = torch.max(out, 1)
    print(predict_label[0])
    predict_word = idx_to_word[predict_label[0].item()]
    print('real word is {}, predict word is {}'.format(label, predict_word))




def getNoteColor(note, velocity):
    match note % 12:
        case 0 | 1:
            color = (255, 0, 0)
        case 2 | 3:
            color = (255, 127, 0)
        case 4 | 5:
            color = (255, 255, 0)
        case 6 | 7:
            color = (0, 255, 0)
        case 8 | 9:
            color = (0, 0, 255)
        case 10 | 11:
            color = (75, 0, 130)
        case _:
            color = (0, 0, 0)
    return color

def getOctaveColor(note):
    octave = note // 12
    match octave:
        case 2:
            color = (255, 0, 0)
        case 3:
            color = (255, 127, 0)
        case 4:
            color = (255, 255, 0)
        case 5:
            color = (0, 255, 0)
        case 6:
            color = (0, 0, 255)
        case 7:
            color = (75, 0, 130)
        case 8:
            color = (148, 0, 211)
        case _:
            color = (0, 0, 0)
    
    return color

def findNote(fullseq, n=60): #find most recent note..
    for _, seq in enumerate(reversed(fullseq)):
        for _, note in enumerate(reversed(seq)):
            if note['&&'] == n:
                return note
    return None


def autocorrelation_envelopes(t, tlens, resolution=60):
    # 'resolution' defines how many array indices equal one tick
    envelopes = []
    st = gstarttimes
    et = gendtimes
    for i, len in enumerate(tlens):
        if len > 0:
            env = {'env': np.zeros(int((len+1) * resolution)), 'start': st[i], 'end': et[i], 'length': len, 'peaks': [], 'bpm': None}
            envelopes.append(env)

    
    for mymsg in t.notes:
        #no determination based on frequency of note..
        #simple example..
        i = getIteration(int(mymsg.msg.time), st, et)

        if (i == -1):
            print("!!--autocorrelation_envelope " + str(mymsg.msg.time) + "\n-$$" + str(st) + "\n-$$" + str(et))
            continue
        idx = int((mymsg.msg.time - st[i]) * resolution)
        if idx < tlens[i] * resolution:
            envelopes[i]['env'][idx] += mymsg.msg.velocity
            
    #for each envelope, detect_beat_and_tempo and print results.
    for i, env in enumerate(envelopes):
        bpm, peaks = detect_beat_and_tempo(env['env'], resolution)
        print(f"Iteration {i}: Detected BPM: {bpm}, Peaks: {peaks}")
        env['peaks'] = peaks
        env['bpm'] = bpm

    return envelopes

from scipy.signal import find_peaks

def detect_beat_and_tempo(onset_env, resolution=60, tempo_min=40, tempo_max=300):
    # Calculate autocorrelation resolution 60 means 60 samples per second, so each index in onset_env corresponds to 1/60th of a second.
    corr = np.correlate(onset_env, onset_env, mode='full')
    corr = corr[corr.size // 2:] # Keep only positive lags
    
    # Define search bounds based on expected BPM (tempo limits)
    # Convert BPM range into lags based on the resolution/tick rate
    min_lag = int((60 / tempo_max) * (resolution)) # 300 BPM corresponds to 0.2 seconds per beat, so min_lag is 0.2 * resolution
    max_lag = int((60 / tempo_min) * (resolution)) # 40 BPM corresponds to 1.5 seconds per beat, so max_lag is 1.5 * resolution
    
    # Find peaks in the valid lag range
    peaks, _ = find_peaks(corr, distance=min_lag, prominence=0.1)
    
    if len(peaks) == 0:
        return None, None
    
    # The first significant peak beyond the zero-lag represents the beat interval
    best_lag = peaks[0]
    
    # Calculate tempo (BPM)
    # (60 seconds per min * samples per second) / (samples per beat)
    # This calculation will vary based on your sampling units:
    bpm = 60 / (best_lag * resolution) 
    
    return bpm, peaks


def printMidiTicker(t, midilink):
    images = []
    images2 = []
    radius = 35
    gwidth = radius*3
    center = gwidth // 2
    color_1 = (255, 255, 255)
    color_2 = (0, 0, 0)

    print('MidiTicker: {}'.format(t.track.name))
    notes = [Message('note_on', channel=0, note=60, velocity=0, time=0)] * 109
    pedal = 0

    st = gstarttimes
    et = gendtimes
    print(st)
    print(et)
#    st, et = getTrackTimes(t)
    if len(st) != len(et) or len(st) < 1:
        print("Incorrect data, please fix" + midilink)
    else:    
        prevIt = 0
        currentTime = 0.0
        prevTime = currentTime
        i = 0
        on = 0
        prevmsg = None
        currentseq = []
        myseq = []
        currentcolor = (0, 0, 0)
        itlengths = [et[z]-st[z] for z in range(len(st))]
        itlengths = [int(x/1000) for x in itlengths]
        print(itlengths)

        autocorrenvs = autocorrelation_envelopes(t, itlengths, resolution=10)

        for mymsg in t.notes:
            cstart = 0
            cend = 360
            if (on > 0):
                prevTime = currentTime #in milliseconds..
                currentTime = mymsg.msg.time
                puretime = currentTime // 1000
                #not very efficient, but good enough for now.  
                i = getIteration(int(currentTime), st, et)
                if (i == -1):
                    print("Error: currentTime " + str(currentTime) + " st: " + str(st) + " et: " + str(et))
                else:
                    if (i != prevIt):
                        prevIt = i                    
                        #new sequence..
                        myseq.append(currentseq)
                        currentseq = []
                    elif (currentTime // 1000 != prevTime // 1000): #per second separation for now.. not accounting for > 1 second pauses for now.  
                        for j in range(1, int(currentTime // 1000 - prevTime // 1000)+1):
                            #new sequence..
                            myseq.append(currentseq)
                            currentseq = []
                    currentseq.append({'..': float(currentTime) / 1000, '&&': mymsg.note, '$$': mymsg.msg.velocity, ':': i, 'dur': 0})




            if (mymsg.msg.type=='note_on' or mymsg.msg.type=='note_off'):
                if (on > 0 and i > -1):  
#                    mymsg.msg.time = currentTime
                    notes[mymsg.note] = mymsg.msg
                    #create image here for each note to start.  
                    if (mymsg.msg.type == 'note_off' or (mymsg.msg.type == 'note_on' and mymsg.msg.velocity == 0)):
                        #find current note.  
                        mynote = findNote(myseq, mymsg.note)
                        if mynote is not None:
                            mynote['dur'] = float(currentTime) / 1000 - mynote['..']
                            #print(f"Note {mymsg.note} at time {currentTime} duration {mynote['dur']} seconds")
                        else:
                            print("!!Error finding note " + str(mymsg.msg))




                on = isOn(mymsg.note, on)

        #reset for second image type..
        currentTime = 0
        prevTime = currentTime
        i = 0
        on = 0
        prevmsg = None
        currentcolor = (0, 0, 0)
        mainimgs = []
        for it in range(prevIt+1):
            itlength = itlengths[it]
            print(f"Creating image for iteration {it} with length {itlength} seconds")
            itimg = Image.new('RGB', (gwidth*20, gwidth * (1 + itlength//20)), color_1)
            mainimgs.append(itimg)

        loci = 0
        locj = 0
        prevIt = 0
        for k, seq in enumerate(myseq):
            #create image for sequence..
#            print(seq)
            im = Image.new('RGB', (gwidth, gwidth), color_1)
            draw = ImageDraw.Draw(im)
            cstart = 0
            cend = 360
            #draw outline for notes..
            draw.line((center-radius*1.3, center, center-radius*1.1, center), fill=(0, 0, 0), width=1)
            draw.line((center+radius*1.1, center, center+radius*1.3, center), fill=(0, 0, 0), width=1)
            draw.line((center, center-radius*1.3, center, center-radius*1.1), fill=(0, 0, 0), width=1)
            draw.line((center, center+radius*1.1, center, center+radius*1.3), fill=(0, 0, 0), width=1)
            draw.arc((center-radius, center-radius, center+radius, center+radius), start=cstart, end=cend, fill=(0,0,0), width=1)
            for m, note in enumerate(seq):
                prevTime = currentTime
                currentTime = note['..']
                dur = note['dur']
                if (dur == 0):
#                    print("!!No duration for note " + str(note) + " at time " + str(currentTime))
                    dur = 0.1 #just a placeholder for now, but this is an issue.

                puretime = currentTime // 1
                #not very efficient, but good enough for now.  
                i = note[':'] #iteration number

                if (i != prevIt):
                    prevIt = i                    
                    loci = 0
                    locj = 0

                if (currentTime - prevTime < 1):
                    cstart = (prevTime - puretime) * 360 - 90
                    cend = (currentTime - puretime) * 360 - 90
                else:
                    print("! " + str(currentTime) + " seconds" + str(prevTime) + " seconds")
                    cstart = (currentTime - puretime) * 360 - 100
                    cend = cstart + 10

                noteangle = (note['&&'] % 12) * 30
                timeangle = (note['..'] - puretime) * 360
                timeangle = round(timeangle)
                oct = note['&&'] // 12
                vol = note['$$'] // 30 #also width..
                vol = max(vol, 2)

                currentcolor = getOctaveColor(note['&&'])
                #draw.arc((center-radius, center-radius, center+radius, center+radius), start=cstart, end=cend, fill=currentcolor, width=vol)


                timepointx = round(center + radius * math.cos(math.radians(timeangle-90)))
                timepointy = round(center + radius * math.sin(math.radians(timeangle-90)))
                notepointx = round(center + radius * math.cos(math.radians(noteangle-90)))
                notepointy = round(center + radius * math.sin(math.radians(noteangle-90)))
                #adjust notepoints.  
                notepointx = round(15 + 15 * math.sin(math.radians(noteangle-90)))
                notepointy = round(15 + 15 * math.cos(math.radians(noteangle-90)))

                timenoteangle = math.atan2(notepointy - timepointy, notepointx - timepointx)

                width = round((currentTime-prevTime)*4)+1
                if (width > 5):
                    width = 5
                color_2 = getNoteColor(note['&&'], note['$$']) #not sure if we want octave color or note color here..

                centerx = (timepointx + notepointx) // 2
                centerx += center
                centerx /= 2
                centery = (timepointy + notepointy) // 2
                centery += center
                centery /= 2
                #draw.line((timepointx, timepointy, centerx, centery), fill=currentcolor, width=width)
                #draw.line((centerx, centery, notepointx, notepointy), fill=currentcolor, width=vol)
 #               if (m%2):
                tnx = round(center + (radius) * math.cos(math.radians(timeangle-90)))
                tny = round(center + (radius) * math.sin(math.radians(timeangle-90)))

                tnx2 = tnx + round(math.cos(math.radians(noteangle+15))*vol*8)
                tnx3 = tnx + round(math.cos(math.radians(noteangle-15))*vol*8)
                tny2 = tny + round(math.sin(math.radians(noteangle+15))*vol*8)
                tny3 = tny + round(math.sin(math.radians(noteangle-15))*vol*8)
 #               else:

#                tnx2 = tnx - round(math.cos(timenoteangle)*vol*2)
#                tny2 = tny - round(math.sin(timenoteangle)*vol*2)
#                draw.line((tnx2, tny2, tnx, tny), fill=currentcolor, width=1)
                draw.polygon([(tnx, tny), (tnx2, tny2), (tnx3, tny3)], fill=currentcolor, width=1, outline="black")

                cx = notepointx
                cy = notepointy
#                draw.ellipse((tnx, tny, tnx+7, tny+7), fill=color_2, width=1)
#                draw.ellipse((tnx, tny, tnx+vol, tny+vol), fill=currentcolor, width=1)
#                draw.pieslice((tnx, tny, tnx2, tny2), start=noteangle-105, end=noteangle-75, fill=currentcolor, width=1, outline="black")

#            print(mymsg.msg)

            if (i > -1 and i < len(st)):
                itlength = itlengths[i]
                mainimgs[i].paste(im, (loci, locj))
                loci += gwidth
                if (loci >= mainimgs[i].width):
                    loci = 0
                    locj += gwidth


    print(t.length)
    print(gstarttimes)
    print(gendtimes)

    return mainimgs

def printMidiGif(t, midilink):

    images = []
    prevIt = 0
    radius = 10
    gwidth = radius*10*3
    center = gwidth // 2
    color_1 = (255, 255, 255)
    color_2 = (0, 0, 0)

    print('Track: {}'.format(t.track.name))
    notes = [Message('note_on', channel=0, note=60, velocity=0, time=0)] * 109
    pedal = 0
    st, et = getTrackTimes(t)
    if len(st) != len(et) or len(st) < 1:
        print("Incorrect data, please fix" + midilink)
    else:    
        currentTime = 0
        prevTime = currentTime
        i = 0
        on = 0
        im = Image.new('RGB', (gwidth, gwidth), color_1)
        images.append(im)
        draw = ImageDraw.Draw(im)
        prevmsg = None
        for mymsg in t.notes:
            if (on > 0):
                currentTime += mymsg.msg.time
                #not very efficient, but good enough for now.  
                i = getIteration(currentTime, st, et)
                if (i != prevIt):
                    im = Image.new('RGB', (gwidth, gwidth), color_1)
                    images.append(im)
                    draw = ImageDraw.Draw(im)
                    prevIt = i

            if (mymsg.msg.type=='note_on'):
                if (on > 0 and i > -1):  
                    mymsg.msg.time = currentTime
                    notes[mymsg.note] = mymsg.msg
                    #create image here for each note to start.  
                    startangle = (mymsg.note % 12) * 30
                    oct = mymsg.note // 12
                    vol = mymsg.msg.velocity /10


                    if prevmsg is not None:
                        startangle1 = (prevmsg.note % 12) * 30
                        oct1 = prevmsg.note // 12
                        vol1 = prevmsg.msg.velocity /10
                        startpointx = round(center + radius*oct1 * math.cos(math.radians(startangle1)))
                        startpointy = round(center + radius*oct1 * math.sin(math.radians(startangle1)))
                        endpointx = startpointx + round(math.cos(math.radians(startangle1))*vol1)
                        endpointy = startpointy + round(math.sin(math.radians(startangle1))*vol1)
                        if (endpointx < startpointx):
                            temp = endpointx
                            endpointx = startpointx
                            startpointx = temp
                        if (endpointy < startpointy):
                            temp = endpointy
                            endpointy = startpointy
                            startpointy = temp

                        color_2 = (255 - round(abs(startangle1-startangle)/2), 0, 255 - round(abs(startangle1-startangle)/2))
#                        color_2 = (50, 50, 50)
 #                       draw.line((startpointx, startpointy, endpointx, endpointy), fill=color_2, width=round(vol/2))
                        draw.ellipse((startpointx, startpointy, endpointx+2, endpointy+2), fill=color_2, width=round(vol/2))
                    prevmsg = mymsg
                    prevTime = currentTime
                on = isOn(mymsg.note, on)
                
#            print(mymsg.msg)
    print(t.length)
    print(starttimes)
    print(endtimes)


#    mid = MidiFile(midifile)
    path = './output/'
    for i, im in enumerate(images):
        im.save(path + 'a' + str(i) + '.png',
                save_all=True, append_images=images[1:], optimize=False, duration=40, loop=0)
    

def printMidi(midilink, title, GroupName, videoid, force=False):
    path = './output/'
    midilink = midilink.replace("\r", "")
    midiname = os.path.basename(midilink)
    midiname = os.path.splitext(midiname)[0]
    filename = midiname + '.jpg'
    #dont redo this.  Live with the analysis of the time for now.  
    if (os.path.exists(os.path.join(path , filename)) and not force):
        print("Skipping " + midilink)
        return
    
    r = requests.get(midilink)
    print(len(r.content))
    midisize = len(r.content)
    if (len(r.content) < 200): #not sure why this is here.  Change 500->200
        print(r.content)
        return
    
    with open(path + midiname + ".mid", "wb") as f:
        f.write(r.content)
    mid = MidiFile(path + midiname + ".mid")

    #outputMidi(mid)    
    t = enhanceMidi(mid)    
    if (t is None):
        return

 #   printNgrams(t, title, GroupName, videoid, midilink)
    starttimes, endtimes = getTrackTimes(t)
    global gstarttimes, gendtimes
    gstarttimes = starttimes
    gendtimes = endtimes

    img = midiToImage(t, midilink, starttimes, endtimes)

#this is to only generate the midi data which has not been created yet.      
    if (img is not None):
        plt.imsave(os.path.join(path , filename), img)
#        cv2.imwrite(os.path.join(path , filename), img)
        uploadanalyze(filename, os.path.join(path, filename))

    #problem with calling getStartTimes multiple times..
#    printMidiGif(t, midilink)
    tickerimgs = printMidiTicker(t, midilink)
    if (tickerimgs is not None):
        path = './output/'
        for i, im in enumerate(tickerimgs):
            #1 second per frame..
            tickname = 'tick' + str(i) + '_' + midiname
            im.save(path + tickname + '.png')
            uploadanalyze(tickname + '.png', os.path.join(path, tickname + '.png'))


    data, rythmdata, alliterations = getNgrams(t)
    if (data is None):
        return

    lcsmatrix = getLCSMatrix(alliterations)


    nimg = ngramToImage(t, midilink, starttimes, endtimes)    
    if (nimg is not None):
        print("Saving ngram image")
        filename = 'ngram_' + midiname + '.png'
        plt.imsave(os.path.join(path , filename), nimg)
        uploadanalyze(filename, os.path.join(path, filename))
    else:
        print("No ngrams, skipping")
    #analyze mapngrams.  

    height = 200
    width = 200    

    
    #what is the note distribution for each and the interval distribution look like?  
    #show a distribution of previous->max
    temp = data.sum(axis=0) #combine all iterations
    temprythm = rythmdata.sum(axis=0)
    
    print(temp[36]) #probability of key after 36
    
    keystrokes = temp.sum(axis=0) #keystrokes for all keys
    rythms = temprythm.sum(axis=0)


    plt.matshow(lcsmatrix, cmap='gray_r') # Show the LCS matrix as a heatmap gray is closer correlation..
    plt.title("LCS Matrix Heatmap")
    filename = 'lcs_' + midiname + '.png'
    plt.savefig(os.path.join(path , filename))
    uploadanalyze(filename, os.path.join(path, filename))
    plt.figure().clear()

    #keys
    print(keystrokes) 
    plt.figure(0)
    _ = plt.hist(keystrokes, bins='auto')
    plt.title("Histogram with 'auto' bins")
    plt.xlim([5,1500])
    filename = 'ks_' + midiname + '.png'
    plt.savefig(os.path.join(path , filename))
    uploadanalyze(filename, os.path.join(path, filename))
    plt.figure(0).clear()
    
    #rythms
    print(rythms) 
    plt.figure(10)
    _ = plt.hist(rythms, bins='auto')
    plt.title("Rythm Histogram with 'auto' bins")
    plt.xlim([5,1500])
    filename = 'rs_' + midiname + '.png'
    plt.savefig(os.path.join(path , filename))
    uploadanalyze(filename, os.path.join(path, filename))
    plt.figure(10).clear()

    #keys
#    plt.show()
    keys = np.indices((len(keystrokes),))
    values = list(keystrokes)
    plt.figure(1)
    plt.bar(list(keys[0]), values)
    plt.xlim([0, 90])
#    plt.figure().set_figwidth(109)
#    plt.show()
    filename = 'ks2_' + midiname + '.png'
    plt.savefig(os.path.join(path , filename))
    uploadanalyze(filename, os.path.join(path, filename))
    plt.figure(1).clear()

    #rythms    
    rythmsa = np.indices((len(rythms),))
    values = list(rythms)
    plt.figure(11)
    plt.bar(list(rythmsa[0]), values)
    plt.xlim([0, 90])
#    plt.figure().set_figwidth(109)
#    plt.show()
    filename = 'rs2_' + midiname + '.png'
    plt.savefig(os.path.join(path , filename))
    uploadanalyze(filename, os.path.join(path, filename))
    plt.figure(11).clear()
    
    #ok enough for now.  
    #save this type of info to images and then use it in analyze.html to review.  
    #much more analytics needed here.  

    #note array    
    plt.figure(2)
    row_sums = temp.sum(axis=1)
    normalized_mat = temp / row_sums[:, np.newaxis]
    # Change major ticks to show every 20.
    ax = plt.figure(2).add_subplot(111)
    
    ax.xaxis.set_major_locator(ticker.MultipleLocator(12))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(12))
    ax.grid(which='major', color='#CCCCCC', linestyle='--')
    plt.imshow(normalized_mat,interpolation='none',cmap='binary')
    plt.colorbar()  
    filename = 'kk_' + midiname + '.png'
    plt.savefig(os.path.join(path, filename))
    uploadanalyze(filename, os.path.join(path, filename))
    plt.figure(2).clear()
    #lets get the correlation matrix.  
    #lets normalize this across row.  
    
    #rythm array
    plt.figure(12)
    row_sumsr = temprythm.sum(axis=1)
    normalized_mat = temprythm / row_sumsr[:, np.newaxis]
    # Change major ticks to show every 20.
    ax = plt.figure(12).add_subplot(111)
    
    ax.xaxis.set_major_locator(ticker.MultipleLocator(8))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(8))
    ax.grid(which='major', color='#CCCCCC', linestyle='--')
    plt.imshow(normalized_mat,interpolation='none',cmap='binary')
    plt.colorbar()  
    filename = 'rr_' + midiname + '.png'
    plt.savefig(os.path.join(path, filename))
    uploadanalyze(filename, os.path.join(path, filename))
    plt.figure(12).clear()

    
    return midisize #for now just return size of the midi.  
#    testNgramModel()
    #from here lets generate a graphic.  
    #read with mido?  

def printTranscript(transcriptlink):
    print(transcriptlink)
    if (transcriptlink == "erro"): #not sure why this is truncated.  
        return 0
    else:
        r = requests.get(transcriptlink)
        print(r.content)
        return len(r.content.split()) #wordcount
    
def uploadanalyze(file, fullpath):

    # Put your local file path 
    bucket = storage.bucket()
    blob = bucket.blob('analyze/' + file)
    blob.upload_from_filename(fullpath)

    # Opt : if you want to make public access from the URL
    blob.make_public()

    print("your analyze file url", blob.public_url)
    return blob.public_url


def getSecsFromTime(time):
    minsec = time.split(":")
    if (minsec == time):
        return 0
    return int(minsec[0])*60 + int(minsec[1])

def calctimes(starttimes, endtimes):
    #calculate from timestamps
    timewithoutplaying = 0
    timewithplaying = 0
    lasttime = 0
    for s, e in zip(starttimes, endtimes):
        timewithoutplaying += getSecsFromTime(s) - lasttime
        lasttime = getSecsFromTime(e)
        timewithplaying += lasttime - getSecsFromTime(s)
    return timewithplaying, timewithoutplaying
    
def updatestatsdb(videoid, starttimes, endtimes, midisize, numwords):
 
    timeplaying, timewithoutplaying = calctimes(starttimes, endtimes)
    #insert into DB
    ref = db.reference(f'/misterrubato/' + videoid + '/stats')
    #if this exists, return
    if ref.get() is not None:
        return
        
    #really this can all be set at play record.py as well, but this is essentially the same as we run this during record.py
    #need to test this works.  Seems to work ok.  
    data = {'timeplaying':timeplaying,'timewithoutplaying':timewithoutplaying, 'midisize':midisize, 'wordsrecognized':numwords}
    ref.set(data)

def getqrcode(prev):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(prev)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    #save as C:\Temp\prevIterationQR.jpg
    img.save("C:\\Temp\\prevIterationQR.jpg")


import asyncio

async def async_execute(cmd):
    # Start the process asynchronously
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    # Non-blocking read loop
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        print(f"Async Captured: {line.decode().strip()}")
        
        # You can perform other tasks right here
        await asyncio.sleep(0.1) 


if __name__ == '__main__':
    argparser.add_argument("--title", help="Video title", default="What a Wonderful World")
    argparser.add_argument("--video", help="Video ID", default="4flRJWtfY9c")
    #for now this is kind of getting annoying.  We can always calculate this later.  
    argparser.add_argument("--skipfinger", help="Skip finger test", default="true")
    argparser.add_argument("--skipmidscribe", help="Skip midscribe test", default="true")
    argparser.add_argument("--force", help="Force reanalyze", default="false")
    args = argparser.parse_args()


    title = args.title

    stats = get_channel_stat()
    print(pd.DataFrame([stats]))
    cwd = os.getcwd()
    print(cwd)
    
    cred = credentials.Certificate("c:\\devinpiano\\misterrubato-test.json")
    databaseURL = "https://misterrubato-test-default-rtdb.firebaseio.com/"
    initialize_app(cred, {'storageBucket': 'misterrubato-test.appspot.com', 
                          'databaseURL': databaseURL})


#    data = get_playlist_items(cred.MY_PLAYLIST)
    
#    dfvideos = pd.DataFrame(data)
    #so getting unlisted videos is annoying, perhaps I should just create a DB and hold the ID and title for search purposes.  
    #yeah I think having an ID for each video probably is best.  Do this in record.py
    

    data = search(title)
    print(data)

    iterations = []    
    totalidx = 0
    latestvideo = None
    latestvideoitem = None
    latestvideoDate = None
    latestmidilink = None

    sorted_data_items = sorted(data, key=lambda item: item[1]['snippet']['publishedAt'])
    print(sorted_data_items)

    for key, item in sorted_data_items:
#    for item in reversed(data["items"]):
#    for item in data['items']:
#        print(item["id"])
#        print(item)
        if (item["kind"] == "youtube#video"):
            videoid = item["id"]
#            url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,status\
#                &id={videoid}&key={api_key}'
#            json_url = requests.get(url)
#            datav = json.loads(json_url.text)
#            if (len(datav['items']) > 0):
            numwords = 0
            midisize = 0
            totalduration = item['contentDetails']['duration']
            GroupName = ""
            publishedDate = item['snippet']['publishedAt']
            date = datetime.datetime.strptime(publishedDate, '%Y-%m-%dT%H:%M:%SZ')
            if (latestvideo is None or date > latestvideoDate):
                latestvideo = videoid
                latestvideoDate = date
                print(date)
            title = item['snippet']['title']
            privacystatus = item['status']['privacyStatus']
            gs = title.find("(")
            ge = title.find(")")
            url = "https://www.youtube.com/watch?v=" + videoid
            
            if (gs > 0):
                GroupName = title[gs+1:ge]
                title = title[0:gs]

            desc = item['snippet']['description']
            starttimes = []
            endtimes = []
            for i in range(1,9):
                ts = desc.find("TRIAL#{} (".format(i))
                te = desc.find(")", ts)
                if (ts > -1):
                    starttimes.append(desc[ts+9:te])

            for i in range(1,9):
                ts = desc.find("END#{} (".format(i))
                te = desc.find(")", ts)
                if (ts > -1):
                    endtimes.append(desc[ts+7:te])

            midis = desc.find("MIDI:")
            if (midis > 0):
                midie = desc.find("\n", midis)
                midilink = desc[midis+5:midie]
                midisize = printMidi(midilink, title, GroupName, videoid, args.force=="true")
                if (videoid==latestvideo):
                    latestmidilink = midilink
                    latestvideoitem = item
#                    print(latestvideoitem)
                    
                fingers = desc.find("FINGERS:")
                if (fingers > 0):
                    print("already has fingers")
                else:
                    #just update DB for now.  Then timestep.py will update Youtube info
                    if (args.skipfinger !="true"):
                        
                        #doesnt work for videoid starting with -
                        cmd = ["python", "./analyze/fingertest.py", "--video", "\"" + videoid + "\"", "--midi", midilink, "--force", args.force]
                        print(cmd)
                        asyncio.run(async_execute(cmd)) #run and capture output asynchronously so we can see it in real time.
    #                    proc = subprocess.Popen(cmd)
                        print("fingertest started")
                if (args.skipmidscribe != "true"):
                    #run midscribe test here as well.  
                    cmd = ["python", "./analyze/midscribe.py", "--video", "\"" + videoid + "\"", "--midi", midilink, "--force", args.force]
                    print(cmd)
                    asyncio.run(async_execute(cmd)) #run and capture output asynchronously so we can see it in real time.
#                    proc = subprocess.Popen(cmd)
                    print("midscribe started")
            
            transcripts = desc.find("TRANSCRIPT:")
            if (transcripts > 0):
                transcripte = desc.find("\n", transcripts)
                transcriptlink = desc[transcripts+11:transcripte]
                numwords = printTranscript(transcriptlink)

            if (len(starttimes) != len(endtimes)):
                print("invalid data {videoid}")
            else:
                print(starttimes)
                updatestatsdb(videoid, starttimes, endtimes, midisize, numwords)
                for idx,t in enumerate(starttimes):
                    totalidx +=1
                    mydata = {"URL": url, "PublishedDate": publishedDate, "starttime": starttimes[idx], "endtime": endtimes[idx], "iteration": totalidx}
#                        print(mydata)
                    iterations.append(mydata)
    

    #further analysis after mappgram and mapsgram built.  
    analyzeNgrams()

    #this is same check as latestmidilink
    if (latestvideoitem is not None):
        getqrcode(latestvideo)
        #open misterrubato.com/analyze.html?video=
        #autoraise=False, sick of waiting for this analyze.py to finish.  
        webbrowser.open('https://www.misterrubato.com/analyze.html?video=' + latestvideo, autoraise=False)
        item = latestvideoitem
        #here we should copy the existing video if it exists to previousIteration
        midilink = latestmidilink.replace("\r", "")
        midiname = os.path.basename(midilink)
        midiname = os.path.splitext(midiname)[0]
        midiname = midiname.replace('%20', ' ')
        inputpath = 'C:\\Users\\devin\\Videos\\'
        sys.path.insert(0, 'C:\\Users\\devin\\Videos\\')
        #mkv saved locally already
        print(midiname)
        path = 'c:\\Temp\\'
        ext = ''
        if os.path.exists(os.path.join(inputpath , midiname + ".mp4")):
            ext = ".mp4"
        elif os.path.exists(os.path.join(inputpath, midiname + ".mkv")):
            ext = ".mkv"
        if ext == '':
            print("prevIteration not found")
        else:
            temp = inputpath + midiname + ".mp4"
            tempout = path + "prevIteration.mp4"
            #copy to previousIteration
            cmd = f'copy "{temp}" "{tempout}"'
             
            # Copy File
            os.system(cmd)
            print("copy to previousIteration")
            
        
    print(iterations)
    