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


#!/usr/bin/python
#getting stuff for image processing.  
#pip install opencv-python

#pip install mido
#pip install rtmidi
#pip install py-midi
#pip install python-rtmidi
#install vc++ redistributable.  

#pip install pydrive

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

import sys
sys.path.insert(0, 'c:/devinpiano/')
 
 
import cred





from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


from transcribe import transcribe_me, get_timestamp


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
CLIENT_SECRETS_FILE = "./../client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

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
    message=MISSING_CLIENT_SECRETS_MESSAGE)
  

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()
  #this local storage of creds was causing problems.  Finally this works now to add to the playlist.  
#  credentials = None
  if credentials is None or credentials.invalid:
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
  
def uploadtranscript(file, title):
    from firebase_admin import credentials, initialize_app, storage
    # Init firebase with your credentials
    cred = credentials.Certificate("../misterrubato-test.json")
    initialize_app(cred, {'storageBucket': 'misterrubato-test.appspot.com'}, name="second")

    # Put your local file path 
    Title = title + '.txt'
    fileName = file + '.txt'
    bucket = storage.bucket()
    blob = bucket.blob('words/' + Title)
    blob.upload_from_filename(fileName)

    # Opt : if you want to make public access from the URL
    blob.make_public()

    print("your transcript file url", blob.public_url)
    return blob.public_url

def uploadmidi(file, title):
    from firebase_admin import credentials, initialize_app, storage
    # Init firebase with your credentials
    cred = credentials.Certificate("../misterrubato-test.json")
    initialize_app(cred, {'storageBucket': 'misterrubato-test.appspot.com'})

    # Put your local file path 
    Title = title + '.mid'
    fileName = file + '.mid'
    bucket = storage.bucket()
    blob = bucket.blob('midi/' + Title)
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
        "playlistId": cred.MY_PLAYLIST,
        "position": 0,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": "7Aadr9Fmftk"
        }
      }
    }
    )
    response = request.execute()
    
    
if __name__ == '__main__':

    argparser.add_argument("--file", required=False, help="Video file to upload")
    argparser.add_argument("--title", help="Video title", default="New Upload")
    argparser.add_argument("--description", help="Video description",
      default="New Upload")
    argparser.add_argument("--category", default="10",
      help="Numeric video category. " +
        "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",
      default="music,learning,experiment")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
      default=VALID_PRIVACY_STATUSES[2], help="Video privacy status.")
    args = argparser.parse_args()
    if (args.title == "New Upload"):
        args.title = args.description
    print(cred.MY_PLAYLIST)
    add_video_to_playlist('7Aadr9Fmftk', cred.MY_PLAYLIST, args)

#    mido.set_backend('mido.backends.portmidi')   
    mid = MidiFile()
#    mid.ticks_per_beat = 1000000
#    mid.tempo = 60
    track = MidiTrack()
#    track.append(MetaMessage('set_tempo', tempo=100000, time=0))
    mid.tracks.append(track)
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
    inputs = mido.get_input_names()
    print(mido.get_input_names())
    
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
    #mido doc is crap.  But this seems ok for now.  
    #the video and midi appear to match up pretty well.  But not perfect I think.  
    #at least enough to get the start times now.  
    with mido.open_input(inputs[1]) as inport:
        for msg in inport:
            if msg:
                if hasattr(msg, 'note'):
                    if lastnote == 21 and msg.note !=lastnote:
                        #1st
                        mytime = time.time() - starttime - delay
                        mins = math.floor(mytime/60)
                        secs = math.floor(mytime - mins*60)
                        filler = ""
                        if secs < 10:
                            filler = "0"
                        args.description += "\nTRIAL#1"
                        args.description += " (" + str(mins) + ":" + filler + str(secs) + ")"
                    if lastnote==107 and msg.note !=lastnote:
                        #adding END messages.  For now they are only using the pause button as indicator.  
                        iterations = len(pausestart)
                        mytime = time.time() - starttime - delay - (time.time() - starttime - delay - lasttick)
                        mins = math.floor(mytime/60)
                        secs = math.floor(mytime - mins*60)
                        filler = ""
                        if secs < 10:
                            filler = "0"
                        args.description += "\nEND#" + str(iterations)
                        args.description += " (" + str(mins) + ":" + filler + str(secs) + ")"
                    if lastnote==108 and msg.note !=lastnote:
                        #2nd etc.  
                        iterations = len(pauseend) + 1
                        mytime = time.time() - starttime - delay
                        mins = math.floor(mytime/60)
                        secs = math.floor(mytime - mins*60)
                        filler = ""
                        if secs < 10:
                            filler = "0"
                        args.description += "\nTRIAL#" + str(iterations)
                        args.description += " (" + str(mins) + ":" + filler + str(secs) + ")"
                    if msg.note == 21:
                        starttime = time.time()
                        msg.time = 0
                    if msg.note == 22:
                        endtime = time.time()
                        break
                    if msg.note == 107 and msg.note !=lastnote:
                        pausestart.append(time.time())
                        print(msg.time)
                    if msg.note == 108 and msg.note !=lastnote:
                        pauseend.append(time.time())
                        delay = calculatedelay(pausestart, pauseend)
                        lasttick = time.time() - starttime - delay
                        msg.time = time.time() - starttime - delay - lasttick
                        msg.time = int(round(msg.time*1000))
                        print("delay " + str(delay))
                    lastnote = msg.note
                    
                if hasattr(msg, 'time'):
#                    msg.time = time.time()-starttime-delay
#                    msg.time = faketime
#                    faketime = faketime +1
                    msg.time = time.time() - starttime - delay - lasttick
                    msg.time = int(round(msg.time*1000))
                    if msg.time < 0:
                        msg.time = 0
                    
                    lasttick = time.time() - starttime - delay

                #print(msg) #dont need all this info.  
                track.append(msg)
                
    list_of_files = glob.glob('C:/Users/devin/Videos/*.mkv') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    args.file = latest_file
    fn = latest_file.split('.')
    mid.save(fn[0] + '.mid')


    #edit the description to match the times which we detected the pauses etc.  
    #for now just upload the video and the midi file.  
    
    
    pathnames = fn[0].split('\\')
    print(pathnames)
    midifile = uploadmidi(fn[0], pathnames[len(pathnames)-1])
    
    
    
    args.description += '\r\n\r\nMIDI:' + midifile
    args.description += '\r\n\r\nKEYWORDS:' + args.keywords #add here like sightread or book, etc.  

    print(args.description)
    
    transcribe_me(latest_file)
    transcribe_file = uploadtranscript(fn[0], pathnames[len(pathnames)-1])
    args.description += '\r\n\r\nTRANSCRIPT:' + transcribe_file
    print(args.description)
    youtube = get_authenticated_service(args)
    videoid = initialize_upload(youtube, args)
    
    add_video_to_playlist(videoid, cred.MY_PLAYLIST, args)
