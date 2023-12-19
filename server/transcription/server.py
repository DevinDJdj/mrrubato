#pip install flask
#pip install python-dotenv
#python ./server/transcription/server.py
#pip install moviepy
import sys

from transcribe import transcribe_fromyoutube

from flask import Flask, request, session, g
import whisper
import pandas as pd
from datetime import datetime

app = Flask(__name__)

model = None
@app.route('/')
def hello():
    return 'Hello, World!'

#http://127.0.0.1:8001/transcribe/?videoid=UUUoYYW7SsE
@app.route('/transcribe/')
def transcribe():
    video = request.args.get('videoid')
    try:
        global model
        if (model is None):
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            model = whisper.load_model("medium")
            print("loaded model")
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ret = transcribe_fromyoutube(video, model)
        
    except Exception as e: # work on python 3.x
        print(e)
        ret = 'error'
    return ret

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=8001)
