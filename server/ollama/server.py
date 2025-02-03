#pip install flask
#pip install python-dotenv
#python ./server/transcription/server.py
#pip install moviepy
#pip install fastembed
import sys

from flask import Flask, request, session, g, json
from flask_cors import CORS
#pip install flask.ext
import whisper
import pandas as pd
from datetime import datetime
from langchain import hub
from langchain.embeddings import GPT4AllEmbeddings
#from langchain.embeddings import OllamaEmbeddings
from langchain.embeddings import FastEmbedEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import chainlit as cl
from langchain.chains import RetrievalQA,RetrievalQAWithSourcesChain
from fastapi.encoders import jsonable_encoder

from langchain.prompts import PromptTemplate
from pathlib import Path
import glob
import os

myhome = "/home/devin"
QUERY_DATA_PATH=myhome + "/data/inquiries/"

prompt_template = """[INST]<<SYS>>Use the following pieces of context to answer the question at the end. Please follow the following rules:
1. If you don't know the answer, try to find sources which include **coherent thoughts** relevant to the question. 
2. If you find the answer, write the answer in a concise way and add the list of sources that are 
**directly** used to derive the answer. 
<</SYS>>
{context}

Question: {question}
Helpful Answer:
[/INST]"""

current_prompt = prompt_template

def custom_prompt():

    PROMPT = PromptTemplate(input_variables=["context","question"], template=current_prompt)
    return PROMPT


QA_CHAIN_PROMPT = hub.pull("rlm/rag-prompt-llama")
QA_CHAIN_PROMPT = custom_prompt()
MY_MODEL = "llama2" #"mistral"
myEmbeddings = FastEmbedEmbeddings() #OllamaEmbeddings(model="llama2") #GPT4AllEmbeddings()

model = None

#load the LLM
def load_llm():
 llm = Ollama(
 model=MY_MODEL,
 verbose=True,
 temperature=0.9, #high temperature for variety.  
 repeat_penalty=1.5, #sometimes gets stuck in loop.  
 callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
 )
 return llm

def retrieval_qa_chain(llm,vectorstore):
 qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": custom_prompt()},
    return_source_documents=True,
)
 return qa_chain


def qa_bot(topic): 
 global model
 if (model is None):
  print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
  model = load_llm()
  print("loaded model")
 DB_PATH = myhome + "/data/vectorstores/db/"
 #topic should exist.  
 DB_PATH = myhome + "/data/vectorstores/db/" + topic + "/"
 print(DB_PATH)
 vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=myEmbeddings)
# vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=myEmbeddings)

 qa = retrieval_qa_chain(model,vectorstore)
 return qa 



app = Flask(__name__)
CORS(app)
#cors = CORS(app, resources={r"/api/*": {"origins": ["https://chat.misterrubato.com", "https://www.misterrubato.com", "*"]}})


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/ping/')
def ping():
    ret = {'answer': 'pong'}
    ret = json.dumps(ret)
    return ret


@app.route('/timestep/')
def timestep():
    query = request.args.get('since')
    uid = request.args.get('uid')
    print(uid + " timestep query " + query)


#http://127.0.0.1:8000/chat/?query=how are you
#utilize additional parameter to separate RAG DB.  
#db=xxx
@app.route('/chat/')
def chat():
    query = request.args.get('query')
    topic = request.args.get('topic')
    if (topic is None or topic ==""):
        topic = "ALL"
    print("chat query" + query)
    try:
        chain=qa_bot(topic)
        print("two")
        # res=await chain.acall(message, callbacks=[cb])
#        res= chain.call(query, callbacks=[cb])
        #this performance will hinder things I suspect.  
        res= chain.invoke(query)
        print(f"response: {res}")
        answer=res["result"]
        answer=answer.replace(".",".\n")
        sources=res["source_documents"]
        # sources = [s.replace('\\n', '\n') for s in sources]


        if sources:
            s = str(str(sources))
            s = s.replace("\\n", "\n")
            #read sources here and add a link to the time.  
            answer+=f"\nSources: "+s
        else:
            answer+=f"\nNo Sources found"
        ret = answer
    except Exception as e: # work on python 3.x
        print(e)
        ret = 'error'
    return ret

#http://127.0.0.1:8000/api/?query=how are you
#utilize additional parameter to separate RAG DB.  
#db=xxx
@app.route('/api/')
def api():
    query = request.args.get('query')
    userid = request.args.get('userid')
    topic = request.args.get('topic') #this should be multiple and combine results.  
    prompt = request.args.get('prompt')
    if (prompt is None):
        current_prompt = prompt_template
    else:
       current_prompt = prompt
    if (topic is None):
       topic = "ALL"
    if (userid is None):
       userid = "Anonymous"

    print(userid + " chat query " + topic + ": \n" + query)
    try:
        chain=qa_bot(topic)
        print("thinking...")
        print(current_prompt)
        # res=await chain.acall(message, callbacks=[cb])
#        res= chain.call(query, callbacks=[cb])
        #this performance will hinder things I suspect.  
        res= chain.invoke(query)
        print(f"response: {res}")
        answer=res["result"]
        answer=answer.replace(".",".\n")
        sources=res["source_documents"]
        # sources = [s.replace('\\n', '\n') for s in sources]

        retsource = []
        if sources:
            for s in sources:               
               retsource.append({'content': s.page_content, 'metadata': s.metadata['source']})
            
        #todo get confidence score.  
#        yearmonth = datetime.now().strftime('%Y%m') just use this on timestep side.  
        #all these files can have this data.  
        #86400 seconds in a day. * ~ 5000 = 432 MB/day max.  15GB/month.  
        #so need to clear this potentially every month.  
        #with multiple topics perhaps more often.  
        currenttime = datetime.now().strftime('%Y%m%d%H%M%S') #do we want %f microseconds here?  
        ret = {'answer': answer, 'sources': retsource, 'query': query, 'prompt': current_prompt, 'userid': userid, 'topic': topic, 'currenttime': currenttime, 'confidence': 0.0}
        ret = json.dumps(ret)
        #save this temporarily to a file.  And then from timestep, we can pull all this data into whatever DB we decide.  
        #for once we are not limited by disk space rather CPU/GPU.  
        #simplicity?  just use a directory structure for now?  
        #so just use the topic as the directory.  
        #load all these responses for the analyze API.  
        topicpath = QUERY_DATA_PATH + topic + "/"

        Path(topicpath).mkdir(parents=True, exist_ok=True)
        topicpath += currenttime + ".json"
        with open(topicpath, 'w') as f:
            f.write(ret)
    except Exception as e: # work on python 3.x
        print(e)
        ret = 'error'
    return ret


@app.route('/listtopics/')
def listtopics():
    filter = request.args.get('filter') #get all or delete all
    limit = request.args.get('limit')
    userid = request.args.get('userid')
    if (filter is None):
       filter = "*"
    else:
       filter = "*" + filter + "*"
    if (limit is None):
         limit = 10
    if (userid is None):
       userid = "Anonymous"

    i = 0
    retsource = []
    all_entries = os.listdir(QUERY_DATA_PATH)    
    print("got entries..." + str(len(all_entries)))
    for e in all_entries:
        if os.path.isdir(os.path.join(QUERY_DATA_PATH, e)):
            retsource.append(e)
            i += 1
        if i > limit:
            break
    ret = {'topics': retsource, 'userid': userid}
    ret = json.dumps(ret)
    return ret


#http://127.0.0.1:8000/analyze/?command=get&userid=..&topic=ALL are you

@app.route('/analyze/')
def analyze():
    command = request.args.get('command') #get all or delete all
    userid = request.args.get('userid')
    topic = request.args.get('topic') #this should be multiple and combine results.  
    limit = request.args.get('limit')
    if (topic is None):
       topic = "ALL"
    if (userid is None):
       userid = "Anonymous"
    if (limit is None):
       limit = 10

    print(userid + " analyze topic " + topic + ": \n")
    try:
        topicpath = QUERY_DATA_PATH + topic + "/"
        Path(topicpath).mkdir(parents=True, exist_ok=True)
        #load all responses for this topic.  
        #rate the responses if necessary from UI.  
        i = 0
        retsource = []

        #review from newest 
        files = glob.glob(topicpath + "*.json")
        print("got files..." + str(len(files)))
        files.sort(key=os.path.getmtime, reverse=True)
        for file in files:
            with open(file, 'r') as f:
                retsource.append(json.load(f))
            i += 1
            if i > limit:
               break
        ret = {'inquiries': retsource, 'topic': topic, 'userid': userid}
        print("got entries..." + str(len(retsource)))
        lastscan = ""
        if (os.path.isfile(topicpath + "lastscan.txt")):
            with open(topicpath + "lastscan.txt", 'r') as f:
                lastscan = f.read()

        if (lastscan == ""):
            lastscan = "20240121000000" 

        date_format = '%Y%m%d%H%M%S'
        print("calculating delete pct..." + lastscan)
        lastscandate = datetime.strptime(lastscan, date_format)
        print("1calculating delete pct..." + lastscan)

        currenttime = datetime.now() #do we want %f microseconds here?  
        diff = currenttime - lastscandate
        print("2calculating delete pct..." + lastscan)
        todeletepct = (diff.total_seconds() / (86400*365))
        totalfiles = len(glob.glob(topicpath + '*.json'))
        print("total entries..." + str(totalfiles))

        #delete from oldest
        files = glob.glob(topicpath + "*.json")
        files.sort(key=os.path.getmtime)
        print(str(todeletepct) + " to delete " + str(totalfiles * todeletepct) + " of " + str(totalfiles) + " files")
        i=0
        for file in files:
            i += 1
            if i > totalfiles * todeletepct:
               break
            if (userid !="Anonymous"):
                os.remove(file)
        print("deleted" + str(i))
        lastscan = currenttime.strftime('%Y%m%d%H%M%S')
        with open(topicpath + "lastscan.txt", 'w+') as f:
            f.write(lastscan)
        
    except Exception as e: # work on python 3.x
        print(e)
        ret = 'error'

    ret = json.dumps(ret)        
    return ret

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=8000, ssl_context=(myhome + '/private/cert.pem', myhome + '/private/secret.key'))
