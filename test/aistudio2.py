#hnsw and tree-based google scANN (Approximate Nearest Neighbor)

#https://visualstudio.microsoft.com/visual-cpp-build-tools/
#pip install google-generativeai
#pip install chromadb
import sys

import datetime
# adding Folder_2/subfolder to the system path
#not great mechanism for config.  Maybe just make absolute path?
sys.path.insert(0, 'c:/devinpiano/')
sys.path.insert(1, 'c:/devinpiano/music')
#sys.path.append('../')
import config  

import os
import pandas as pd
import requests
import json
from oauth2client.tools import argparser, run_flow
import google.generativeai as genai

from IPython.display import HTML, Markdown, display
import time
from chromadb import Documents, EmbeddingFunction, Embeddings
from google.api_core import retry



class GeminiEmbeddingFunction(EmbeddingFunction):
    # Specify whether to generate embeddings for documents, or queries
    document_mode = True

    def __call__(self, input: Documents) -> Embeddings:
        if self.document_mode:
            embedding_task = "retrieval_document"
        else:
            embedding_task = "retrieval_query"

        retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}

        response = genai.embed_content(
            model="models/text-embedding-004",
            content=input,
            task_type=embedding_task,
            request_options=retry_policy,
        )
        return response["embedding"]


if __name__ == '__main__':
    argparser.add_argument("--title", help="Video title", default="What a Wonderful World")
    argparser.add_argument("--video", help="Video ID", default="4flRJWtfY9c")

    args = argparser.parse_args()


    genai.configure(api_key=config.cfg['google']['AISTUDIO'])
    flash = genai.GenerativeModel('gemini-1.5-flash')

    for m in genai.list_models():
        if "embedContent" in m.supported_generation_methods:
            print(m.name)

    DOCUMENT1 = "Operating the Climate Control System  Your Googlecar has a climate control system that allows you to adjust the temperature and airflow in the car. To operate the climate control system, use the buttons and knobs located on the center console.  Temperature: The temperature knob controls the temperature inside the car. Turn the knob clockwise to increase the temperature or counterclockwise to decrease the temperature. Airflow: The airflow knob controls the amount of airflow inside the car. Turn the knob clockwise to increase the airflow or counterclockwise to decrease the airflow. Fan speed: The fan speed knob controls the speed of the fan. Turn the knob clockwise to increase the fan speed or counterclockwise to decrease the fan speed. Mode: The mode button allows you to select the desired mode. The available modes are: Auto: The car will automatically adjust the temperature and airflow to maintain a comfortable level. Cool: The car will blow cool air into the car. Heat: The car will blow warm air into the car. Defrost: The car will blow warm air onto the windshield to defrost it."
    DOCUMENT2 = 'Your Googlecar has a large touchscreen display that provides access to a variety of features, including navigation, entertainment, and climate control. To use the touchscreen display, simply touch the desired icon.  For example, you can touch the "Navigation" icon to get directions to your destination or touch the "Music" icon to play your favorite songs.'
    DOCUMENT3 = "Shifting Gears Your Googlecar has an automatic transmission. To shift gears, simply move the shift lever to the desired position.  Park: This position is used when you are parked. The wheels are locked and the car cannot move. Reverse: This position is used to back up. Neutral: This position is used when you are stopped at a light or in traffic. The car is not in gear and will not move unless you press the gas pedal. Drive: This position is used to drive forward. Low: This position is used for driving in snow or other slippery conditions."

    documents = [DOCUMENT1, DOCUMENT2, DOCUMENT3]
    import chromadb

    DB_NAME = "googlecardb"
    embed_fn = GeminiEmbeddingFunction()
    embed_fn.document_mode = True

    chroma_client = chromadb.Client()
    db = chroma_client.get_or_create_collection(name=DB_NAME, embedding_function=embed_fn)

    db.add(documents=documents, ids=[str(i) for i in range(len(documents))])
    db.count()
    # You can peek at the data too.
    # db.peek(1)

    # Switch to query mode when generating embeddings.
    embed_fn.document_mode = False

    # Search the Chroma DB using the specified query.
    query = "How do you use the touchscreen to play music?"

    result = db.query(query_texts=[query], n_results=1)
    [[passage]] = result["documents"]

    Markdown(passage)


    passage_oneline = passage.replace("\n", " ")
    query_oneline = query.replace("\n", " ")

    # This prompt is where you can specify any guidance on tone, or what topics the model should stick to, or avoid.
    prompt = f"""You are a helpful and informative bot that answers questions using text from the reference passage included below. 
    Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. 
    However, you are talking to a non-technical audience, so be sure to break down complicated concepts and 
    strike a friendly and converstional tone. If the passage is irrelevant to the answer, you may ignore it.

    QUESTION: {query_oneline}
    PASSAGE: {passage_oneline}
    """
    print(prompt)

    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    answer = model.generate_content(prompt)
    Markdown(answer.text)


    