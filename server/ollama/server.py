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





def custom_prompt():
    prompt_template = """[INST]<<SYS>>Use the following pieces of context to answer the question at the end. Please follow the following rules:
    1. If you don't know the answer, try to find sources which include **coherent thoughts** relevant to the question. 
    and add the source links as a list.
    2. If you find the answer, write the answer in a concise way and add the list of sources that are 
    **directly** used to derive the answer. Exclude the sources that are irrelevant to the final answer.
    <</SYS>>
    {context}

    Question: {question}
    Helpful Answer:
    [/INST]"""

    PROMPT = PromptTemplate(input_variables=["context","question"], template=prompt_template)
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
 callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
 )
 return llm

def retrieval_qa_chain(llm,vectorstore):
 qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    return_source_documents=True,
)
 return qa_chain


def qa_bot(db): 
 global model
 if (model is None):
  print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
  model = load_llm()
  print("loaded model")
 DB_PATH = "vectorstores/db/"
 if db is not None:
  DB_PATH = "vectorstores/db/" + db + "/"
  print(DB_PATH)
 vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=myEmbeddings)
# vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=myEmbeddings)

 qa = retrieval_qa_chain(model,vectorstore)
 return qa 



app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello, World!'


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
    db = request.args.get('db')
    print("chat query" + query)
    try:
        chain=qa_bot(db)
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
@app.route('/api/')
def api():
    query = request.args.get('query')
    print("chat query" + query)
    try:
        chain=qa_bot()
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

        retsource = []
        if sources:
            for s in sources:               
               retsource.append({'content': s.page_content, 'metadata': s.metadata['source']})
            
        ret = {'answer': answer, 'sources': retsource, 'query': query}
        ret = json.dumps(ret)
    except Exception as e: # work on python 3.x
        print(e)
        ret = 'error'
    return ret

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=8000, ssl_context=('../../private/cert.pem', '../../private/secret.key'))
