#get videos and create a DB of Data about all played.  
#link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
#for now just generate a csv file.  
#dont download the videos, just get the written description


#notesplayed


import sys
 
# adding Folder_2/subfolder to the system path
sys.path.insert(0, 'c:/devinpiano/')

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

CONTEXT_SIZE = 2
EMBEDDING_DIM = 10

import mymidi


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
    channelId = "UC4dK3RpqBq2JpIkRmQn6HOA"

    url = f"https://www.googleapis.com/youtube/v3/search?maxResults={limit}&channelId={channelId}&order=date&q={title}&key={api_key}&part=snippet"
    r = requests.get(url)
    return r.json()

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
        if (on > 0):
            currentTime += mymsg.msg.time
        if (mymsg.msg.type == 'note_on'):
            if mymsg.prevmsg is not None and (mymsg.prevmsg.note == 21 or mymsg.prevmsg.note == 108):
                starttimes.append(currentTime)
            if mymsg.nextmsg is not None and (mymsg.nextmsg.note == 22 or mymsg.nextmsg.note == 107):
                endtimes.append(currentTime)
        if (mymsg.msg.type == 'note_on'):
            on = isOn(mymsg.msg.note, on)
                

    return starttimes, endtimes

def getTrackTime(track):
    #skip between pauses and only start with the start signal.  
    currentTime = 0
    on = 0
    for msg in track:        
        if (on > 0):
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
        if (starttimes[i] <= currentTime and currentTime <= endtimes[i]):
            return i
    print("getIterationError" + str(currentTime))
    print(starttimes)
    print(endtimes)
    return -1
    
def midiToImage(t, midilink):
    
    print('Track: {}'.format(t.track.name))
    notes = [Message('note_on', channel=0, note=60, velocity=0, time=0)] * 109
    pedal = 0
    height = 88*2
    width = 1
    starttimes, endtimes = getTrackTimes(t)
    midi_image = None
    if len(starttimes) != len(endtimes) or len(starttimes) < 1:
        print("Incorrect data, please fix" + midilink)
    else:    
        for i, st in enumerate(starttimes):
            w = int((endtimes[i]-starttimes[i])/100)
            if w > width:
                width = w +1
        height = (i+1)*88*2
        midi_image = np.ones((height,width,3), np.uint8)
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
    
    
    for i, track in enumerate(mid.tracks):
        totalTime = getTrackTime(track)
        t = mymidi.MyTrack(track, totalTime)
        on = 0
        for msg in track:
            if (msg.type=='note_on'):
                if (on > 0):  
                    m = mymidi.MyMsg(msg, prevMsg, pedal)
                    if (prevMsg is not None):
                        prevMsg.nextmsg = m
                    prevMsg = m
                    t.notes.append(m)
                on = isOn(msg.note, on)
            if (msg.type=='control_change'):
                #https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2
                if (msg.control == 64):  #assuming this is pedal, yep 
                    pedal = msg.value
    return t
    
def getNgrams(t):
    it = -1
    on = 0
    currentTime = 0
    prevTime = currentTime
    starttimes, endtimes = getTrackTimes(t)
    if len(starttimes) != len(endtimes) or len(starttimes) < 1:
        print("Incorrect data, please fix")
        
    else:    
        notearray = np.zeros(len(t.notes), dtype=int)
        #create array of [iterations (10)][notes (88)][prevnote (88)]
        data = np.zeros((10, 88, 88), dtype=int)
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
                while (i < mymidi.MAXNGRAM and mymsg.prevmsg is not None):
                    tempmsg = mymsg.prevmsg
                    i = i+1
                    mymsg.ngrams[mymidi.MAXNGRAM-i] = tempmsg.note
                
                mymsg.ngramstensor = torch.tensor(mymsg.ngrams)
                #use this tensor for prediction
                #for now fill the array to do some statistics.  
                data[it][mymsg.prevmsg.msg.note-21][mymsg.msg.note-21] += 1
                #for now return the random note based on probability distribution from this array
            if (mymsg.msg.type=='note_on'):
                if (on > 0 and it > -1):  
                    prevTime = currentTime
                on = isOn(mymsg.note, on)
        return data
        
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

def printMidi(midilink):
    r = requests.get(midilink)
    print(len(r.content))
    with open("test.mid", "wb") as f:
        f.write(r.content)
    mid = MidiFile("test.mid")
    #outputMidi(mid)
    t = enhanceMidi(mid)
    data = getNgrams(t)
    img = midiToImage(t, midilink)

    height = 200
    width = 200    
    midiname = os.path.basename(midilink)
    midiname = os.path.splitext(midiname)[0]
    path = './output/'
    if (img is not None):
        cv2.imwrite(os.path.join(path , midiname + '.jpg'), img)
    
    #what is the note distribution for each and the interval distribution look like?  
    #show a distribution of previous->max
    temp = data.sum(axis=0) #combine all iterations
    
    print(temp[36]) #probability of key after 36
    
    keystrokes = temp.sum(axis=0) #keystrokes for all keys
    print(keystrokes) 
    plt.figure(0)
    _ = plt.hist(keystrokes, bins='auto')
    plt.title("Histogram with 'auto' bins")
    plt.xlim([5,1500])
    plt.savefig(os.path.join(path , 'ks_' + midiname + '.png'))
    plt.figure(0).clear()
#    plt.show()
    keys = np.indices((len(keystrokes),))
    print(keys[0])
    values = list(keystrokes)
    plt.figure(1)
    plt.bar(list(keys[0]), values)
    plt.xlim([0, 90])
#    plt.figure().set_figwidth(109)
#    plt.show()
    plt.savefig(os.path.join(path , 'ks2_' + midiname + '.png'))
    plt.figure(1).clear()
    #ok enough for now.  
    #save this type of info to images and then use it in analyze.html to review.  
    #much more analytics needed here.  
    
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
    plt.savefig(os.path.join(path, 'kk_' + midiname + '.png'))
    plt.figure(2).clear()
    #lets get the correlation matrix.  
    #lets normalize this across row.  
    
    
#    testNgramModel()
    #from here lets generate a graphic.  
    #read with mido?  

if __name__ == '__main__':
    argparser.add_argument("--title", help="Video title", default="What a Wonderful World")
    args = argparser.parse_args()

    title = args.title
    stats = get_channel_stat()
    print(pd.DataFrame([stats]))


    data = search(title)
    print(data)

    iterations = []    
    totalidx = 0
    for item in reversed(data["items"]):
#    for item in data['items']:
#        print(item["id"])
        if (item["id"]["kind"] == "youtube#video"):
            videoid = item["id"]["videoId"]
            url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,status\
                &id={videoid}&key={api_key}'
            json_url = requests.get(url)
            datav = json.loads(json_url.text)
            if (len(datav['items']) > 0):
                totalduration = datav['items'][0]['contentDetails']['duration']
                GroupName = ""
                publishedDate = datav['items'][0]['snippet']['publishedAt']
                title = datav['items'][0]['snippet']['title']
                privacystatus = datav['items'][0]['status']['privacyStatus']
                gs = title.find("(")
                ge = title.find(")")
                url = "https://www.youtube.com/watch?v=" + videoid
                
                if (gs > 0):
                    GroupName = title[gs+1:ge]
                    title = title[0:gs]

                desc = datav['items'][0]['snippet']['description']
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
                    printMidi(midilink)
                
                if (len(starttimes) != len(endtimes)):
                    print("invalid data {videoid}")
                else:
                    print(starttimes)
                    for idx,t in enumerate(starttimes):
                        totalidx +=1
                        mydata = {"URL": url, "PublishedDate": publishedDate, "starttime": starttimes[idx], "endtime": endtimes[idx], "iteration": totalidx}
#                        print(mydata)
                        iterations.append(mydata)
            
    print(iterations)
    