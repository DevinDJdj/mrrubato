#get videos and create a DB of Data about all played.  
#link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
#for now just generate a csv file.  
#dont download the videos, just get the written description


#notesplayed


import sys
 
# adding Folder_2/subfolder to the system path
sys.path.insert(0, 'c:/devinpiano/')
from mymidi import MyTrack, MyMsg
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
    if (pedal > 0):
        estimate = (initialvelocity**2/math.log(timepassed+1))
        if (estimate > initialvelocity):
            estimate = initialvelocity
        return int(estimate)
    else:
        return 0
    
def fillImage(midi_image, notes, currentTime, prevTime, pedal):
    #between prevTime and currentTime fill the image    
    a = prevTime
    while (a < currentTime):
        for n in notes:
            if n.time < a and n.velocity > 0:
                c = getColor(a - n.time, n.velocity, pedal)
                #note is on
                if (c > 0):
                    midi_image[n.note*2:n.note*2+1,int(a/100)] = (0,n.velocity+c,n.velocity*2-c)      # (B, G, R)
        a += 100
    
def midiToImage(mid):
    
    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        totalTime = getTrackTime(track)
        currentTime = 0
        prevTime = currentTime
        notes = [Message('note_on', channel=0, note=60, velocity=0, time=0)] * 109
        pedal = 0
        height = 88*2
        width = int(totalTime/100)
        midi_image = np.ones((height,width,3), np.uint8)
        midi_image = 255*midi_image
        on = 0
        for msg in track:
            if (on > 0):
                currentTime += msg.time
            if (msg.type=='note_on'):
                if (on > 0):  
                    msg.time = currentTime
                    notes[msg.note] = msg
                    fillImage(midi_image, notes, currentTime, prevTime, pedal)
                    prevTime = currentTime
                on = isOn(msg.note, on)
            if (msg.type=='control_change'):
                #https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2
                if (msg.control == 64):  #assuming this is pedal, yep 
                    pedal = msg.value
                
            print(msg)
        print(totalTime)
    return midi_image

#continue here.  Need to further this.      
def enhanceMidi(mid):
    prevMsg = None
    pedal = 0
    
    for i, track in enumerate(mid.tracks):
        totalTime = getTrackTime(track)
        t = MyTrack(track, totalTime)
        on = 0
        for msg in track:
            if (msg.type=='note_on'):
                if (on > 0):  
                    m = MyMsg(msg, prevMsg, pedal)
                    prevMsg = m
                    t.notes.append(m)
                on = isOn(msg.note, on)
            if (msg.type=='control_change'):
                #https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2
                if (msg.control == 64):  #assuming this is pedal, yep 
                    pedal = msg.value
                
    
def printMidi(midilink):
    r = requests.get(midilink)
    print(len(r.content))
    with open("test.mid", "wb") as f:
        f.write(r.content)
    mid = MidiFile("test.mid")
    #outputMidi(mid)
    enhanceMidi(mid)
    img = midiToImage(mid)

    height = 200
    width = 200    
    
    path = './output/'
    cv2.imwrite(os.path.join(path , 'test.jpg'), img)
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
    