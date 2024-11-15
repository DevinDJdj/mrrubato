#hnsw and tree-based google scANN (Approximate Nearest Neighbor)

#https://visualstudio.microsoft.com/visual-cpp-build-tools/
#pip install google-generativeai
#pip install chromadb
#pip install seaborn
#pip install scikit-learn

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

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from google.api_core import retry
from tqdm.rich import tqdm

import keras
from keras import layers

import sklearn
from sklearn.datasets import fetch_20newsgroups


def truncate(t: str, limit: int = 50) -> str:
  """Truncate labels to fit on the chart."""
  if len(t) > limit:
    return t[:limit-3] + '...'
  else:
    return t


import email
import re

import pandas as pd
import numpy as np


def preprocess_newsgroup_row(data):
    # Extract only the subject and body
    msg = email.message_from_string(data)
    text = f"{msg['Subject']}\n\n{msg.get_payload()}"
    # Strip any remaining email addresses
    text = re.sub(r"[\w\.-]+@[\w\.-]+", "", text)
    # Truncate each entry to 5,000 characters
    text = text[:5000]

    return text


def preprocess_newsgroup_data(newsgroup_dataset):
    # Put data points into dataframe
    df = pd.DataFrame(
        {"Text": newsgroup_dataset.data, "Label": newsgroup_dataset.target}
    )
    # Clean up the text
    df["Text"] = df["Text"].apply(preprocess_newsgroup_row)
    # Match label to target name index
    df["Class Name"] = df["Label"].map(lambda l: newsgroup_dataset.target_names[l])

    return df

def sample_data(df, num_samples, classes_to_keep):
    # Sample rows, selecting num_samples of each Label.
    df = (
        df.groupby("Label")[df.columns]
        .apply(lambda x: x.sample(num_samples))
        .reset_index(drop=True)
    )

    df = df[df["Class Name"].str.contains(classes_to_keep)]

    # We have fewer categories now, so re-calibrate the label encoding.
    df["Class Name"] = df["Class Name"].astype("category")
    df["Encoded Label"] = df["Class Name"].cat.codes

    return df

@retry.Retry(timeout=300.0)
def embed_fn(text: str) -> list[float]:
    # You will be performing classification, so set task_type accordingly.
    response = genai.embed_content(
        model="models/text-embedding-004", content=text, task_type="classification"
    )

    return response["embedding"]


def create_embeddings(df):
    df["Embeddings"] = df["Text"].progress_apply(embed_fn)
    return df

def build_classification_model(input_size: int, num_classes: int) -> keras.Model:
    return keras.Sequential(
        [
            layers.Input([input_size], name="embedding_inputs"),
            layers.Dense(input_size, activation="relu", name="hidden"),
            layers.Dense(num_classes, activation="softmax", name="output_probs"),
        ]
    )


if __name__ == '__main__':
    argparser.add_argument("--title", help="Video title", default="What a Wonderful World")
    argparser.add_argument("--video", help="Video ID", default="4flRJWtfY9c")

    args = argparser.parse_args()


    genai.configure(api_key=config.cfg['google']['AISTUDIO'])
    flash = genai.GenerativeModel('gemini-1.5-flash')

    for m in genai.list_models():
        if "embedContent" in m.supported_generation_methods:
            print(m.name)


    texts = [
        'The quick brown fox jumps over the lazy dog.',
        'The quick rbown fox jumps over the lazy dog.',
        'teh fast fox jumps over the slow woofer.',
        'a quick brown fox jmps over lazy dog.',
        'brown fox jumping over dog',
        'fox > dog',
        # Alternative pangram for comparison:
        'The five boxing wizards jump quickly.',
        # Unrelated text, also for comparison:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus et hendrerit massa. Sed pulvinar, nisi a lobortis sagittis, neque risus gravida dolor, in porta dui odio vel purus.',
    ]


    response = genai.embed_content(model='models/text-embedding-004',
                                content=texts,
                                task_type='semantic_similarity')
    
    truncated_texts = [truncate(t) for t in texts]
    # Set up the embeddings in a dataframe.

    df = pd.DataFrame(response['embedding'], index=truncated_texts)
    # Perform the similarity calculation
    sim = df @ df.T
    # Draw!
    sns.heatmap(sim, vmin=0, vmax=1)
    plt.show()
    print(sim['The quick brown fox jumps over the lazy dog.'].sort_values(ascending=False))



    newsgroups_train = fetch_20newsgroups(subset="train")
    newsgroups_test = fetch_20newsgroups(subset="test")

    # View list of class names for dataset
    print(newsgroups_train.target_names)
    print(newsgroups_train.data[0])

    df_train = preprocess_newsgroup_data(newsgroups_train)
    df_test = preprocess_newsgroup_data(newsgroups_test)

    df_train.head()
    TRAIN_NUM_SAMPLES = 100
    TEST_NUM_SAMPLES = 25
    CLASSES_TO_KEEP = "sci"  # Class name should contain 'sci' to keep science categories

    df_train = sample_data(df_train, TRAIN_NUM_SAMPLES, CLASSES_TO_KEEP)
    df_test = sample_data(df_test, TEST_NUM_SAMPLES, CLASSES_TO_KEEP)
    df_train.value_counts("Class Name")
    df_test.value_counts("Class Name")

    
    tqdm.pandas()

    df_train = create_embeddings(df_train)
    df_test = create_embeddings(df_test)
    df_train.head()

    # Derive the embedding size from observing the data. The embedding size can also be specified
    # with the `output_dimensionality` parameter to `embed_content` if you need to reduce it.
    embedding_size = len(df_train["Embeddings"].iloc[0])

    classifier = build_classification_model(
        embedding_size, len(df_train["Class Name"].unique())
    )
    classifier.summary()

    classifier.compile(
        loss=keras.losses.SparseCategoricalCrossentropy(),
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        metrics=["accuracy"],
    )

    NUM_EPOCHS = 20
    BATCH_SIZE = 32

    # Split the x and y components of the train and validation subsets.
    y_train = df_train["Encoded Label"]
    x_train = np.stack(df_train["Embeddings"])
    y_val = df_test["Encoded Label"]
    x_val = np.stack(df_test["Embeddings"])

    # Specify that it's OK to stop early if accuracy stabilises.
    early_stop = keras.callbacks.EarlyStopping(monitor="accuracy", patience=3)

    # Train the model for the desired number of epochs.
    history = classifier.fit(
        x=x_train,
        y=y_train,
        validation_data=(x_val, y_val),
        callbacks=[early_stop],
        batch_size=BATCH_SIZE,
        epochs=NUM_EPOCHS,
    )

    classifier.evaluate(x=x_val, y=y_val, return_dict=True)    

    # This example avoids any space-specific terminology to see if the model avoids
    # biases towards specific jargon.
    new_text = """
    First-timer looking to get out of here.

    Hi, I'm writing about my interest in travelling to the outer limits!

    What kind of craft can I buy? What is easiest to access from this 3rd rock?

    Let me know how to do that please.
    """
    embedded = embed_fn(new_text)

    # Remember that the model takes embeddings as input, and the input must be batched,
    # so here they are passed as a list to provide a batch of 1.
    inp = np.array([embedded])
    [result] = classifier.predict(inp)

    for idx, category in enumerate(df_test["Class Name"].cat.categories):
        print(f"{category}: {result[idx] * 100:0.2f}%")
