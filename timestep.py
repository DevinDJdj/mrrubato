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
 
 
import cred
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

CLIENT_SECRETS_FILE = "./../client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
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


channel_id = cred.CHANNELID
api_key = cred.APIKEY
def get_channel_stat() -> dict:
    url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={api_key}'

    r = requests.get(url)
    data = r.json()
    return data['items'][0]['statistics']
    

    
    
    
def search(mydate, limit: int=50) -> dict:
    channelId = "UC4dK3RpqBq2JpIkRmQn6HOA"
    
    url = f"https://www.googleapis.com/youtube/v3/search?maxResults={limit}&channelId={channelId}&order=date&publishedBefore={mydate}&key={api_key}&part=snippet&type=video"
    r = requests.get(url)
    return r.json()

    

if __name__ == '__main__':
    args = argparser.parse_args()

    stats = get_channel_stat()
    print(pd.DataFrame([stats]))

    mydate = date.today() + relativedelta(months=-TIME_WINDOW)
    dt = datetime.combine(mydate, datetime.min.time())
    print(dt.strftime('%Y-%m-%dT%H:%M:%SZ'))
    #unlist anything older than this.  

    
    data = search(dt.strftime('%Y-%m-%dT%H:%M:%SZ'))
    print(data)

    iterations = []    
    totalidx = 0
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
                    videos_update_response = youtube.videos().update(
                        part='status',
                        body=dict(
                          status=mystatus,
                          id=videoid
                        )).execute()            
                    print(videos_update_response)
