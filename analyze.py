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
                    totalduration = datav['items'][0]['contentDetails']['duration']
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
                    times = []
                    ts = desc.find("1st (")
                    te = desc.find(")", ts)
                    if (ts > -1):
                        times.append(desc[ts+5:te])
                    ts = desc.find("2nd (")
                    te = desc.find(")", ts)
                    if (ts > -1):
                        times.append(desc[ts+5:te])
                    ts = desc.find("3rd (")
                    te = desc.find(")", ts)
                    if (ts > -1):
                        times.append(desc[ts+5:te])
                    for i in range(4,15):
                        ts = desc.find("{}th (".format(i))
                        te = desc.find(")", ts)
                        if (ts > -1):
                            times.append(desc[ts+5:te])


                    if len(times) < 1:
                        times[0] = "0:00"
                    for idx,t in enumerate(times):
                        starttime = t
                        if idx < len(times)-1:
                            endtime = times[idx+1]
                        else:
                            endtime = totalduration
                            e = endtime.find("M")
                            
                            endtime = endtime.replace("M", ":")
                            endtime = endtime.replace("S", "")
                            endtime = endtime.replace("PT", "")
                            idxa = endtime.rfind(":")
                            if idxa > -1 and len(endtime)-idxa < 3:
                                endtime = endtime[:idxa+1] + "0" + endtime[idxa+1:]
                        data = {"GroupName": f'"{GroupName}"', "Title": f'"{title}"', "URL": url, "PublishedDate": publishedDate, "starttime": starttime, "endtime": endtime, "iteration": idx+1}
                        df.loc[vidx] = data#[GroupName, title, url, publishedDate, starttime, endtime, idx]
                        vidx = vidx + 1
                        
        #                print(data)
                #        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
        #                print(GroupName)
        #                print(title)
        #                print(url)
        #                print(publishedDate)
        #                print(starttime)
        #                print(endtime)
        #                print(idx)
        
     #   print(df)
    print(itemcount)
    #create datatable with all this data.  For each, just make an avg speed, top speed
    #create a csv file.  
    #link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
df.drop_duplicates()
df.to_csv("test.csv")
    