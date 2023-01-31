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
import random
import sys
import time
import cv2
import pytesseract
from PIL import Image
import numpy as np
import string


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


#for now just see what frames I am playing and then convert that to time.  
#any time that my hand is on the piano, we count as playing.  
#anything longer than 5 seconds with no hands on piano is not playing.  

#get the names of songs from here.  
#https://nanonets.com/blog/ocr-with-tesseract/
#install tesseract.  
#pip install pytesseract
#https://github.com/UB-Mannheim/tesseract/wiki


def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result
  
  
def video_to_frames(input_loc, output_loc):
    """Function to extract frames from input video file
    and save them as separate frames in an output directory.
    Args:
        input_loc: Input video file.
        output_loc: Output directory to save the frames.
    Returns:
        None
    """
    try:
        os.mkdir(output_loc)
    except OSError:
        pass
    # Log the time
    time_start = time.time()
    # Start capturing the feed
    cap = cv2.VideoCapture(input_loc)
    # Find the number of frames
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print ("Number of frames: ", video_length)
    count = 0
    print ("Converting video..\n")
    # Start converting the video
    
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    # Example tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    while cap.isOpened():
        # Extract the frame
        ret, frame = cap.read()
        if not ret:
            continue
        # Write the results back to output location.
        count = count + 1
        if count%30==0:
            frame = rotate_image(frame, -10)
            #title FRAME for most things I guess.  
            frame = frame[200:300, 100:1200]
            
            cv2.imwrite(output_loc + "/%#05d.jpg" % (count+1), frame)
            print(pytesseract.image_to_string(frame))
            # If there are no more frames left
            if (count > (video_length-1)):
                # Log the time again
                time_end = time.time()
                # Release the feed
                cap.release()
                # Print stats
                print ("Done extracting frames.\n%d frames extracted" % count)
                print ("It took %d seconds forconversion." % (time_end-time_start))
                break
            
            
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



def msg2dict(msg):
    result = dict()
    if 'note_on' in msg:
        on_ = True
    elif 'note_off' in msg:
        on_ = False
    else:
        on_ = None
    result['time'] = int(msg[msg.rfind('time'):].split(' ')[0].split('=')[1].translate(
        str.maketrans({a: None for a in string.punctuation})))

    if on_ is not None:
        for k in ['note', 'velocity']:
            result[k] = int(msg[msg.rfind(k):].split(' ')[0].split('=')[1].translate(
                str.maketrans({a: None for a in string.punctuation})))
    return [result, on_]

def switch_note(last_state, note, velocity, on_=True):
    # piano has 88 notes, corresponding to note id 21 to 108, any note out of this range will be ignored
    result = [0] * 88 if last_state is None else last_state.copy()
    if 21 <= note <= 108:
        result[note-21] = velocity if on_ else 0
    return result


def get_new_state(new_msg, last_state):
    new_msg, on_ = msg2dict(str(new_msg))
    new_state = switch_note(last_state, note=new_msg['note'], velocity=new_msg['velocity'], on_=on_) if on_ is not None else last_state
    return [new_state, new_msg['time']]
    
def track2seq(track):
    # piano has 88 notes, corresponding to note id 21 to 108, any note out of the id range will be ignored
    result = []
    last_state, last_time = get_new_state(str(track[0]), [0]*88)
    for i in range(1, len(track)):
        new_state, new_time = get_new_state(track[i], last_state)
        if new_time > 0:
            result += [last_state]*new_time
        last_state, last_time = new_state, new_time
    return result

def mid2arry(mid, min_msg_pct=0.1):
    tracks_len = [len(tr) for tr in mid.tracks]
    min_n_msg = max(tracks_len) * min_msg_pct
    # convert each track to nested list
    all_arys = []
    for i in range(len(mid.tracks)):
        if len(mid.tracks[i]) > min_n_msg:
            ary_i = track2seq(mid.tracks[i])
            all_arys.append(ary_i)
    # make all nested list the same length
    max_len = max([len(ary) for ary in all_arys])
    for i in range(len(all_arys)):
        if len(all_arys[i]) < max_len:
            all_arys[i] += [[0] * 88] * (max_len - len(all_arys[i]))
    all_arys = np.array(all_arys)
    all_arys = all_arys.max(axis=0)
    # trim: remove consecutive 0s in the beginning and at the end
    sums = all_arys.sum(axis=1)
    ends = np.where(sums > 0)[0]
    return all_arys[min(ends): max(ends)]


def getmidikey(result_array, key=0):
    r = []
    on = False
    onframe = 0
    for i in range(result_array.shape[0]):
#        print(result_array[i][0])
        if (result_array[i][key] != 0):
            on = True
            onframe = i
        else:
            if on:
                r.append(i)
                on = False
    
    if on:
        r.append(i)
        on = False
    return r

def getstarttime(result_array, start):
    i = start
    while i < result_array.shape[0]:
        i = i+1
        for k in result_array[i]:
            if k != 0:
                return i
    
def getendtime(result_array, end):
    i = end-1
    while i > 0:
        i = i-1
        for k in result_array[i]:
            if k != 0:
                return i

def readmidi(f):
    import mido
    exta = f.rfind('.')
    f = f[0:exta]
    mid = mido.MidiFile(f + '.mid', clip=True)
    for m in mid.tracks[1][0:20]:
        print(m)
        
    result_array = mid2arry(mid)
    
    print(result_array.shape)
    
    start = getmidikey(result_array, 0)
    end = getmidikey(result_array, 1)
    pause = getmidikey(result_array, 86)
    unpause = getmidikey(result_array, 87)
    print(pause)
    print(unpause)
    if (len(pause) != len(unpause)):
        print("Pause Problems")
        
    print(getstarttime(result_array, start[0]))
    for idx,p in enumerate(pause):
        print(getendtime(result_array, p))
        print(getstarttime(result_array, unpause[idx]))
    
    print(getendtime(result_array, end[0]))
    

    
#    import matplotlib.pyplot as plt
#    plt.plot(range(result_array.shape[0]), np.multiply(np.where(result_array>0, 1, 0), range(1, 89)), marker='.', markersize=1, linestyle='')
#    plt.title(f)
#    plt.show()
        


    
if __name__ == '__main__':
  argparser.add_argument("--file", required=True, help="Video file to upload")
  argparser.add_argument("--title", help="Video title", default="Test Title")
  argparser.add_argument("--description", help="Video description",
    default="Test Description")
  argparser.add_argument("--category", default="22",
    help="Numeric video category. " +
      "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
  argparser.add_argument("--keywords", help="Video keywords, comma separated",
    default="")
  argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
    default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
  args = argparser.parse_args()

  if not os.path.exists(args.file):
    exit("Please specify a valid file using the --file= parameter.")

  head, tail = os.path.split(args.file)
  #here also 
  #gettitle (maybe skip for now)
  f,m = tail.split('.')
  print(f)
  readmidi(args.file)
  #get iterations
  #upload
  #video_to_frames(args.file, "./output/test/")
  youtube = get_authenticated_service(args)
  try:
    a = 2
#    initialize_upload(youtube, args)
  except HttpError as e:
    print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))