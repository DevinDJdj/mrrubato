#Call the TTS/bin/synthesize.py
#and return the wav or best format file.  
#call locally from **server/ollama/server.py or just call after we get response in the browser.  
#Response speed will improve gradually.  

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

from flask import Flask, request, session, g, json
from flask_cors import CORS
import whisper
import pandas as pd
from datetime import datetime

import subprocess

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
        #subprocess.call('python ./synthesize.py --text ' + text, shell=True)
        #get temp file from synthesize.  
                
    except Exception as e: # work on python 3.x
        print(e)
        ret = 'error'
    return ret

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=8003, ssl_context=('../../private/cert.pem', '../../private/secret.key'))
