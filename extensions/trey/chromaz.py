import chromadb
import logging
import sys
#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
sys.path.insert(2, 'c:/devinpiano/music/mrrubato') #config.py path Base project path

from chromadb.utils import embedding_functions

import extensions.trey.playwrighty as playwrighty
import requests
from bs4 import BeautifulSoup

client = None
current_id = 0
def load_chromaz(topic, ollama_ef=None):
    #load from persistent DB from book topic directory FULL..
    global client
    if client is None:
        client = init_chromaz()

    coll = client.get_or_create_collection(name=topic, embedding_function=ollama_ef)
    return coll

def init_chromaz(persist=False, path="./my_chroma_db"):

    global client
    if client is None:
        if persist:
            client = chromadb.PersistentClient(path=path)
        else:
            client = chromadb.Client()

    return client

def get_chunks(text, max_len=1000):
    chunks = []
    current_chunk = ""
    for line in text.split("\n"):
        current_chunk += line + "\n"
        if len(current_chunk) > max_len:
            chunks.append(current_chunk)
            current_chunk = ""
    if current_chunk:
        chunks.append(current_chunk)
    return chunks  # Simple chunking by newline, can be replaced with more sophisticated chunking

mod_len_map = {"en": 1000, "fr": 1000, "ja": 500}
def mod_length(lang):
    return mod_len_map.get(lang, 1000)

def add_data(topic, text, url="", lang="en", embedding='nomic-embed-text-v2-moe'):
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name=embedding  # Ensure 'embedding' variable holds your model string, e.g., 'nomic-embed-text'
    )
    collection = load_chromaz(topic, ollama_ef)
    #adjust max_len based on language
    max_len = mod_length(lang)
    chunks = get_chunks(text, max_len=max_len)
    metadatas = []
    current_offset = 0
    ids = []
    import hashlib
    ids = [hashlib.sha256(doc.encode()).hexdigest() for doc in chunks]
    for i, chunk in enumerate(chunks):
        metadatas.append({"url": url, "offset": current_offset, "topic": topic})
        current_offset += len(chunk)
        global current_id
        #ids.append(f"{current_id}")
        #current_id += 1

    print(f"Adding data with IDs: {ids}")
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

def search_data(topic, query, embedding='nomic-embed-text-v2-moe'):
    ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url="http://localhost:11434",
        model_name=embedding
    )
    collection = load_chromaz(topic, ollama_ef)
    results = collection.query(
        query_texts=[query],
        n_results=5
    )

    #dont like this return structure, but..
    ids = results["ids"]
    documents = results["documents"]
    distances = results["distances"]
    metadatas = results["metadatas"]
    #create struct with each 
    ret = []
    for i in range(len(ids)):
        for j in range(len(ids[i])):
            ret.append({
                "id": ids[i][j],
                "document": documents[i][j],
                "distance": distances[i][j],
                "metadata": metadatas[i][j] if metadatas else None
            })

    return ret

if (__name__ == "__main__"):

#    qdrant = QdrantClient(":memory:") # Create in-memory Qdrant instance, for testing, CI/CD
    # OR
#    client = QdrantClient(path="path/to/db")  # Persists changes to disk, fast prototyping
    init_chromaz()
#    load_chromaz(topic="demo_collection")

    myurl = "https://www.gutenberg.org/cache/epub/1/pg1-images.html"
    mydata = BeautifulSoup(requests.get(myurl).text, "html.parser")
    texts = [p.get_text() for p in mydata.find_all("p")]
    add_data(topic="demo_collection", text="\n".join(texts), url=myurl, lang="en")
    results = search_data(topic="demo_collection", query="What rights do all people have?")


    for result in results:
        print(result)
