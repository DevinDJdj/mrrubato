#https://www.geeksforgeeks.org/how-to-upload-file-in-python-flask/

from distutils.log import debug 
from fileinput import filename 
from flask import *  
from flask_cors import CORS

app = Flask(__name__)   
CORS(app)
#cors = CORS(app, resources={r"/api/*": {"origins": ["https://chat.misterrubato.com", "https://www.misterrubato.com", "*"]}})
  
@app.route('/')   
def main():   
    return 'Hello, World!'
  
@app.route('/ping/')
def ping():
    ret = {'answer': 'pong'}
    ret = json.dumps(ret)
    return ret

@app.route('/upload', methods = ['POST'])   
def success():   
    if request.method == 'POST':   
        try:
            fname = request.form.get('video-filename')
            print("upload request " + fname)

            f = request.files['video-blob'] 
            f.save(fname)   
            #kick off subprocesses here.  
            #upload to peertube for now or just GCP storage perhaps depending.  
            #other processes should complete.  
            #then delete the file.  
            #
            return 'success'
        except:
            print("error uploading " + fname)
            return 'failure'
if __name__ == '__main__':   
    app.run(host='0.0.0.0', port=8002, ssl_context=('../../private/cert.pem', '../../private/secret.key'))
