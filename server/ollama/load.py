from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.document_loaders import UnstructuredHTMLLoader, BSHTMLLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import GPT4AllEmbeddings
from langchain.embeddings import LlamaCppEmbeddings
from langchain.embeddings import FastEmbedEmbeddings #pip install fastembed

#from langchain.embeddings import OllamaEmbeddings
#dont think this is working.  
#try to continue here 
#https://medium.com/@vndee.huynh/build-your-own-rag-and-run-it-locally-langchain-ollama-streamlit-181d42805895

import os

DATA_PATH="data/"
DB_PATH = "vectorstores/db/"

def create_vector_db():
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    print(f"Processed {len(documents)} pdf files")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    texts=text_splitter.split_documents(documents)
    #this results in OSError: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32' not found
    vectorstore = Chroma.from_documents(documents=texts, embedding=GPT4AllEmbeddings(),persist_directory=DB_PATH)      
#    vectorstore = Chroma.from_documents(documents=texts, embedding=LlamaCppEmbeddings(),persist_directory=DB_PATH) 
#    vectorstore = Chroma.from_documents(documents=texts, embedding=FastEmbedEmbeddings(),persist_directory=DB_PATH)      
         
    vectorstore.persist()

if __name__=="__main__":
    create_vector_db()