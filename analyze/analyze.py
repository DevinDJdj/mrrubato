#get videos and create a DB of Data about all played.  
#link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
#for now just generate a csv file.  
#dont download the videos, just get the written description


#notesplayed


import sys

import datetime
# adding Folder_2/subfolder to the system path
#not great mechanism for config.  Maybe just make absolute path?
sys.path.insert(0, 'c:/devinpiano/')
sys.path.insert(1, 'c:/devinpiano/music')
#sys.path.append('../')
import config  

import os
import cred
import pandas as pd
import requests
import json
from oauth2client.tools import argparser, run_flow

from mido import MidiFile
from mido import Message
import math

#generate image from midi
import cv2
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

import webbrowser

#from subprocess import Popen
import subprocess

CONTEXT_SIZE = 2
EMBEDDING_DIM = 10

import mymidi

#pip install qrcode
import qrcode

from PIL import Image, ImageDraw


mappgram = {} #map [ SIGNGRAM ] [PGRAM]
mapsgram = {} #map [seqngram][pgram]

channel_id = cred.CHANNELID
api_key = cred.APIKEY
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

def midiToImage(t, midilink):
    
    print('Track: {}'.format(t.track.name))
    notes = [Message('note_on', channel=0, note=60, velocity=0, time=0)] * 109
    pedal = 0
    height = 88*2
    iwidth = 1
    starttimes, endtimes = getTrackTimes(t)
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
                currentTime += mymsg.msg.time
                #not very efficient, but good enough for now.  
                i = getIteration(currentTime, starttimes, endtimes)
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
                        m.msg.time += othertime
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
    
def getNgrams(t):
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
        #create array of [iterations (10)][notes (88)][prevnote (88)]
        data = np.zeros((20, 88, 88), dtype=int)
        rythmdata = np.zeros((20, 64, 64), dtype=int)
        #create an array of [iterations (10][notes (88)][
        #only sum across [notes]
        
        #then create a plot of each 
        #calculated volume of each note like we have for the piano roll.  
        #then create histogram of this.  
        counter = 0
        for mymsg in t.notes:
            if (on > 0):
                currentTime += mymsg.msg.time
                notearray[counter] = mymsg.msg.note
                counter += 1
                #not very efficient, but good enough for now.  
                it = getIteration(currentTime, starttimes, endtimes)
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
                signs = mymsg.getSigns(wrds) 
                
                #here can use seqgram as well.  
                #try to find the patterns.  
                #what sequences are the same, probably find more about playing quality than anything intrinsic to the piece.  
                if signs not in mappgram:
                    mappgram[signs] = {}
                if pgram not in mappgram[signs]:
                    mappgram[ signs ] [ pgram ] = { 'time': [], 'iteration': [] }
                    
                it = getIteration(currentTime, starttimes, endtimes)
                reltime = getRelativeTime(it, currentTime, starttimes, endtimes)
                mappgram[ signs ] [ pgram ]['time'].append( reltime)
                mappgram[ signs ] [ pgram ]['iteration'].append(it)
                
                
                if seqgram not in mapsgram:
                    mapsgram[seqgram] = {}
                if pgram not in mapsgram[seqgram]:
                    mapsgram[ seqgram ] [ pgram ] = { 'time': [], 'iteration': [] }
                mapsgram[ seqgram ] [ pgram ]['time'].append(reltime)
                mapsgram[ seqgram ] [ pgram ]['iteration'].append(it)

            if (mymsg.msg.type=='note_on'):
                if (on > 0 and it > -1):  
                    prevTime = currentTime
                on = isOn(mymsg.note, on)
        return data, rythmdata
        
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
        im.save(path + str(i) + '.png',
                save_all=True, append_images=images[1:], optimize=False, duration=40, loop=0)
    

def printMidi(midilink, title, GroupName, videoid):
    path = './output/'
    midilink = midilink.replace("\r", "")
    midiname = os.path.basename(midilink)
    midiname = os.path.splitext(midiname)[0]
    filename = midiname + '.jpg'
    #dont redo this.  Live with the analysis of the time for now.  
    if (os.path.exists(os.path.join(path , filename))):
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
    img = midiToImage(t, midilink)

    printMidiGif(t, midilink)
    data, rythmdata = getNgrams(t)
    if (data is None):
        return
        

    height = 200
    width = 200    

#this is to only generate the midi data which has not been created yet.      
    if (img is not None):
        cv2.imwrite(os.path.join(path , filename), img)
        uploadanalyze(filename, os.path.join(path, filename))
    
    #what is the note distribution for each and the interval distribution look like?  
    #show a distribution of previous->max
    temp = data.sum(axis=0) #combine all iterations
    temprythm = rythmdata.sum(axis=0)
    
    print(temp[36]) #probability of key after 36
    
    keystrokes = temp.sum(axis=0) #keystrokes for all keys
    rythms = temprythm.sum(axis=0)

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

if __name__ == '__main__':
    argparser.add_argument("--title", help="Video title", default="What a Wonderful World")
    argparser.add_argument("--video", help="Video ID", default="4flRJWtfY9c")
    #for now this is kind of getting annoying.  We can always calculate this later.  
    argparser.add_argument("--skipfinger", help="Skip finger test", default="true")
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
#    print(data)

    iterations = []    
    totalidx = 0
    latestvideo = None
    latestvideoitem = None
    latestvideoDate = None
    latestmidilink = None
    for key, item in reversed(data):
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
                midisize = printMidi(midilink, title, GroupName, videoid)
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
                        cmd = ["python", "./analyze/fingertest.py", "--video", "\"" + videoid + "\"", "--midi", midilink]
                        print(cmd)
#                        os.spawn("python", cmd, no_wait=True)
                        proc = subprocess.Popen(cmd)
                        print("fingertest started")

            
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
    