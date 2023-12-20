#import required dependencies
#this default port is 8000
#chainlit run RAG.py

from langchain import hub
from langchain.embeddings import GPT4AllEmbeddings
from langchain.embeddings import OllamaEmbeddings
from langchain.embeddings import FastEmbedEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import chainlit as cl
from langchain.chains import RetrievalQA,RetrievalQAWithSourcesChain
# Set up RetrievelQA model
QA_CHAIN_PROMPT = hub.pull("rlm/rag-prompt-llama")
MY_MODEL = "llama2" #"mistral"
myEmbeddings = FastEmbedEmbeddings() #OllamaEmbeddings(model="llama2") #GPT4AllEmbeddings()

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


def qa_bot(): 
 llm=load_llm() 
 DB_PATH = "vectorstores/db/"
 vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=myEmbeddings)

 qa = retrieval_qa_chain(llm,vectorstore)
 return qa 

@cl.on_chat_start
async def start():
 chain=qa_bot()
 msg=cl.Message(content="Firing up the research info bot...")
 await msg.send()
 msg.content= "Hi, welcome to research info bot. What is your query?"
 await msg.update()
 cl.user_session.set("chain",chain)

@cl.on_message
async def main(message):
 chain=cl.user_session.get("chain")
 cb = cl.AsyncLangchainCallbackHandler(
 stream_final_answer=True,
 answer_prefix_tokens=["FINAL", "ANSWER"]
 )
 cb.answer_reached=True
 # res=await chain.acall(message, callbacks=[cb])
 res=await chain.acall(message.content, callbacks=[cb])
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

 await cl.Message(content=answer).send() 