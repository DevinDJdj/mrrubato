#https://medium.com/@bravekjh/plug-dspy-into-ollama-or-openai-for-rag-inference-8a7de41c8ca3
#--crap
#https://medium.com/@arancibia.juan22/implementing-rag-with-dspy-a-technical-guide-a6ae15f6a455

#pip install dspy-ai openai chromadb
#pip install langchain langchain_community langchain_openai unstructured langchain_ollama
#pip install libmagic
#ollama pull nomic-embed-text
#ollama pull llama3:8b

import dspy
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from langchain_ollama import OllamaEmbeddings


lm = dspy.LM(model="ollama_chat/llama3:8b", api_base="http://localhost:11434")
dspy.settings.configure(
    lm=lm
)

question = "What is a module?"
basic_chat = dspy.Predict("question -> response")
res = basic_chat(question=question)
print(res)



docdir = "../../book"

loader = DirectoryLoader(docdir, glob="**/*.txt")
documents = loader.load()
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

chunk_size = 1000
chunk_overlap = 100
text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
sections = text_splitter.split_documents(documents)

from langchain_community.vectorstores import Chroma
"""



# Create a vector store with a sample text
from langchain_core.vectorstores import InMemoryVectorStore

text = "LangChain is the framework for building context-aware reasoning applications"

"""
embeddings = OllamaEmbeddings(
    model="llama3:8b",
    base_url="http://localhost:11434"  # Adjust the base URL as per your Ollama server configuration
)
"""

embeddings = OllamaEmbeddings(
    model="llama3",
)

doc_sources = [doc.metadata['source']  for doc in documents]
doc_content = [doc.page_content for doc in documents]

for (i, doc) in enumerate(documents):
    doc_sources[i] = doc_sources[i] + "_" + str(len(doc_content[i]))

"""
vectorstore = InMemoryVectorStore.from_texts(
    doc_content,
    embedding=embeddings,
)
"""

myhome = "../.."
DB_PATH = myhome + "/data/vectorstores/db/"
print(doc_sources)
# prevent duplication, but need to update if changed...
vectorstore = Chroma.from_documents(documents=documents, ids=doc_sources, embedding=embeddings,persist_directory=(DB_PATH + "book/"))
vectorstore.persist()

#vectorstore = InMemoryVectorStore.from_documents(
#    documents,
#    embedding=embeddings,
#)

# Use the vectorstore as a retriever
retriever = vectorstore.as_retriever()

question = "What are you doing?"
# Retrieve the most similar text
retrieved_documents = retriever.invoke(question)

# show the retrieved document's content
print(retrieved_documents[0].page_content)


#vectordb = Chroma.from_documents(documents=sections, embedding=ef, persist_directory=persist_directory)
#retriever = vectordb.as_retriever()


def retrieve(inputs):
  return [doc.page_content for doc in retriever.invoke(inputs["question"])]


class RAG(dspy.Module):
    def __init__(self):
        self.response = dspy.Predict("context, question -> response")
        
    def forward(self, question):
        context = retrieve({"question": question})
        return self.response(context=context, question=question)

rag = RAG()
print(rag(question=question))


class COT_RAG(dspy.Module):
    def __init__(self):
        self.respond = dspy.ChainOfThought("context, question -> response")
        
    def forward(self, question):
        context = retrieve({"question": question})
        return self.respond(context=context, question=question)

cot_rag = COT_RAG()
print(cot_rag(question=question))

