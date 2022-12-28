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





from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


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
    


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

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

  resumable_upload(insert_request)

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


def uploadmidi(file, title):
    from pydrive.drive import GoogleDrive
    from pydrive.auth import GoogleAuth
    # Below code does the authentication
    # part of the code
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(CLIENT_SECRETS_FILE)
    # Creates local webserver and auto
    # handles authentication.
#    gauth.LocalWebserverAuth()       
    drive = GoogleDrive(gauth)
       
    f = drive.CreateFile({'title': title})
    f.SetContentFile(os.path.join(file, x))
    f.Upload()
    #cleanup
    f = None

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
      default=VALID_PRIVACY_STATUSES[1], help="Video privacy status.")
    args = argparser.parse_args()


#    mido.set_backend('mido.backends.portmidi')   
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    inputs = mido.get_input_names()
    print(mido.get_input_names()) 
    with mido.open_input(inputs[1]) as inport:
        for msg in inport:
            if msg:
                print(msg)
                track.append(msg)
                if hasattr(msg, 'note') and msg.note == 22:
                    break
    list_of_files = glob.glob('C:/Users/devin/Videos/*.mkv') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    args.file = latest_file
    fn = latest_file.split('.')
    mid.save(fn[0] + '.mid')


    #edit the description to match the times which we detected the pauses etc.  
    #for now just upload the video and the midi file.  
    
    youtube = get_authenticated_service(args)
    initialize_upload(youtube, args)
    
    pathnames = fn[0].split('/')
    uploadmidi(fn[0] + '.mid', pathnames[len(pathnames)-1])