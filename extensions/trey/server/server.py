#pip install flask
#pip install python-dotenv
#python ./server/transcription/server.py
#pip install moviepy
import sys
import os
import json
from fastapi import Request
from fastapi.responses import JSONResponse
#from flask import Flask, request, session, g, json
#from flask_cors import CORS

import pandas as pd
from datetime import datetime

import subprocess

myhome = "c:/devinpiano"

import uvicorn
from fastapi import FastAPI

app = FastAPI()

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='trey.log', 
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

#app = Flask(__name__)
#CORS(app)

# get state
#selection map tracks transcript selection history for each topic
state = {'selectionhistory': [], 'selectionmap': {},
         'cmdhistory': [], 'transcripthistory': [], 
         'currentfunctions': [], 
         'currenttopic': '', 'currentbook': '', 'filter': [], 
         'tabs': [], 'webtabs': [], 
         'last_sent': 0, 'last_received': 0, 'last_edited': 0}

model = None
qrin_queue = None
@app.get('/')
def hello():
    return 'Hello, World!'


@app.get('/state/')
def get_state():
    ret = json.dumps(state)
    return JSONResponse(content=state)


@app.post('/transcript/update/')
async def update_transcript(request: Request):
    global state
    data = await request.json()
    if ('&&' in data):
        state['transcripthistory'].append(data['&&'])
        logger.info(f"Transcript updated: {data['&&']}")
        #handle the new transcript update..
    if qrin_queue is not None:        
        qrin_queue.put(data) # -> trigger mykeys..

    return JSONResponse(content=state)

@app.post('/state/update/')
async def update_state(request: Request):
    global state
    data = await request.json()
    logger.info(f"Updating state with data: {data}")
    for key, value in data.items():
        if key in state:
            state[key] = value
    #dump data to qrin_queue
    logger.info(f"State updated: {state}")
    return JSONResponse(content=state)

@app.get('/ping/')
def ping():
    ret = {'answer': 'pong'}
    logger.info("Ping received, responding with pong")
    return JSONResponse(content=ret)


def run_flask_app(qrin=None):
    global qrin_queue
    qrin_queue = qrin
    # IMPORTANT: use_reloader=False prevents the background thread from crashing
    logger.info("> FastAPI open 127.0.0.1:8003")
    uvicorn.run(app, host="127.0.0.1", port=8003, log_level="info")
    
if (__name__ == '__main__'):
    logger.info("Fastapi app is running on 0.0.0.0:8003")
    uvicorn.run(app, host='0.0.0.0', port=8003)#, ssl_context=(myhome + '/private/cert.pem', myhome + '/private/secret.key'))
