#get videos and create a DB of Data about all played.  
#link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
#for now just generate a csv file.  
#dont download the videos, just get the written description


#notesplayed


import sys
import os
import httplib2 
# adding Folder_2/subfolder to the system path
sys.path.insert(0, 'c:/devinpiano/')
 
import config 
#import cred
#import record

import pandas as pd
import requests
import json
from oauth2client.tools import argparser, run_flow

#print(cred.APIKEY)
from datetime import datetime
from datetime import date

from dateutil.relativedelta import relativedelta

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import firebase_admin
from firebase_admin import db
from firebase_admin import firestore

from firebase_admin import credentials
from firebase_admin import initialize_app, storage, auth

CLIENT_SECRETS_FILE = "./../client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))


TIME_WINDOW = 6


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("../%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))


channel_id = config.cfg['youtube']['CHANNELID']
api_key = config.cfg['youtube']['APIKEY']
def get_channel_stat() -> dict:
    url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}'

    r = requests.get(url)
    data = r.json()
    return data['items'][0]['statistics']
    

    
def add_video_to_playlist(videoID,playlistID, args):
    youtube = get_authenticated_service(args) #write it yourself
    body=dict(
      snippet=dict(
        playlistId=playlistID,
        resourceId=dict(
          kind="youtube#video",
          videoId=videoID
        ),
      ),
    )
#    add_video_request=youtube.playlistItems().insert(
#        part="snippet",
#        body=body
#    ).execute()

#cant use position, but default is to add at the end anyway.  
#but we need to list then by date.  
    request = youtube.playlistItems().insert(
    part="snippet",
    body={
      "snippet": {
        "playlistId": playlistID,
#        "position": 0,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": videoID
        }
      }
    }
    )
    response = request.execute()
    
    
def search(mydate, limit: int=50) -> dict:
    channelId = "UC4dK3RpqBq2JpIkRmQn6HOA"
    
    url = f"https://www.googleapis.com/youtube/v3/search?maxResults={limit}&channelId={channelId}&order=date&publishedBefore={mydate}&key={api_key}&part=snippet&type=video"
    r = requests.get(url)
    return r.json()

    
def localBackup():
    # Get the Firebase reference
    ref = db.reference(f'/misterrubato/')

    # Get the backup path
    backup_path = "c:/devinpiano/backup/"

    # Take the backup
    today = date. today()
    today = today. strftime("%Y%m%d")
    
    with open(backup_path + today + '.json', 'w') as f:
        json.dump(ref.get(), f)
        

    snapshot = ref.order_by_child('snippet/publishedAt').get()
    return snapshot.items()
#    return ref.items()


def getPlaylistFromGrade(grade):
    if grade == "test":
        return ""
    if int(grade) > 8:
        return cred.GREAT_PLAYLIST
    elif int(grade) > 4:
        return cred.GOOD_PLAYLIST
    elif int(grade) == 0:
        return ""
    else:
        return cred.OK_PLAYLIST
        
if __name__ == '__main__':
    args = argparser.parse_args()

    stats = get_channel_stat()
    print(pd.DataFrame([stats]))

    mydate = date.today() + relativedelta(months=-TIME_WINDOW)
    dt = datetime.combine(mydate, datetime.min.time())
    print(dt.strftime('%Y-%m-%dT%H:%M:%SZ'))
    #unlist anything older than this.  

    
    databaseURL = "https://misterrubato-test-default-rtdb.firebaseio.com/"
    # Init firebase with your credentials
    creda = credentials.Certificate("../misterrubato-test.json")
    initialize_app(creda, {'storageBucket': 'misterrubato-test.appspot.com', 'databaseURL':databaseURL})    

    data = search(dt.strftime('%Y-%m-%dT%H:%M:%SZ'))
    print(data)

    iterations = []    
    totalidx = 0
    #take local backup of full DB.  
    ref = localBackup()
    #ok this looks ok.  Now use the retrieved DB and update any info in the DB.  
    #then get each video individually from the DB info.  
    #no need to search.  
    #just do the ones which are recent.  
    #and update in Youtube as well as we go through.  
    #retrieve, if they are different, update in youtube.  
    
    
    adminuid = config.cfg['youtube']['ADMIN_USERID']
    
    #need to sort by date.  
    for key, item in ref:
#    for item in reversed(data["items"]):
#    for item in data['items']:
#        print(item["id"])
        if (item["kind"] == "youtube#video"):
#            print(item)
            videoid = item["id"]
            privacystatus = item['status']['privacyStatus']
            url = f'https://www.googleapis.com/youtube/v3/videos?part=status\
                &id={videoid}&key={api_key}'
            #for now get rid of all the old data from the queries gradually everything up to when we use DB.  
            #data quality is too poor to do much with anyway.  Also no midi before Jan/2023.  
            publishedDate = item['snippet']['publishedAt']
            print(publishedDate + " " + videoid + " " + privacystatus + " " + item['snippet']['title'])
            #what is the state of this and the title etc.  
            
            pDate = datetime.strptime(publishedDate, '%Y-%m-%dT%H:%M:%SZ')
            pl = ""
            plwords = ""
            #update to public if we have reviewed.  
            #if we dont want to publish, rank as 0.  
            if (privacystatus=="unlisted" and pDate.date() > mydate):
                refpl = db.reference(f'/misterrubato/' + videoid + '/playlist')
                #if this exists, return
                if refpl.get() is None and "comments" in item:
                    if adminuid in item["comments"]:
                        grade = item["comments"][adminuid]["sentiment"]
                        pl = getPlaylistFromGrade(grade)
                        if pl !="":
                            print("add " + videoid + " to " + pl)
                            #add to playlist
                            if  "stats" in item:
                                if item["stats"]["wordsrecognized"] > 50:
                                    plwords = cred.WORDS_PLAYLIST
                                    print("add to words " + plwords)
                                    #add to playlist.  
                                    add_video_to_playlist(videoid, plwords, args)
                        
                                
                            #really this can all be set at play record.py as well, but this is essentially the same as we run this during record.py
                            #need to test this works.  Seems to work ok.  
                            if pl !="":
                                item['status']['privacyStatus'] = "public"
                                vref = db.reference(f'/misterrubato/' + videoid)
                                vref.set(item)
                                data = {'playlist':pl,'wordsplaylist':plwords}
                                refpl.set(data)
                                if plwords !="":
                                    add_video_to_playlist(videoid, plwords, args)
                                add_video_to_playlist(videoid, pl, args)
                                mystatus = {}         
                                mystatus['privacyStatus'] = "public"
                                
                                youtube = get_authenticated_service(args)
                                videos_update_response = youtube.videos().update(
                                    part='status',
                                    body=dict(
                                      status=mystatus,
                                      id=videoid
                                    )).execute()            
                                print(videos_update_response)
                            

                
            if ((privacystatus=="public" or privacystatus=="unlisted") and pDate.date() < mydate ):
                print(videoid)
                print("Making private")
                youtube = get_authenticated_service(args)
                
                #update the RTDB as well.  
                item['status']['privacyStatus'] = "private"
                vref = db.reference(f'/misterrubato/' + videoid)
                vref.set(item)
                
                mystatus = {}         
                mystatus['privacyStatus'] = "private"
                
                videos_update_response = youtube.videos().update(
                    part='status',
                    body=dict(
                      status=mystatus,
                      id=videoid
                    )).execute()            
                print(videos_update_response)

    prior = """
    for item in reversed(data["items"]):
    
#    for item in data['items']:
#        print(item["id"])
        if (item["id"]["kind"] == "youtube#video"):
            videoid = item["id"]["videoId"]
            url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,status\
                &id={videoid}&key={api_key}'
            json_url = requests.get(url)
            datav = json.loads(json_url.text)
            if (len(datav['items']) > 0):
                privacystatus = datav['items'][0]['status']['privacyStatus']
            
                url = f'https://www.googleapis.com/youtube/v3/videos?part=status\
                    &id={videoid}&key={api_key}'
                youtube = get_authenticated_service(args)
                #for now get rid of all the old data from the queries gradually everything up to when we use DB.  
                #data quality is too poor to do much with anyway.  Also no midi before Jan/2023.  
                if (privacystatus=="public" or privacystatus=="unlisted"):
                    mystatus = {}         
                    mystatus['privacyStatus'] = "private"
                    #update the RTDB as well.  
                    
                    videos_update_response = youtube.videos().update(
                        part='status',
                        body=dict(
                          status=mystatus,
                          id=videoid
                        )).execute()            
                    print(videos_update_response)
    """