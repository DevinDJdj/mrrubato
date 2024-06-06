#take input of tennis match audio, and use the timings which occur and separate the sounds of the 
#ball hitting the racket, the players footsteps, the type of shot, and the applause.  
#every distinct type of act should be identified and a sound timbre should be created for each.
#represent the tennis match in a midi file, and compose a piece of music based on the match.  
#Group by each player, and create a life track for each player in sequence of matches played.  
#or perhaps also create some combination of multiple matches played.  
#or by player/location etc.  
#maxsimultaneous = 4?  
#work with each player to choose ball striking sound etc.  

#test with this https://www.youtube.com/@WTA/playlists
#https://www.youtube.com/@tennistv/playlists


#https://shiqiang.wang/papers/AB_MMSports2019.pdf
#https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=888c823137434f4ebb85083bcb20f7a2ed486d36
#https://medium.com/@kosolapov.aetp/tennis-analysis-using-deep-learning-and-machine-learning-a5a74db7e2ee
#tennis ball/player detection
#https://github.com/yastrebksv/TennisProject
#https://github.com/ArtLabss/tennis-tracking
#this looks a bit better.  

#https://www.youtube.com/watch?v=L23oIHZE14w
#audio event detection
#https://github.com/amsehili/auditok


###start here###
#full match playlist:
#WTA
#https://www.youtube.com/playlist?list=PLhQBpwasxUpldXpIymjy_FeQrax9qXGNT
#https://www.youtube.com/playlist?list=PL_2A0MxHOgdaYmi__7UiR8HQqkPaGdmqr

#USOPEN
#https://www.youtube.com/watch?v=HCIhFyeQxu0&list=PL_2A0MxHOgdYzDdqZaYu4nQ6jdl95rKvK
#https://www.youtube.com/watch?v=RzEw4pTdLEU&list=PL_2A0MxHOgdY7HQMncvHtHLoE4PtMBnFy
#classic matches
#https://www.youtube.com/watch?v=DCzT_AmY0HY&list=PL_2A0MxHOgdZxZ3vK104p51lFOFVsEgrR

#AUOPEN
#https://www.youtube.com/watch?v=HgN6t1-JhDs&list=PL2RR--XMozwUbAdvjCLuhe4Cuqgfv6X1U
#https://www.youtube.com/watch?v=q7b-fcV1Q-4&list=PL2RR--XMozwUKlrwbxNPUQAW-SU8AJvI_
#https://www.youtube.com/watch?v=6I06-ITW88k&list=PL2RR--XMozwUsQ8ieTUc-0VkWdKpzV4mK



#ROLAND GARROS
#no full playlist
#https://www.youtube.com/c/rolandgarros

#WIMBLEDON
#no full playlist
#https://www.youtube.com/@Wimbledon/playlists


#download all videos and create some structure for Player and location etc.  
#use audio event detection to get events.  
#how do we categorize events?  
#https://github.com/karolpiczak/ESC-50?tab=readme-ov-file
#use this?  
#try this:
##start here##
#https://medium.com/@ujjawalshah1080/using-deep-learning-for-audio-classification-of-urban8k-dataset-based-on-the-mel-frequency-cepstral-7cc52f55a97
#do this for tennis events which were extracted.  
#extract events from one or two matches from each playlist similar to below.  

#or this?  Hmmm...
#pip install soundata
#ENV musicgen


#https://github.com/amsehili/auditok
#use this perhaps to split the audio into events and add them to the csv as new categories or whatever structure we need to add it to.  
#then categorize them.  Tennis events shouldnt be too many.  
#grunt_hit
CAT_SIMPLE = ['ball_hit', 'ball_bounce', 'footsteps', 'applause', 'grunt_hit', 'voice']
#CATEGORIES = ['ball_hit_top', 'ball_hit_slice', 'ball_hit_overhead', 'footsteps', 'ball_bounce', 'applause', 'volley', 'drop_shot', 
              
#CAT_SCORE = ['fault', 'out', 'let', 'game', 'set', 'match', 
#              '0_15', '0_30', '0_40', '15_0', '15_15', '15_30', '15_40', '30_0', '30_15', '30_30', '30_40', '40_0', '40_15', '40_30', '40_40', 
#              'DEUCE', 'AD_IN', 'AD_OUT' ]
test = """
import soundata

dataset = soundata.initialize('urbansound8k', data_home='c:\\devinpiano\\test\\urbansound')
dataset.download()  # download the dataset
dataset.validate()  # validate that all the expected files are there

example_clip = dataset.choice_clip()  # choose a random example clip
print(example_clip)  # see the available data

"""

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
sys.path.insert(0, 'c:/devinpiano/music/')

import config 

import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile

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

def get_audio_map(videoid, mediafile=None, playlist=None, args=None):
    #download all audio files from playlist.  
    if playlist != None:
        #download all videos from playlist.  
        #use youtube-dl
        #
        youtube = get_authenticated_service(args) #write it yourself
        res = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist,
        maxResults="50"
        ).execute()

        nextPageToken = res.get('nextPageToken')
        while ('nextPageToken' in res):
            nextPage = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist,
            maxResults="50",
            pageToken=nextPageToken
            ).execute()
            res['items'] = res['items'] + nextPage['items']

            if 'nextPageToken' not in nextPage:
                res.pop('nextPageToken', None)
            else:
                nextPageToken = nextPage['nextPageToken']

        for item in res['items']:
            videoid = item['snippet']['resourceId']['videoId']
            get_audio_map(videoid)

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
    
    command = "ffmpeg -i \"" + latest_file + "\" -ar 22050 -ac 1 output/wavs/" + videoid + ".wav"
    print(command)
    subprocess.call(command, shell=True)

    command = "ffmpeg -i \"" + latest_file + "\" -ar 16000 -ac 1 output/wavs16000/" + videoid + ".wav"
    print(command)
    subprocess.call(command, shell=True)



def get_speech(filename):
    import torch
    torch.set_num_threads(1)

    from IPython.display import Audio
    from pprint import pprint
    # download example
    torch.hub.download_url_to_file('https://models.silero.ai/vad_models/en.wav', 'en_example.wav')

    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                model='silero_vad',
                                force_reload=True)

    (get_speech_timestamps,
    _, read_audio,
    *_) = utils


    sampling_rate = 16000 # also accepts 8000
    wav = read_audio(filename, sampling_rate=sampling_rate)
    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sampling_rate, return_seconds=True)
    pprint(speech_timestamps)
    return speech_timestamps

if __name__ == '__main__':
    argparser.add_argument("--admin", help="Add Admin user", default="")
    args = argparser.parse_args()
#    get_audio_map(playlist='PLhQBpwasxUpldXpIymjy_FeQrax9qXGNT', args=args)
    #mj4jpeBvD2o
    get_audio_map(videoid='5uFAkizQNJI', args=args) #Alcaraz Djokovic Wimbeldon 2023

    #next run #https://github.com/amsehili/auditok or similar to detect events.  
    #save event files to wavs and csv.  
    #from original video wav file, split events into separate files.
    #event.secs.microsecs
    #in metadata save duration, and label (if we think we know)
    #then categorize them with trained .  
    #https://medium.com/@ujjawalshah1080/using-deep-learning-for-audio-classification-of-urban8k-dataset-based-on-the-mel-frequency-cepstral-7cc52f55a97
    #add to category folder once identified.  

    #then when detecting, we can simply use the same strategy to detect audio events.  
    #and then just categorize them with the best existing model.  
    output_directory = "output/wavs/"
    output_directory16000 = "output/wavs16000/"
    event_directory = "output/events/"
    for filename in os.listdir(output_directory):
        f = os.path.join(output_directory, filename)
        f16000 = os.path.join(output_directory16000, filename)
        # checking if it is a file
        if os.path.isfile(f):
            print(f)
            #split the file into events.
#git clone https://github.com/amsehili/auditok.git
#cd auditok
#python setup.py install            
#sudo pip install auditok            
            import auditok

#maybe this will work better?  
#https://github.com/biboamy/TVSM-dataset
            #voice activity detection.  Lets try to get rid of some of the commentary.  
            #python3 sileo-vad.py --input ex_example.wav --output only_speech.wav
#            https://github.com/snakers4/silero-vad
            
            # split returns a generator of AudioRegion objects
            audio_regions = auditok.split(
                f,
                min_dur=0.1,     # minimum duration of a valid audio event in seconds
                max_dur=4,       # maximum duration of an event
                max_silence=0.05, # maximum duration of tolerated continuous silence within an event
                energy_threshold=25 # threshold of detection
            )

            speechtimes = get_speech(f16000) 
            sstart = []
            send = []
            for s in speechtimes:
                sstart.append(s['start'])
                send.append(s['end'])


            currentindex = 0
            for i, r in enumerate(audio_regions):
                while send[currentindex] < r.meta.start and len(send) > currentindex + 1:
                    currentindex += 1
                # Regions returned by `split` have 'start' and 'end' metadata fields
                if (sstart[currentindex] > r.meta.end):
                    print("Region {i}: {r.meta.start:.3f}s -- {r.meta.end:.3f}s".format(i=i, r=r))
                    # play detection
#                    r.play(progress_bar=True)

                    # region's metadata can also be used with the `save` method
                    # (no need to explicitly specify region's object and `format` arguments)

                    filename = r.save(event_directory + "{r.meta.start:.3f}.wav".format(r=r))

                    print("region saved as: {}".format(filename))
                    sample_rate, samples = wavfile.read(filename)
                    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)

                    plt.pcolormesh(times, frequencies, spectrogram)
                    plt.imshow(spectrogram)
                    plt.ylabel('Frequency [Hz]')
                    plt.xlabel('Time [sec]')
                    plt.savefig(event_directory + "{r.meta.start:.3f}.png".format(r=r))

                    #look for peaks in each wav file.  
                    #separate the events on peaks from the spectrograms.  
                    #pass divided wav for analysis to categorize.  
                    #for now see if we can get all the peaks and save them in a more useful fashion.  
                    #change auditok?  or start new?  https://github.com/madhavlab/wav2tok
                    #then categorize them.  
                    #use only short wav files to identify categories.  
                    #we can categorize the sound after enhancing the urban8k dataset.

#                print("Region {i}: {r.meta.start:.3f}s -- {r.meta.end:.3f}s".format(i=i, r=r))

                # play detection
                # r.play(progress_bar=True)

                # region's metadata can also be used with the `save` method
                # (no need to explicitly specify region's object and `format` arguments)

#                filename = r.save(event_directory + "region_{meta.start:.3f}.wav")
#                print("region saved as: {}".format(filename))

