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
    
    

def get_playlist_items(plid, limit: int=50):
    res = []
    nextPageToken = None
    while True:
        data = get_pl_items_per_page(plid, nextPageToken, limit)
        nextPageToken = data.get("nextPageToken", None)
        res.append(data)
        
        if nextPageToken is None: break
    return res
    
    

    
stats = get_channel_stat()
print(pd.DataFrame([stats]))


data = get_playlists_data()
df = pd.DataFrame(data)
p_ids = set(df.explode('items')["items"].apply(pd.Series)["id"].to_list())
print(p_ids)


limit = 50

vidx = 0
df = pd.DataFrame(data, columns=['GroupName', 'Title', 'URL', 'PublishedDate', 'starttime', 'endtime', 'iteration'])


itemcount = 0
songdurations = {}
groupdurations = {}
for plid in p_ids:
#plid = next(iter(p_ids))
    print(plid)
    data = get_playlist_items(plid)
    dfvideos = pd.DataFrame(data)
    print(dfvideos.shape)
#    print(dfvideos.loc[0])

#    url = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails\
#        &playlistId={plid}&key={api_key}'
#    json_url = requests.get(url)
#    data = json.loads(json_url.text)
#    print(data)
#    print(dfvideos.loc[0]['items'])
#    print(data['pageInfo']['totalResults'])
    
    for idxdfv in range(dfvideos.shape[0]):
    
        if dfvideos.loc[idxdfv]['items'] is not None and len(dfvideos.loc[idxdfv]['items']) > 0:
            itemcount += len(dfvideos.loc[idxdfv]['items'])
            for item in dfvideos.loc[idxdfv]['items']:
        #    for item in data['items']:
                videoid = item['snippet']['resourceId']['videoId']
                url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails\
                    &id={videoid}&key={api_key}'
                json_url = requests.get(url)
                datav = json.loads(json_url.text)
                if (len(datav['items']) > 0):
        #            print(datav)
                    
        #            print(datav['items'][0]['snippet']['publishedAt'])
        #            print(datav['items'][0]['snippet']['title'])
        #            print(datav['items'][0]['snippet']['description'])
        #            print(datav['items'][0]['snippet']['thumbnails']['default']['url'])
        #            print(datav['items'][0]['contentDetails']['duration'])
                    
                    GroupName = ""
                    publishedDate = datav['items'][0]['snippet']['publishedAt']
                    title = datav['items'][0]['snippet']['title']
                    gs = title.find("(")
                    ge = title.find(")")
                    url = "https://www.youtube.com/watch?v=" + videoid
                    
                    if (gs > 0):
                        GroupName = title[gs+1:ge]
                        title = title[0:gs]

                    desc = datav['items'][0]['snippet']['description']

                    totalduration = datav['items'][0]['contentDetails']['duration']
                    totalduration = totalduration.replace("H", ":")
                    totalduration = totalduration.replace("M", ":")
                    totalduration = totalduration.replace("S", "")
                    totalduration = totalduration.replace("PT", "")
                    hms = totalduration.split(":")
                    #rule dont make videos over 1 hour.  
                    #just extra logic to deal with.  
                    try:
                        myduration = 0
                        if (len(hms) > 2):
                            myduration += int(hms[0]) * 3600
                            myduration += int(hms[1]) * 60
                            if (hms[2] !=""):
                                myduration += int(hms[2])
                        elif (len(hms) > 1):
                            myduration += int(hms[0]) * 60
                            if (hms[1] !=""):
                                myduration += int(hms[1])
                        else:
                            #guessing just minutes
                            myduration += int(hms[0]) * 60
                            
                        if (title in songdurations):
                            songdurations[title] += myduration
                        else:
                            songdurations[title] = myduration
                        
                        if (GroupName != ""):
                            if (GroupName in groupdurations):
                                groupdurations[GroupName] += myduration
                            else:
                                groupdurations[GroupName] = myduration
                    except:
                        print(title)
                        print(totalduration)
                    #make a map of MONTH, DAYOFWEEK, TIMEOFDAY, SONGMAP
                    #with new videos, take the time outside of TRIAL#x -> END#x and count as words.  
                    
     #   print(df)
    print(songdurations)
    #create datatable with all this data.  For each, just make an avg speed, top speed
    #create a csv file.  
    #link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
print(songdurations)
print(groupdurations)