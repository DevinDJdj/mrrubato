#get videos and create a DB of Data about all played.  
#link, title, GroupName, Published date, Iteration#, PlayedInSeconds, #notesplayed-calculated
#for now just generate a csv file.  
#dont download the videos, just get the written description
#on login failure, change status/privacyStatus -> unlisted, remove playlist data.  

#notesplayed


import sys
import os
import httplib2 
# adding Folder_2/subfolder to the system path
sys.path.insert(0, 'c:/devinpiano/')
 
import config 
#import cred
#import record
import util

import subprocess

import pandas as pd
import requests
import json
import re
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


#from transcribe import transcribe_fromyoutube
#import whisper


CLIENT_SECRETS_FILE = config.cfg['youtube']['CLIENT_SECRETS_FILE']

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


TIME_WINDOW = 9

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=[YOUTUBE_UPLOAD_SCOPE],
           #, "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/plus.me"],
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("../%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)
 
 # r = requests.get("https://www.googleapis.com/oauth2/v3/userinfo",
 #               headers = {"Authorization": "Bearer " + credentials.access_token})

#  data = r.json()
#  print(data)

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
    if playlistID == "":
        return
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
    ref = db.reference(f'/')

    # Get the backup path
    backup_path = "c:/devinpiano/backup/db/"

    # Take the backup
    today = date. today()
    today = today. strftime("%Y%m%d")
    
    with open(backup_path + today + '.json', 'w', encoding="utf-8") as f:
        json.dump(ref.get(), f)
        

    ref = db.reference(f'/misterrubato/')
    snapshot = ref.order_by_child('snippet/publishedAt').get()
    return snapshot.items()
#    return ref.items()


def getPlaylistFromGrade(grade):
    if grade == "test":
        return ""
    if int(grade) > 8:
        return config.cfg['youtube']['GREAT_PLAYLIST']
    elif int(grade) > 4:
        return config.cfg['youtube']['GOOD_PLAYLIST']
    elif int(grade) == 0:
        return ""
    else:
        return config.cfg['youtube']['OK_PLAYLIST']
        
        
def getCodeHistory():
#this should be a parameter.  
#similar functionality can be used in other ways.  
#where do we store this?  
#dont, just do this on the front-end.  
  try:
    url = 'https://api.github.com/repos/DevinDJdj/mrrubato/commits?sha=master'
    r = requests.get(url)
    arr = r.json()
    i = 0
    limit = 100
    for e in arr[:limit]:
        print(e['url'])
        print(e['html_url']) #this is the link we want to use in UI somewhere.  
        stats = requests.get(e['url']).json()
        print(stats['stats'])
        for f in stats['files']:
            print(f['filename'])
            print(f['changes'])
            #f['blob_url'
#    return r.json()    
  except Exception as e:
    print(e)
        

def getWatched():
    #add the description from youtube so that we have this info for UI.  
    ref = db.reference(f'/watch')
    #snapshot = ref.get()
    snapshot = ref.order_by_child('snippet/addedAt').get()  #this doesnt accept null values.  
    ref = snapshot.items()
    
    for key, item in ref:
        if "snippet" not in item:
            url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails\
                &id={key}&key={api_key}'
            json_url = requests.get(url)
            datav = json.loads(json_url.text)
            if (len(datav['items']) > 0):
    #            print(datav)
                
    #            print(datav['items'][0]['snippet']['publishedAt'])
    #            print(datav['items'][0]['snippet']['title'])
    #            print(datav['items'][0]['snippet']['description'])
    #            print(datav['items'][0]['snippet']['thumbnails']['default']['url'])
    #            print(datav['items'][0]['contentDetails']['duration'])
                updRef = db.reference(f'/watch/' + key)
                
                current_datetime = datetime.now()
                current_datetime_string = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
                datav['items'][0]['snippet']['addedAt'] = current_datetime_string
                if "comments" in item: #really this shouldnt occur.  
                #just failed when we first started doing this.  
                    c = item['comments']
                    datav['items'][0]['comments'] = c
                updRef.set(datav['items'][0])

    return snapshot.items()

#https://github.com/youtube/api-samples/blob/master/python/comment_threads.py
#include the original question here if we cant reply directly?  
def insert_comment(youtube, channel_id, video_id, parent_id, text):
  insert_result = youtube.commentThreads().insert(
    part="snippet",
    body=dict(
      snippet=dict(
        channelId=channel_id,
        videoId=video_id,
        topLevelComment=dict(
          snippet=dict(
            parentId=parent_id,
            textOriginal=text
          )
        )
      )
    )
  ).execute()





def massageComment(data):
    final = data["answer"]
    allsources = ""
    for s in data["sources"]:
        vid = util.getVidFromMetadata(s["metadata"])
        allsources += util.makeTimeLinks(s["content"], vid)
        allsources += "<br><br>"

    final += allsources
    return final

def respondtoComments(args):
    youtube = get_authenticated_service(args)
    results = youtube.commentThreads().list(
        part="snippet",
        allThreadsRelatedToChannelId=channel_id,
        textFormat="plainText"
    ).execute()

    #for now just -1 to the port to get ollama.  
    #should be a separate port/server config.  
    localserver = config.cfg['localserver']['host'] + ":" + str(config.cfg['localserver']['port']-1)
    qas = []
    servererrorcnt = 0
    for item in results["items"]:
#        threadid = item["id"]
        comment = item["snippet"]["topLevelComment"]
        numreplies = item["snippet"]["totalReplyCount"]
        if numreplies < 1 and servererrorcnt < 3: #dont keep banging on the door when server is down.
            vidid = item["snippet"]["videoId"]
            commentid = comment["id"]
            author = comment["snippet"]["authorDisplayName"] #cant get userID
            authorchannel = comment["snippet"]["authorChannelId"]["value"] #is this better than displayname?  
            text = comment["snippet"]["textDisplay"]
            print("Comment by %s: %s" % (author, text))

            url = f'{localserver}/api/?query={text}&userid={author}'
            print(url)
            try:
                #ease the pain of SSL certificates.  
                res = requests.get(url, timeout=(120, None), verify = False).text
    #            print(res)
    #            if (res is not None):
                data = json.loads(res)
                print(data["answer"])
                mycomment = massageComment(data)
                print(mycomment)
                #dont need anything where we have no comment
                #for the foreseeable future this may less than optimal garbage.  
                if ("sources" in data and len(data["sources"]) > 0):
                    qas.append({"author": author, "authorchannel": authorchannel, "question": text, "answer": mycomment, "prompt": "" })
#                insert_comment(youtube, channel_id, vidid, commentid, mycomment)
            except Exception as e:
                print('error using ollama ' + vidid + ' ' + str(e))
                servererrorcnt += 1

    if (len(qas) > 0):
        today = date. today()
        today = today. strftime("%Y%m%d")
        RSS_FOLDER = "rss/data/" #probably should be config.  But is is necessary?  
        with open(RSS_FOLDER + today + ".json", "w") as f:
            json.dump(qas, f)

        print('rss gen python ./rss/gen.py --d ' + today)
        subprocess.call('python ./rss/gen.py --d ' + today)
        print("rss gen complete")


def addAdmins(uid):
    auth.set_custom_user_claims(uid, {'admin': True})

def checkAdmins():

    ref = db.reference(f'/users')
    snapshot = ref.get()  
    for key, item in snapshot.items():
    
        # Lookup the user associated with the specified uid.
        user = auth.get_user(key)
        # The claims can be accessed on the user record.
        print(key + " " + item['name'] + str(user.custom_claims.get('admin')))
    


def updatetranscript(vidid, updated, transcript):
 
    # Put your local file path 
    Title = vidid + '.txt'
    fileName = updated + '.txt'
    with open('../words/' + fileName, 'w', encoding="utf-8") as f:
        f.write(transcript)

    bucket = storage.bucket()
    blob = bucket.blob('words/' + updated[0:4] + '/' + Title)
    blob.upload_from_filename('../words/' + fileName)

    # Opt : if you want to make public access from the URL
    blob.make_public()

    print("your new transcript file url", blob.public_url)
    return blob.public_url
	

def calctimes(starttimes, endtimes):
    #calculate from timestamps
    timewithoutplaying = 0
    timewithplaying = 0
    lasttime = 0
    for s, e in zip(starttimes, endtimes):
        timewithoutplaying += util.getSecsFromTime(s) - lasttime
        lasttime = util.getSecsFromTime(e)
        timewithplaying += lasttime - util.getSecsFromTime(s)
    return timewithplaying, timewithoutplaying
    
def updatestatsdb(videoid, starttimes, endtimes, midisize, numwords):
#this should already exist from analyze.py 
#    timeplaying, timewithoutplaying = calctimes(starttimes, endtimes)
    #insert into DB
    ref = db.reference(f'/misterrubato/' + videoid + '/stats')
    #if this exists, return
    if ref.get() is None:
        return
        
    #really this can all be set at play record.py as well, but this is essentially the same as we run this during record.py
    #need to test this works.  Seems to work ok.  
    ref.update({'wordsrecognized': numwords})


def rungitDownload():
    print('git download start python ./git/clone.py')
    subprocess.call('python ./git/clone.py')
    print("git download complete")



def writeTranscripts(alltranscripts):
    #this should be a separate function.  
    #append to the existing transcript file.  

    f = open('./data/transcription/trans.json', "w", encoding='utf-8')
    f.write(json.dumps(alltranscripts, ensure_ascii=False, indent=4))



if __name__ == '__main__':
    argparser.add_argument("--admin", help="Add Admin user", default="")
    args = argparser.parse_args()

    stats = get_channel_stat()
    print(pd.DataFrame([stats]))

    mydate = date.today() + relativedelta(months=-TIME_WINDOW)
    dt = datetime.combine(mydate, datetime.min.time())
    print(dt.strftime('%Y-%m-%dT%H:%M:%SZ'))
    #unlist anything older than this.  

    
    databaseURL = config.cfg["firebase"]["fbconfig"]["databaseURL"]
    # Init firebase with your credentials
    creda = credentials.Certificate(config.cfg["firebase"]["credentialsfile"])
    initialize_app(creda, {'storageBucket': config.cfg["firebase"]["fbconfig"]["storageBucket"], 'databaseURL':databaseURL})    
    
    if args.admin is not None and args.admin !="":
        addAdmins(args.admin)
        checkAdmins()
        
#    youtube = get_authenticated_service(args)

    data = search(dt.strftime('%Y-%m-%dT%H:%M:%SZ'))
    print(data)


    
    iterations = []    
    totalidx = 0
    #take local backup of full DB.  
    ref = localBackup()

    alltranscripts = []
    model = None
    #ok this looks ok.  Now use the retrieved DB and update any info in the DB.  
    #then get each video individually from the DB info.  
    #no need to search.  
    #just do the ones which are recent.  
    #and update in Youtube as well as we go through.  
    #retrieve, if they are different, update in youtube.  
    
    
    adminuid = config.cfg['youtube']['ADMIN_USERID']
    
    servererrorcnt = 0
    #need to sort by date.  
    for key, item in ref:
#    for item in reversed(data["items"]):
#    for item in data['items']:
#        print(item["id"])
        #this is old dont need key !="watch" and key !="users"
        if (key !="users" and key !="watch" and item["kind"] == "youtube#video"):
#            print(item)
            videoid = item["id"]
            privacystatus = item['status']['privacyStatus']
            url = f'https://www.googleapis.com/youtube/v3/videos?part=status\
                &id={videoid}&key={api_key}'
            #for now get rid of all the old data from the queries gradually everything up to when we use DB.  
            #data quality is too poor to do much with anyway.  Also no midi before Jan/2023.  
            publishedDate = item['snippet']['publishedAt']
            description = item['snippet']['description']
            mediafile = util.getMediaFile(description)
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
                #probably not hte best way to do this.  
                if refpl.get() is None and "comments" in item:
                    if adminuid in item["comments"]:
                        grade = item["comments"][adminuid]["sentiment"]
                        pl = getPlaylistFromGrade(grade)
                        if pl !="":
                            print("add " + videoid + " to " + pl)
                            #add to playlist
                            if  "stats" in item:
                                if item["stats"]["wordsrecognized"] > 50:
                                    plwords = config.cfg["youtube"]["WORDS_PLAYLIST"]                                                                
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
                                #do we really need this?  
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
                            
                        else:
                            item['status']['privacyStatus'] = "private"
                            vref = db.reference(f'/misterrubato/' + videoid)
                            vref.set(item)
                            add_video_to_playlist(videoid, pl, args)
                            mystatus = {}         
                            mystatus['privacyStatus'] = "private"
                            
                            youtube = get_authenticated_service(args)
                            videos_update_response = youtube.videos().update(
                                part='status',
                                body=dict(
                                  status=mystatus,
                                  id=videoid
                                )).execute()            
                            print(videos_update_response)
                        

                
            transcript_file = util.getTranscriptFile(description)
            #dont repeat if not error.  
            #update "transcript" to use in chat.  
            reftranscript = db.reference(f'/misterrubato/' + videoid + '/transcript')
            reftr = reftranscript.get()
            if (reftr is not None and "transcript" in reftr):
                mytranscript = {"id": videoid, "description": description, "transcript": reftr["transcript"]}
                if ("updated" in reftr):
                    mytranscript["updated"] = reftr["updated"][0:8] #just the date
                else:
                    mytranscript["updated"] = publishedDate.replace('-', '')[0:8] #just the date
                alltranscripts.append(mytranscript)

            #update "transcript" from webUI if we have a transcript.  

            if (((privacystatus=="public")) and pDate.date() > mydate):
                #only loading once.  
                if reftr is not None and "updated" in reftr and "loaded" not in reftr:
                    print("STT training ready")
                    new_transcript_file = updatetranscript(transcript_file, reftr["updated"], reftr["transcript"]) #just creating a new instance.  
                    #store in words/...
                    #update with new transcript file.  Youtube info not updated.  Do we care?  
                    description = description.replace(transcript_file, new_transcript_file)
                    item['snippet']['description'] = description
                    vref = db.reference(f'/misterrubato/' + videoid)
                    vref.set(item)
                    #we add the file link here.  only load once.  
                    data = {'transcript': reftr["transcript"], 'transcript_file':new_transcript_file, 'updated': reftr['updated'], 'loaded': reftr['updated']}
                    reftranscript.set(data)

                    localserver = config.cfg['localserver']['host'] + ":" + str(config.cfg['localserver']['port'])
                    #update the transcriptfile.  
                    #http://
                    util.getIterations(description)
                    sta = ",".join(str(s) for s in util.st)
                    eta = ",".join(str(e) for e in util.et)
                    #pass mediafile as well.  
                    params = [('videoid', videoid),('st',sta),('et',eta),('transcriptfile',new_transcript_file), ('mediafile',mediafile)]
#                    url = f'{localserver}/transcribe/?videoid={videoid}&mediafile={mediafile}&st={sta}&et={eta}'
                    url = f'{localserver}/transcribe/'
                    print(url)
                    try:
#                        transcript = requests.get(url, timeout=(30, None)).text
                        transcript = requests.get(url, params=params, timeout=(30, None), verify=False).text
                        if (transcript is not None and transcript !="error"):
                            print("STT training complete")
                        else:
                            print('STT training error' + videoid)
                    except:
                        print('error using transcript service' + videoid)

            if (((privacystatus=="unlisted" and transcript_file=="error")) and "transcript" not in item and pDate.date() > mydate):
                if reftr is None and servererrorcnt < 3: #dont keep banging on the door when server is down.  
                    #http://192.168.1.120/transcribe/?videoid=ZshYVeNHkOM
                    #LAk9aL9uBcg, gMlt5CRj6-0, RKRHigZ-PUM, why is transcribe_whisper failing again?  
                    #need to use http or https as necessary
                    localserver = config.cfg['localserver']['host'] + ":" + str(config.cfg['localserver']['port'])
                    #should be able to use both https or http, too annoying to address now.  
                    #why does this video fail?  jRpisYQZmjU now set to null.  

                    #add start and end times here for what we want to use for speech generation.  
                    #use mediafile to download if this is not stored on youtube.  
                    util.getIterations(description)
                    #pass st and et to allow for creating wav files for voice generation.  
                    #need a userid as well so that we can generate multiple voices.  
                    #this userid should be added to the description when recording.  
                    print(util.st)
                    print(util.et)
                    sta = ",".join(str(s) for s in util.st)
                    eta = ",".join(str(e) for e in util.et)
                    params = [('videoid', videoid),('st',sta),('et',eta),('mediafile',mediafile)]
#                    url = f'{localserver}/transcribe/?videoid={videoid}&mediafile={mediafile}&st={sta}&et={eta}'
                    url = f'{localserver}/transcribe/'
                    print(url)
                    try:
#                        transcript = requests.get(url, timeout=(30, None)).text
                        #set OUTPUT_DIR
                        #just call server/transcription/transcribe.py --transcribe_fromyoutube
                        """
                        if (model is None):
                            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            model = whisper.load_model("base")
                            print("loaded model")
                            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#                        transcript = transcribe_fromyoutube(videoid, model, mediafile, sta, eta)
                        """
                        transcript = requests.get(url, params=params, timeout=(30, None), verify=False).text
                        if (transcript is not None and transcript !="error"):
                            data = {'transcript':transcript}
                            reftranscript.set(data)
                            print(data)
                            updatestatsdb(videoid, util.st, util.et, 0, len(transcript.split())) #wordcount

                        else:
                            print('transcript error' + videoid)
                    except:
                        print('error using transcript service' + videoid)
                        servererrorcnt += 1

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
                try: 
                    videos_update_response = youtube.videos().update(
                        part='status',
                        body=dict(
                        status=mystatus,
                        id=videoid
                        )).execute()            
                    print(videos_update_response)
                except:
                    print('error updating video' + videoid)


    #    #write the transcripts to a file.
    writeTranscripts(alltranscripts)

    getCodeHistory()
    
    getWatched()

    respondtoComments(args)

    rungitDownload()
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