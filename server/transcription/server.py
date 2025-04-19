#pip install flask
#pip install python-dotenv
#python ./server/transcription/server.py
#pip install moviepy
import sys
import os
from transcribe import transcribe_fromyoutube, downloadtranscript

from flask import Flask, request, session, g, json
from flask_cors import CORS
import whisper
import pandas as pd
from datetime import datetime

import subprocess

myhome = "/home/devin"

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

#http://127.0.0.1:8001/transcribe/?videoid=UUUoYYW7SsE
@app.route('/transcribe/')
def transcribe():
    video = request.args.get('videoid')
    mediafile = request.args.get('mediafile')
    transcriptfile = request.args.get('transcriptfile')
    st = request.args.get('st')
    et = request.args.get('et')
    reviewed = ""
    try:
        global model
        if (model is None):
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            model = whisper.load_model("base") #have to use base here?  
            print("loaded model")
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if (transcriptfile != None and transcriptfile != ""):
            ret = downloadtranscript(transcriptfile, mediafile, video, st, et)
            reviewed = " --topic REVIEWED"
        else:
            ret = transcribe_fromyoutube(video, model, mediafile, st, et)
        
    except Exception as e: # work on python 3.x
        print(e)
        ret = 'error'
    if ret !='error' and ret !='':
        subprocess.call('python3 ' + myhome + '/mrrubato/server/ollama/load.py --video ' + video + reviewed, shell=True)
    return ret

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=8001, ssl_context=(myhome + '/private/cert.pem', myhome + '/private/secret.key'))
