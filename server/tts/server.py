#download coqui-tts https://github.com/coqui-ai/TTS to this directory.  
#Call the TTS/bin/synthesize.py
#and return the wav or best format file.  
#call locally from **server/ollama/server.py or just call after we get response in the browser.  
#Response speed will improve gradually.  
#creating a wrapper for this because I dont want to run the coqui server every time.  


#We can update these transcript files from **web/public/analyze.html
#make separate transcription entry to indicate fixed data.  

#**server/transcription/server.py
#->api->update

#**web/public/server/tts.html
#->tts/server.py->api->train.py
#pip install flask
#pip install python-dotenv
#python ./server/transcription/server.py
#pip install moviepy

import sys
import os
import time

from flask import Flask, request, session, g, json, send_file
from flask_cors import CORS
import whisper
import pandas as pd
from datetime import datetime

import subprocess


myhome = os.environ['HOME']

TACOTRON_DIR = myhome + '/TSS/recipes/ljspeech/tacotron2-DCA/'

app = Flask(__name__)
CORS(app)
#cors = CORS(app, resources={r"/api/*": {"origins": ["https://chat.misterrubato.com", "https://www.misterrubato.com", "*"]}})

model = None
@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/ping/')
def ping():
    ret = {'answer': 'pong'}
    ret = json.dumps(ret)
    return ret

#http://127.0.0.1:8003/api/?text=
@app.route('/api/')
def transcribe():
    text = request.args.get('text')
    try:
        print('tts synthesize')
        #--list_models
        #--vocoder_paths
        all_subdirs = [d for d in os.listdir(TACOTRON_DIR) if os.path.isdir(d)]
        latest_subdir = max(all_subdirs, key=os.path.getmtime)
        #python3 ./synthesize.py --text text --model_path "../../recipes/ljspeech/tacotron2-DDC/' + latest_subdir + '/best_model.pth" --config_path "../../recipes/ljspeech/tacotron2-DDC/' + latest_subdir + '/config.json"
        subprocess.call('python3 ' + myhome + '/TTS/bin/synthesize.py --output_path tts_output.wav --text "' + text + '" --model_path ' + TACOTRON_DIR + latest_subdir + 'best_model.pth --config_path ' + TACOTRON_DIR + latest_subdir + '/config.json', shell=True)
        #get temp file from synthesize.  
        return send_file("tts_output.wav", mimetype="audio/wav")
                
    except Exception as e: # work on python 3.x
        print(e)
        ret = 'error'
    return ret

@app.route('/train/')
def train():
    #do we want this via API?  
    #just save last call time.  
    userid = request.args.get('userid')

    all_subdirs = [d for d in os.listdir(TACOTRON_DIR) if os.path.isdir(d)]
    latest_subdir = max(all_subdirs, key=os.path.getmtime)

    lastscan = ""
    if (os.path.isfile("lastscan.txt")):
        with open("lastscan.txt", 'r') as f:
            lastscan = f.read()

    if (lastscan == ""):
        lastscan = "20240121000000" 

    date_format = '%Y%m%d%H%M%S'
    lastscandate = datetime.strptime(lastscan, date_format)

    currenttime = datetime.now() #do we want %f microseconds here?  
    diff = currenttime - lastscandate
    lasttrain = (diff.total_seconds() / (86400*365)) #pct of year
    print(str(lasttrain) + " since last train ")

    #do all processing ...
    #or just do if the last date matches the folder date and the model path and config.json exist.  
    #if the currenttime is > 2 weeks from this, allow training.  
    #will have to run this once manually probably.  
    lasttraindir = os.path.getmtime(TACOTRON_DIR + latest_subdir)
    age = (time.time() - lasttraindir)/(86400*365)
    if age > 0.02: #~1 week go ahead and train again.  Keep 2-3 iterations?  Delete others.  
        #have to see how long this actually takes on a bit better machine.  
        if (os.path.exists(TACOTRON_DIR + latest_subdir + '/best_model.pth') and os.path.exists(TACOTRON_DIR + latest_subdir + '/config.json')):
            #run training.  
            #python3 TACOTRON_DIR + 'train_tacotron_ddc.py'
            #from model directory can we use?
            #recipes/ljspeech/tacotron2-DDC/run-April-03-2024_04+21PM-dbf1a08a
            #../../../../TTS/bin/train_tts.py --continue_path .
#            subprocess.call('python3 ' + TACOTRON_DIR + 'train_tacotron_ddc.py', shell=True)
            #this should be used, then no modifying files necessary GGGG.  
            subprocess.call('python3 ' + TACOTRON_DIR + 'TTS/bin/train_tts.py --continue_path ' + TACOTRON_DIR + latest_subdir, shell=True)
    #check that we succeed.  
    #otherwise will have to do via command line.  


    lastscan = currenttime.strftime('%Y%m%d%H%M%S')
    with open("lastscan.txt", 'w+') as f:
        f.write(lastscan)



if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=8003, ssl_context=(myhome + '/private/cert.pem', myhome + '/private/secret.key'))
