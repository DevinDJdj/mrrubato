#run/store the query/response in a more permanent way.  
#right now the sqlitedb here is probably not the best way.  
#maybe start running timestep here?  That may be easier.  
#for now just create some server proxy functionality.  
#leave timestep.py as the client.  
#primarily interaction with the DB and any backend processes should occur here.  
#need a more permanent DB.  Create Cloud instance of PostGRES DB, and interact with that later.  
#for now we will just use another sqlite db.  
#make sure any SQL is compatible though.  
#is this enough
#cors = CORS(app, resources={r"/api/*": {"origins": ["http://www.domain1.com", "http://www.domain2.com"]}})
#for now just do this.  
#then we need a management panel or whatever.  We wanted this anyway.  
#then run from the management panel the timestep and any servers etc.  


#https://www.geeksforgeeks.org/how-to-upload-file-in-python-flask/

# http://flask.pocoo.org/docs/1.0/tutorial/database/
import sqlite3

from db import init_db_command
from distutils.log import debug 
from fileinput import filename 
from flask import *  
from flask_cors import CORS
from flask.cli import with_appcontext

DBNAME  = 'ollama.db'
app = Flask(__name__)   
cors = CORS(app, resources={r"/api/*": {"origins": ["https://chat.misterrubato.com", "https://www.misterrubato.com", "*"]}})
  
# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

@app.route('/')   
def main():   
    return 'Hello, World!'
  
@app.route('/api/timestep/', methods = ['GET'])   
def success():   
    if request.method == 'GET':   
        try:
            return 'success'
        except:
            print("error ")
            return 'failure'
if __name__ == '__main__':   
    app.run(host='0.0.0.0', port=8003, ssl_context=('../../private/cert.pem', '../../private/secret.key'))

