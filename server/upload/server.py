#https://www.geeksforgeeks.org/how-to-upload-file-in-python-flask/

from distutils.log import debug 
from fileinput import filename 
from flask import *  
app = Flask(__name__)   
  
@app.route('/')   
def main():   
    return render_template("index.html")   
  
@app.route('/upload', methods = ['POST'])   
def success():   
    if request.method == 'POST':   
        f = request.files['file'] 
        f.save(f.filename)   
        #kick off subprocesses here.  
        #upload to peertube for now.  
        #other processes should come.  
        #then delete the file.  
        #
        return render_template("Acknowledgement.html", name = f.filename)   
  
if __name__ == '__main__':   
    app.run(host='0.0.0.0', port=8002, ssl_context=('../../private/cert.pem', '../../private/secret.key'))
