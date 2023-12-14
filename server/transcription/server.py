#pip install flask
#pip install python-dotenv
#python ./server/transcription/server.py
import sys

sys.path.insert(0, 'c:/devinpiano/music/')

from transcribe import transcribe_me, get_timestamp

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'


if (__name__ == '__main__'):
    app.run()
