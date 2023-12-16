#pip install flask
#pip install python-dotenv
#python ./server/transcription/server.py
#pip install moviepy
import sys

from transcribe import transcribe_fromyoutube

from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'

#http://127.0.0.1:8001/transcribe/?videoid=UUUoYYW7SsE
@app.route('/transcribe/')
def transcribe():
    video = request.args.get('videoid')
    return transcribe_fromyoutube(video)

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=8001)
