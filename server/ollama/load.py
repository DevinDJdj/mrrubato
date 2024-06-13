#pip install chromadb
#pip install langchain
#pip install BeautifulSoup4
#pip install gpt4all
#pip install langchainhub
#pip install pypdf
#pip install chainlit
#pip install fastembed
#pip install langchain-text-splitters

from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain_community.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader, BSHTMLLoader

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.embeddings import LlamaCppEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.embeddings import FastEmbedEmbeddings #pip install fastembed


from oauth2client.tools import argparser, run_flow

#from langchain.embeddings import OllamaEmbeddings
#dont think this is working.  
#try to continue here 
#https://medium.com/@vndee.huynh/build-your-own-rag-and-run-it-locally-langchain-ollama-streamlit-181d42805895

import os
from pathlib import Path

myhome = "/home/devin"
DATA_PATH="data/"
DATA_PATH=myhome + "/data/transcription/output/"
DB_PATH = myhome + "/data/vectorstores/db/"
QUERY_DATA_PATH=myhome + "/data/inquiries/"

def create_vector_db():
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    print(f"Processed {len(documents)} pdf files")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    texts=text_splitter.split_documents(documents)
    #this results in OSError: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32' not found
#    vectorstore = Chroma.from_documents(documents=texts, embedding=GPT4AllEmbeddings(),persist_directory=DB_PATH)      
#    vectorstore = Chroma.from_documents(documents=texts, embedding=LlamaCppEmbeddings(),persist_directory=DB_PATH) 
    vectorstore = Chroma.from_documents(documents=texts, embedding=FastEmbedEmbeddings(),persist_directory=DB_PATH)      
         
    vectorstore.persist()


def create_llama2_db(video = "*", topic = "ALL"):
    topicpath = DB_PATH + topic + "/"
    Path(topicpath).mkdir(parents=True, exist_ok=True)
    querytopicpath = QUERY_DATA_PATH + topic + "/"
    Path(querytopicpath).mkdir(parents=True, exist_ok=True)
    loader = DirectoryLoader(DATA_PATH, glob="**/" + video + ".txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"Processed {len(documents)} txt files")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=390, chunk_overlap=40)
    texts = text_splitter.split_documents(documents)
    ollamaEmbeddings = OllamaEmbeddings(model="llama2")
#    vectorstore = Chroma.from_documents(documents=texts, embedding=ollamaEmbeddings,persist_directory=DB_PATH) 
    #use default ALL model for everything.  
    #always store in ALL
    vectorstore = Chroma.from_documents(documents=texts, embedding=FastEmbedEmbeddings(),persist_directory=(DB_PATH + "ALL/"))
    vectorstore.persist()

    #store in additional topic
    if (topic != "ALL"):
        topicstore = Chroma.from_documents(documents=texts, embedding=FastEmbedEmbeddings(),persist_directory=topicpath)      
        topicstore.persist()


if __name__=="__main__":
#    create_vector_db()
    argparser.add_argument("--video", help="Add video to DB", default="")
    argparser.add_argument("--topic", help="Topic for utilization", default="ALL")
    #called from transcript server
    args = argparser.parse_args()
    video = "*"
    if args.video is not None and args.video !="":
        video = args.video
    create_llama2_db(video)
