#pip install flask
#pip install python-dotenv
#python ./server/transcription/server.py
#gcloud run deploy
#https://transcription-vzowg6vu6q-uw.a.run.app/transcribe/?videoid=ZshYVeNHkOM
#"ModuleNotFoundError: No module named 'transcribe'"
import sys

sys.path.insert(0, 'c:/devinpiano/music/')

from transcribe import transcribe_fromyoutube

from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'

#http://127.0.0.1:5000/transcribe/?videoid=UUUoYYW7SsE
@app.route('/transcribe/')
def transcribe():
    video = request.args.get('videoid')
    return transcribe_fromyoutube(video)

if (__name__ == '__main__'):
    app.run(host='0.0.0.0')
