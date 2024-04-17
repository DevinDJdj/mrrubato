#pip install noisereduce

import wave
import json
from pydub import AudioSegment
from os import path
import subprocess
import glob
import os
import sys
import math
import pandas as pd
from datetime import datetime
import urllib.request

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from pytube import YouTube


from oauth2client.tools import argparser, run_flow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import firebase_admin
from firebase_admin import db
from firebase_admin import firestore

from firebase_admin import credentials
from firebase_admin import initialize_app, storage, auth

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload

import httplib2 
# adding Folder_2/subfolder to the system path
sys.path.insert(0, 'c:/devinpiano/')

import config 

CLIENT_SECRETS_FILE = "./../client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl" #needed for comments, does this work?  
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


def reduce_noise(f):
    from scipy.io import wavfile
    import noisereduce as nr
    # load data
    rate, data = wavfile.read(f)
    # perform noise reduction
    reduced_noise = nr.reduce_noise(y=data, sr=rate)
    wavfile.write(f, rate, reduced_noise)


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

def get_audio_file(videoid, mediafile=None, args=None):
    #download all audio files from playlist.  

    if mediafile != None and mediafile != "":
        #should work with this.  
        #see if transcribe is working still after update.  
        urllib.request.urlretrieve(mediafile, "output/" + videoid + "/" + videoid + ".mp4")
    else:
        youtube_video_url = "https://www.youtube.com/watch?v=" + videoid
        youtube_video_content = YouTube(youtube_video_url)

        for stream in youtube_video_content.streams:
            print(stream)

        audio_streams = youtube_video_content.streams.filter(only_audio = True)
        for stream in audio_streams:
            print(stream)

        audio_stream = audio_streams[1]
        print(audio_stream)

        audio_stream.download("output/" + videoid)

    list_of_files = glob.glob('output/' + videoid + '/*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    
    output_dir = "output/reduce/"
    command = "ffmpeg -i \"" + latest_file + "\" -ar 22050 -ac 1 " + output_dir + videoid + ".wav"
    print(command)
    subprocess.call(command, shell=True)

    reduce_noise(output_dir + videoid + ".wav")

#    command = "ffmpeg -i \"" + latest_file + "\" -ar 16000 -ac 1 output/wavs16000/" + videoid + ".wav"
#    print(command)
#    subprocess.call(command, shell=True)



if __name__ == '__main__':
    argparser.add_argument("--admin", help="Add Admin user", default="")
    args = argparser.parse_args()
#    get_audio_map(playlist='PLhQBpwasxUpldXpIymjy_FeQrax9qXGNT', args=args)
    #mj4jpeBvD2o
    get_audio_file(videoid='0kvXEzw3GSI', args=args)

