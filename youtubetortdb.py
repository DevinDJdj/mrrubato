# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import google_auth_oauthlib.flow
from oauth2client.file import Storage

from oauth2client.tools import argparser, run_flow
import googleapiclient.discovery
import googleapiclient.errors

import sys
sys.path.insert(0, 'c:/devinpiano/')
 

import cred

#guess I am using firestore.  
#not sure why this is necessary
#gcloud alpha firestore databases update --type=firestore-native
#oh this is not working, just use the rtdb stuff.  


import firebase_admin
from firebase_admin import db
from firebase_admin import firestore

from firebase_admin import credentials
import requests
import json


#https://misterrubato-test-default-rtdb.firebaseio.com/

channel_id = cred.CHANNELID
api_key = cred.APIKEY

def main():
    argparser.add_argument("--video", help="Video ID", default="4flRJWtfY9c")
    args = argparser.parse_args()

    cred = credentials.Certificate("../misterrubato-test.json")
    databaseURL = "https://misterrubato-test-default-rtdb.firebaseio.com/"
    firebase_admin.initialize_app(cred, {
	'databaseURL':databaseURL
	})
    ref = db.reference("/")
    print(ref)

    videoid = args.video
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
            datav['items'][0]['snippet']['group'] = GroupName

        desc = datav['items'][0]['snippet']['description']

        
        #insert into DB
        ref = db.reference(f'/misterrubato/{videoid}')
        ref.set(datav['items'][0])

    #ok this is a start.  
    #now we have to change to use this structure instead of calling the youtube API, that is kind of annoying.  
    #also on record.py, we need to add this same data.  
    ref = db.reference(f'/misterrubato')
    snapshot = ref.order_by_child('snippet/title').equal_to('I Do It For You (Bryan Adams)').get()
    for key, value in snapshot.items():
        print(key)
        print(value)
        
if __name__ == "__main__":
    main()