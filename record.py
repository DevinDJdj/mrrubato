#git config http.postBuffer 524288000
#git reset --soft HEAD^1
#pip install google-api-python-client
#npm install -g firebase-tools
#https://misterrubato-test.web.app
#https://console.firebase.google.com/u/1/project/misterrubato-test/hosting/sites?hl=en-US
#category 10 is music
#python ./upload.py --file="./input/test.mp4" --title="Test Upload" --description="Wow this should be easy" --keywords="music, piano" --category="10" --privacyStatus="private"
#ffmpeg -i "2022-12-13 12-32-17.mkv" -codec copy "2022-12-13 12-32-17.mp4"
#python ./upload.py --file="./input/2022-12-13 12-32-17.mkv" --title="Test Upload" --description="Wow this should be easy" --keywords="music, piano" --category="10" --privacyStatus="private"
#python ./upload.py --file="./input/2022-12-12_13-46-58.mkv" --title="Test Upload" --description="Wow this should be easy" --keywords="music, piano" --category="10" --privacyStatus="private"
#python ./upload.py --file="./output/testmidi/2022-12-22 20-43-48.mkv" --title="Test Upload" --description="Wow this should be easy" --keywords="music, piano" --category="10" --privacyStatus="private"

#I use description not title.  
#python ./record.py --description "Claire De Lune"
#python ./record.py --description "Claire De Lune" --config "config.json"


#!/usr/bin/python
#getting stuff for image processing.  
#pip install opencv-python #key detection

#pip install mido #midi capture
#pip install rtmidi #midi capture
#pip install py-midi 
#pip install python-rtmidi
#install vc++ redistributable.  

#pip install pydrive

#pip install manim #math visualization
#moviepy 1.0.3 requires decorator<5.0,>=4.0.2, but you have decorator 5.1.1 which is incompatible.


#from midi file get start times and stop times.  
#for now just use the next note after the start video/stop video (21/22)
#and the pause/unpause (108?)
#use note prior to pause to indicate end.  
#use note after unpause to indicate next iteration.  
#use note before stop video to indicate end.  
#1st (), 1st end ()
#2nd (), 2nd end ()

import math
#import httplib
import httplib2
import os
import glob
import random
import sys
import time
import cv2
import pytesseract
from PIL import Image
import numpy as np
import string

import mido
from mido import Message, MidiFile, MidiTrack

from mido.ports import MultiPort

import datetime

import config 

#pip install pynput
#key input for hotkeys to trigger recording etc.  
from pynput.keyboard import Key, Controller

import subprocess
import sys
sys.path.insert(0, 'c:/devinpiano/')
 
 
import cred


channel_id = cred.CHANNELID
api_key = cred.APIKEY



from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


from transcribe import transcribe_me, transcribe_me2, get_timestamp
import util

import firebase_admin
from firebase_admin import db
from firebase_admin import firestore

from firebase_admin import credentials
from firebase_admin import initialize_app, storage

import requests
import json

import mykeys


import manim
# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
#, httplib.NotConnected,
#  httplib.IncompleteRead, httplib.ImproperConnectionState,
#  httplib.CannotSendRequest, httplib.CannotSendHeader,
#  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.cloud.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = config.cfg['youtube']['CLIENT_SECRETS_FILE']

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

GOOGLE_PLUS_SCOPE = "https://www.googleapis.com/auth/plus.me"
#https://www.googleapis.com/auth/userinfo.profile
GOOGLE_PLUS_SERVICE_NAME = "plus"
GOOGLE_PLUS_VERSION = "v1"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
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

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")



#midiIn = MidiIn()
 
#def printNote(eventType, channel, data1, data2):
#   print ("pitch =", data1, "volume =", data2)
 
#midiIn.onNoteOn(printNote)
 
# since we have established our own way to process incoming messages,
# stop printing out info about every message
#midiIn.hideMessages()
    


def get_authenticated_service(args, myscope=YOUTUBE_SCOPE):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=myscope,
#    scope=[GOOGLE_PLUS_SCOPE, myscope],
    message=MISSING_CLIENT_SECRETS_MESSAGE)
  

#  userservice = build(GOOGLE_PLUS_SERVICE_NAME, GOOGLE_PLUS_VERSION, http=http)
#  userpeople = userservice.people()
#  me = userpeople.get(userId="me").execute()

#  print(me)
  #then use this to add uid to the video info.  


  storage = Storage("%s-oauth2.json" % config.cfg["youtube"]["CHANNELID"])
  credentials = storage.get()
  #this local storage of creds was causing problems.  Finally this works now to add to the playlist.  
#  credentials = None
  if credentials is None or credentials.invalid or args.config != "config.json":
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

   
def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body=dict(
    snippet=dict(
      title=options.title,
      description=options.description,
      tags=tags,
      categoryId=options.category
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  return resumable_upload(insert_request)


def addtodb(videoid, args):
#need to utilize a different mechanism here.  
    #this youtube data structure is really not needed.  
    if (config.cfg['youtube']['enabled'] == "true"):
        url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,status\
            &id={videoid}&key={api_key}'
        json_url = requests.get(url)
        datav = json.loads(json_url.text)
    else:
        datav = {}
        datav['items'] = []
        datav['items'].append({'snippet': {'title': args.title, 'description': args.description}})
        datav['items'][0]['snippet']['resourceId'] = {'videoId': videoid}
        datav['items'][0]['snippet']['publishedAt'] = "2022-12-12T12:12:12Z"
        datav['items'][0]['snippet']['channelId'] = channel_id
        datav['items'][0]['snippet']['categoryId'] = "10"
        datav['items'][0]['snippet']['tags'] = ["Test", "Test"]
        datav['items'][0]['snippet']['defaultLanguage'] = "en"
        datav['items'][0]['contentDetails'] = {"duration": "PT1H1M1S", "dimension": "2d", "definition": "hd", "caption": "false", "licensedContent": "true"}
        datav['items'][0]['status'] = {"uploadStatus": "uploaded", "privacyStatus": "unlisted", "license": "youtube", "embeddable": "true", "publicStatsViewable": "true"}
        datav['items'][0]['status']['license'] = "CC BY"
        datav['items'][0]['status']['privacyStatus'] = "unlisted"

    if (len(datav['items']) > 0):
        GroupName = ""
        title = datav['items'][0]['snippet']['title']
        #add userid.  
        #datav['items'][0]['uid'] = me
        gs = title.find("(")
        ge = title.find(")")
        url = "https://www.youtube.com/watch?v=" + videoid
        
        if (gs > 0):
            GroupName = title[gs+1:ge]
            title = title[0:gs]
            datav['items'][0]['snippet']['group'] = GroupName

        datav['items'][0]['snippet']['uid'] = config.cfg["uid"]
        #insert into DB
        ref = db.reference(f'/misterrubato/' + videoid)
        ref.set(datav['items'][0])

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print ("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print ("Video id '%s' was successfully uploaded." % response['id'])
          videoid = response['id']
          return response['id']
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print (error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print ("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)
  return None
  

def uploadmediafile(file, title):
    # Put your local file path 
    Title = title + '.mp4'
    fileName = file + '.mp4'
    bucket = storage.bucket()
    year = datetime.date.today().year
#    blob = bucket.blob('videos/' + Title)
    blob = bucket.blob('videos/' + str(year) + '/' + Title)
    blob.upload_from_filename(fileName)

    # Opt : if you want to make public access from the URL
    blob.make_public()

    print("your media file url", blob.public_url)
    return blob.public_url
   

def uploadtranscript(file, title):
 
    # Put your local file path 
    Title = title + '.txt'
    fileName = file + '.txt'
    bucket = storage.bucket()
    year = datetime.date.today().year
#    blob = bucket.blob('words/' + Title)
    blob = bucket.blob('words/' + str(year) + '/' + Title)
    blob.upload_from_filename(fileName)

    # Opt : if you want to make public access from the URL
    blob.make_public()

    print("your transcript file url", blob.public_url)
    return blob.public_url

def uploadmidi(file, title):


    # Put your local file path 
    Title = title + '.mid'
    fileName = file + '.mid'
    bucket = storage.bucket()
    year = datetime.date.today().year
#    blob = bucket.blob('midi/' + Title)
    blob = bucket.blob('midi/' + str(year) + '/' + Title)
    blob.upload_from_filename(fileName)

    # Opt : if you want to make public access from the URL
    blob.make_public()

    print("your midi file url", blob.public_url)
    return blob.public_url
    
    
    
def calculatedelay(pausestart, pauseend):
    delay = 0
    print(pausestart)
    print(pauseend)
    for idx in range(len(pauseend)):
        delay += pauseend[idx] - pausestart[idx]
    return delay
    
    
def add_video_to_playlist(videoID,playlistID, args):
    youtube = get_authenticated_service(args, YOUTUBE_SCOPE) #write it yourself
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

    request = youtube.playlistItems().insert(
    part="snippet",
    body={
      "snippet": {
        "playlistId": playlistID,
        "position": 0,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": videoID
        }
      }
    }
    )
    print(playlistID)
    response = request.execute()
    
def get_latest_file():
    list_of_files = glob.glob('C:/Users/devin/Videos/*.mp4') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    return latest_file


#python ./record.py --description "Test" --config "../config_ms.json"
if __name__ == '__main__':

    argparser.add_argument("--rerun", help="Rerun upload",
      default="false") #--rerun true perhaps add other options but right now this is all that really fails.  
    argparser.add_argument("--file", required=False, help="Video file to upload")
    argparser.add_argument("--title", help="Video title", default="New Upload")
    argparser.add_argument("--description", help="Video description",
      default="New Upload")
    argparser.add_argument("--config", required=False, help="Config file to use", default="config.json")
    
    argparser.add_argument("--category", default="10",
      help="Numeric video category. " +
        "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",
      default="music,learning,experiment")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
      default=VALID_PRIVACY_STATUSES[2], help="Video privacy status.") #default unlisted
    args = argparser.parse_args()

    if (args.config != "config.json"):
        config.cfg = config.init(args.config)
        CLIENT_SECRETS_FILE = config.cfg['youtube']['CLIENT_SECRETS_FILE']

    channel_id = config.cfg["youtube"]["CHANNELID"] #cred.CHANNELID
    api_key = config.cfg["youtube"]["APIKEY"] #cred.APIKEY


    if (args.title == "New Upload"):
        args.title = args.description
        
#    print(cred.MY_PLAYLIST)
#    add_video_to_playlist('7Aadr9Fmftk', cred.MY_PLAYLIST, args)
    temp = "C:\\Temp\\prevIteration.mp4"
    cmd = f'del "{temp}"'
     
    # Copy File
    os.system(cmd)
    print("delete previousIteration")

    myid = time.strftime("%Y%m%d%H%M%S") #for now just use this as ID, not sure if we want global IDs or not.           
    databaseURL = config.cfg["firebase"]["fbconfig"]["databaseURL"]
    if (args.rerun == "true"):
        print("Start Rerun")
        # Init firebase with your credentials
        creda = credentials.Certificate(config.cfg["firebase"]["credentialsfile"])
        initialize_app(creda, {'storageBucket': config.cfg["firebase"]["fbconfig"]["storageBucket"], 'databaseURL':databaseURL})    
        args.file = get_latest_file()
        tempfile = open('desc.txt', 'r')
        args.description = tempfile.read()
        tempfile.close()
        if (config.cfg['youtube']['enabled'] == "true"):
            print("Authentication with Youtube")
            youtube = get_authenticated_service(args)
            videoid = initialize_upload(youtube, args)    
            add_video_to_playlist(videoid, cred.MY_PLAYLIST, args)
        else:
            videoid = myid 
        addtodb(videoid, args)
        print("End Rerun")
        sys.exit(0)


    #start up analyze.py with this title/description.  
#    os.system('python ./analyze/analyze.py --title "' + args.description + '"')
#use title here as description contains all info
    print('analyze start python ./analyze/analyze.py --title "' + args.title + '"')
    subprocess.call('python ./analyze/analyze.py --title "' + args.title + '"')
    print("analyze complete")
    obsp = subprocess.Popen("C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe", start_new_session=True, cwd="C:\\Program Files\\obs-studio\\bin\\64bit")
    
    time.sleep(3)
#    mido.set_backend('mido.backends.portmidi')   
    mid = MidiFile()
#    mid.ticks_per_beat = 1000000
#    mid.tempo = 60
    track = MidiTrack()
    controltrack = MidiTrack()
#    track.append(MetaMessage('set_tempo', tempo=100000, time=0))
    mid.tracks.append(track)
    #mid.tracks.append(controltrack)
    test = """
    track.append(Message('program_change', program=12, time=0))
    track.append(Message('note_on', note=64, velocity=64, time=32))
    track.append(Message('note_off', note=64, velocity=127, time=32))
    track.append(Message('note_on', note=65, velocity=64, time=32))
    track.append(Message('note_off', note=65, velocity=127, time=32))
    track.append(Message('note_on', note=66, velocity=64, time=32))
    track.append(Message('note_off', note=66, velocity=127, time=32))
    track.append(Message('note_on', note=67, velocity=64, time=32))
    track.append(Message('note_off', note=67, velocity=127, time=32))
    track.append(Message('note_on', note=68, velocity=64, time=32))
    track.append(Message('note_off', note=68, velocity=127, time=32))
    track.append(Message('note_on', note=69, velocity=64, time=32))
    track.append(Message('note_off', note=69, velocity=127, time=32))
"""    
    
    #when we start the recording, lets get data from the previous iterations so that we have some comparison
    #spit out previous statistics on iterations here in this record.py for reference.  
    #separate function, or separate file?  Use Youtube Query to get data/time analysis and analyze midi as well.  
    #printPrevStats(title)    
    delay = 0
    timeoffset = 0
    starttime = 0
    pausestart = []
    pauseend = []
    lastnote = 0
    faketime = 0
    test = """
    """
    lasttick = 0
    controltick = 0
    #mido doc is crap.  But this seems ok for now.  
    #the video and midi appear to match up pretty well.  But not perfect I think.  
    #at least enough to get the start times now.  
    #need some comment here, what is input[1].  Having hardware issues, lol.  
    #some problems here when we use overlays like "Concert Guitar" or "Strings"
    #sometimes the midi msg of 21 or pause etc occurs twice or inadvertently

    inputs = mido.get_input_names()
    print(mido.get_input_names())
    outputs = mido.get_output_names()
    print(mido.get_output_names())

    #Portable Grand-1 2
    output = mido.open_output(outputs[2])
    mk = mykeys.MyKeys(config.cfg)
    keyboard = Controller()    
    with mido.open_input(inputs[1]) as inport:
        print("hello")
        for msg in inport:
#            print(msg)
#            print(msg.time)
            ignorelast = False
            if msg and hasattr(msg, 'channel') and msg.channel < 8: #0, 1, 2 for input from user.  #others for feedback.  
                
                if hasattr(msg, 'time'):
                    temptime = time.time() #msg.time #time.time() #msg.time
                if hasattr(msg, 'note') and msg.channel==0:
                    #is just the note enough.  Extra complexity by passing other variables.  
                    #lets just pass them and then figure out later if we want to use.  
                    #how to get the note length?  This is what we may want.  
                    mk.key(msg.note, msg)
                
                #here we need to set up a on/off keymap like with analyze image creation.  
                #need an include file here.  
                #master keycontrol and then one for each function.  
                if hasattr(msg, 'note') and msg.channel == 0: #for now this is a workaround to only use channel 0 as control.  
                    #oh yeah I dont think this has the time.  
                    #tried to adjust midi settings on the device.  See if we can get the time transmitted.  
                    #config.keymap.global.Unpause
                    #we can use set(mk.getSequence(2) if order is not significant.  
                    twonotes = mk.getSequence(2)
                    print(twonotes)
                    if twonotes == config.cfg['keymap']['global']['ShowScreen']:
                    #if msg.note==105:
                        #adding two more controllers on piano.  
                        keyboard.press(Key.ctrl)
                        keyboard.press(Key.shift)
                        keyboard.press('5')
                        time.sleep(0.25)
                        keyboard.release('5')
                        keyboard.release(Key.ctrl)
                        keyboard.release(Key.shift)
                        print("Showing Screen" + str(time.time()))
                        ignorelast = True
                    if twonotes ==config.cfg['keymap']['global']['HideScreen']:
                    #if msg.note==106:
                        #adding two more controllers on piano to show screen and hide screen.   
                        keyboard.press(Key.ctrl)
                        keyboard.press(Key.shift)
                        keyboard.press('6')
                        time.sleep(0.25)
                        keyboard.release('6')
                        keyboard.release(Key.ctrl)
                        keyboard.release(Key.shift)
                        print("Hiding Screen" + str(time.time()))
                        ignorelast = True

                    if lastnote ==config.cfg['keymap']['global']['Start'] and msg.note !=lastnote and not ignorelast:
                    #if lastnote == 21 and msg.note !=lastnote and not ignorelast:
                        #1st
#                        mytime = time.time() - starttime - delay
                        mytime = temptime - starttime - delay
                        mins = math.floor(mytime/60)
                        secs = math.floor(mytime - mins*60)
                        filler = ""
                        if secs < 10:
                            filler = "0"
                        args.description += "\nTRIAL#1"
                        args.description += " (" + str(mins) + ":" + filler + str(secs) + ")"
                        
                    if msg.note == config.cfg['keymap']['global']['Pause'] and msg.note !=lastnote and not ignorelast:
                    #if msg.note == 107 and msg.note !=lastnote and not ignorelast:
                        pausestart.append(time.time())

                        keyboard.press(Key.ctrl)
                        keyboard.press(Key.shift)
                        keyboard.press('8')
                        time.sleep(0.25)
                        keyboard.release('8')
                        keyboard.release(Key.ctrl)
                        keyboard.release(Key.shift)
                        print("Pause Recording" + str(time.time()))
                        print(msg.time)
                        #adding END messages.  For now they are only using the pause button as indicator.  
                        iterations = len(pausestart)
                        mytime = temptime - starttime - delay - (temptime - starttime - delay - lasttick)
                        mins = math.floor(mytime/60)
                        secs = math.floor(mytime - mins*60)
                        filler = ""
                        if secs < 10:
                            filler = "0"
                        args.description += "\nEND#" + str(iterations)
                        args.description += " (" + str(mins) + ":" + filler + str(secs) + ")"
                    if msg.note == config.cfg['keymap']['global']['Unpause'] and msg.note !=lastnote and not ignorelast:
                    #if msg.note == 108 and msg.note !=lastnote and not ignorelast:
                        pauseend.append(temptime)
                        delay = calculatedelay(pausestart, pauseend)
                        lasttick = temptime - starttime - delay
                        msg.time = temptime - starttime - delay - lasttick
#                        msg.time = int(round(msg.time*1000))

                        keyboard.press(Key.ctrl)
                        keyboard.press(Key.shift)
                        keyboard.press('9')
                        time.sleep(0.25)
                        keyboard.release('9')
                        keyboard.release(Key.ctrl)
                        keyboard.release(Key.shift)
                        print("Unpause Recording" + str(temptime))

                        print("delay " + str(delay))
                    if lastnote==config.cfg['keymap']['global']['Unpause'] and msg.note !=lastnote and not ignorelast:
                    #if lastnote==108 and msg.note !=lastnote and not ignorelast:
                        #2nd etc.  
                        iterations = len(pauseend) + 1
                        mytime = temptime - starttime - delay
                        mins = math.floor(mytime/60)
                        secs = math.floor(mytime - mins*60)
                        filler = ""
                        if secs < 10:
                            filler = "0"
                        args.description += "\nTRIAL#" + str(iterations)
                        args.description += " (" + str(mins) + ":" + filler + str(secs) + ")"
                    if msg.note == config.cfg['keymap']['global']['Start']:
                    #if msg.note == 21:

                        keyboard.press(Key.ctrl)
                        keyboard.press(Key.shift)
                        keyboard.press('1')
                        time.sleep(0.25)
                        keyboard.release('1')
                        keyboard.release(Key.ctrl)
                        keyboard.release(Key.shift)
                        print("Start Recording" + str(temptime))
                        starttime = temptime
                        msg.time = 0
                    if msg.note == config.cfg['keymap']['global']['Stop']:
                    #if msg.note == 22:
                        endtime = temptime

                        keyboard.press(Key.ctrl)
                        keyboard.press(Key.shift)
                        keyboard.press('2')
                        time.sleep(0.25)
                        keyboard.release('2')
                        keyboard.release(Key.ctrl)
                        keyboard.release(Key.shift)
                        print("Stop Recording" + str(temptime))
                        break
                        
                    if not ignorelast:
                        lastnote = msg.note
                    
                if hasattr(msg, 'time') and not ignorelast:
#                    msg.time = time.time()-starttime-delay
#                    msg.time = faketime
#                    faketime = faketime +1
                    msg.time = temptime - starttime - delay - lasttick
                    msg.time = int(round(msg.time*1000))
                    if msg.time < 0:
                        msg.time = 0
                    
                    lasttick = temptime - starttime - delay
                else:
                    #control track. 
                    
                    msg.time = temptime - starttime - delay - controltick #absolutetime                    
                    msg.time = int(round(msg.time*1000))
                    if msg.time < 0:
                        msg.time = 0
                    controltick = temptime - starttime - delay
                #print(msg) #dont need all this info.  
                if not ignorelast:
                    track.append(msg)
                else:
                    #control track
                    controltrack.append(msg)
                
                if hasattr(msg, 'channel') and hasattr(msg, 'note') and msg.channel == 0:
                    omsg = Message('note_on', note=msg.note, velocity=msg.velocity, time=msg.time)
                    omsg.channel = 8
                    vel = int(omsg.velocity)
                    vel = round(vel*0.25)
                    omsg.velocity = vel
                    omsg.note = omsg.note + 12
                    print(omsg)
                    #output.send(omsg)    
    
    
    databaseURL = config.cfg["firebase"]["fbconfig"]["databaseURL"]
        # Init firebase with your credentials
    creda = credentials.Certificate(config.cfg["firebase"]["credentialsfile"])
    #auth.current_user['localId']
    initialize_app(creda, {'storageBucket': config.cfg["firebase"]["fbconfig"]["storageBucket"], 'databaseURL':databaseURL})    

    latest_file = get_latest_file()    
    args.file = latest_file
    fn = latest_file.split('.')
    mid.save(fn[0] + '.mid')


    #edit the description to match the times which we detected the pauses etc.  
    #for now just upload the video and the midi file.  
    
    
    pathnames = fn[0].split('\\')
    print(pathnames)
    midifile = uploadmidi(fn[0], pathnames[len(pathnames)-1]) #fb bucket upload
    
    
    args.description += '\r\n\r\nLANG:' + mk.getLangs()
    args.description += '\r\n\r\nMIDI:' + midifile
    args.description += '\r\n\r\nKEYWORDS:' + args.keywords #add here like sightread or book, etc.  

    print(args.description)

    #should have some kind of check here.      
    mediafile = uploadmediafile(fn[0], pathnames[len(pathnames)-1] ) #fb bucket upload.  
    args.description += '\r\n\r\nMEDIAFILE:' + mediafile + '\r\n'

    #in case we have difficulty with generating transcript etc.  
    tempfile = open('desc.txt', 'w')
    tempfile.write(args.description)
    tempfile.close()
    print(latest_file)

    #move to external service, can we still add the link?  
    #lets just put this into the DB I think.  That makes our life easier.  
    #to start we are going to use text anyway.  This is 1KB or so per video, nothing.  
#    transcribe_me(latest_file)

    localserver = config.cfg['localserver']['host'] + ":" + str(config.cfg['localserver']['port'])
    transcript = transcribe_me2(args.description, latest_file, mediafile, localserver, myid) #use myid as we havent uploaded yet.  

    if transcript is not None:
      transcribe_file = uploadtranscript(fn[0], pathnames[len(pathnames)-1])
    else:
      transcribe_file = "error"

    args.description += '\r\n\r\nTRANSCRIPT:' + transcribe_file + '\r\n'

    print(args.description)
    
    tempfile = open('desc.txt', 'w')
    tempfile.write(args.description)
    tempfile.close()
    

    if (config.cfg['youtube']['enabled'] == "true"):
        print("Authentication with Youtube")
        youtube = get_authenticated_service(args)
        videoid = initialize_upload(youtube, args)
        add_video_to_playlist(videoid, cred.MY_PLAYLIST, args)
    else:
        videoid = myid 

    addtodb(videoid, args)


#upload to peertube (Need Node)
#default upload both, option to turn off.  
    #sudo npm install -g @peertube/peertube-cli
#peertube-cli upload -u "peertube.misterrubato.com:3000" -U petunia -p Passw0rd -n "Start Peertube thinking" -d "Start Peertube thinking" --file "/mnt/c/Users/Devin/Videos/2024-01-17 23-53-52.mkv"
    #perhaps should make server in between.  And then this can change as need be.  
    #makybe no reason to reconfigure peertube for instance.  Can just serve as need be.  

#    print('peertube-cli upload -u "' + config.cfg['peertube']['host'] + ':' + str(config.cfg['peertube']['port']) + '" -U ' + config.cfg['peertube']['ADMIN_USERID'] + ' -p ' + config.cfg['peertube']['ADMIN_PASSWORD'] + ' -n "' + args.title + '" -d "' + args.description + '" --file "' + latest_file + '"')
#    subprocess.call('peertube-cli upload -u ' + config.cfg['peertube']['host'] + ':' + config.cfg['peertube']['port'] + ' -U ' + config.cfg['peertube']['ADMIN_USERID'] + ' -p ' + config.cfg['peertube']['ADMIN_PASSWORD'] + ' -n "' + args.title + '" -d "' + args.description + '" --file "' + latest_file + '"')
#call again to run the any post-analysis like finger locations.  
    subprocess.call('python ./analyze/analyze.py --title "' + args.title + '"')
    
    time.sleep(20)
    obsp.terminate()

    
    #cant automate this, as it will become public.  
#   if (len(transcribe_file) > 500):
#       add_video_to_playlist(videoid, cred.WORD_PLAYLIST, args)
