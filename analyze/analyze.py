#get videos and create a DB of Data about all played.  
#link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
#for now just generate a csv file.  
#dont download the videos, just get the written description


#notesplayed


import sys
 
# adding Folder_2/subfolder to the system path
sys.path.insert(0, 'c:/devinpiano/')
 
 
import cred
import pandas as pd
import requests
import json
from oauth2client.tools import argparser, run_flow

from mido import MidiFile

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
        
def printMidi(midilink):
    r = requests.get(midilink)
    print(len(r.content))
    with open("test.mid", "wb") as f:
        f.write(r.content)
    mid = MidiFile("test.mid")
    outputMidi(mid)
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
    