#https://www.geeksforgeeks.org/doc2vec-in-nlp/
#pip install gensim
#pip install nltk
#pip install spacy
#python -m spacy download en_core_web_sm

"""
def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)


article = nlp(text)
labels = [x.label_ for x in article.ents]
Counter(labels)

"""

from atlassian import Confluence
import json
import requests
import subprocess
import config
from oauth2client.tools import argparser, run_flow
import glob
from pathlib import Path   

import gensim.models as g
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import nltk
from nltk.tokenize import word_tokenize
import os
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")


nltk.download('punkt')
# define a list of documents.
#download all OCRed docs from confluence.  
#_ocr


pat = config.cfg["confluence"]["pat"]
confluence = Confluence(url=config.cfg["confluence"]["url"], 
                        token=pat)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def getOCRDocs(ocr):
    scans = []
    for i in range(20):
        startstr = "--OCR" + str(i) + "--"
        endstr = "--OCR" + str(i) + "END--"
        startpos = ocr.find(startstr)
        endpos = ocr.find(endstr)
        if (startpos > -1 and endpos > -1):
            scans.append(ocr[startpos+len(startstr):endpos])

    return scans
#    s[s.find(start)+len(start):s.rfind(end)]

def parseOCRDocs(DATA_PATH="output/ocr/"):
    alldocs = []
    allids = []
    list_of_files = glob.glob(DATA_PATH + "*") # * means all if need specific format then *.csv
    for file in list_of_files:
        with open(file, "r") as f:
            file = file.rsplit('.',1)[0]
            file = file.split('/')[-1]
            file = file.split('\\')[-1]
            file = file.replace('_ocr', '')
            ocr = f.read()
            scans = getOCRDocs(ocr)
            for i in range(len(scans)):
                allids.append(file + "_" + str(i))
            alldocs.extend(scans)

    return allids, alldocs

def getOCRDocsFromCF():
    allocr = "siteSearch+~+\"file.extension:txt\"+and+type+=+\"attachment\"+and+spacekey+=+\"AYUD\""
    #label?IN(%22yourlabel%22,%22yourlabel2%22)

    #confluence.remove_page_label(page_id, "OCR")
    #confluence.set_page_label(page_id, "OCR")

    #go through all pages and add to our doc list.  
#    result = confluence.get_all_pages_by_label("OCR", start=0, limit=50)
    result = confluence.get_all_pages_from_space(config.cfg["confluence"]["space"])

    print(result)

    for r in result:
        print(r["id"])
        #perhaps copy from here to another test location?  
        attachments_container = confluence.get_attachments_from_content(page_id=r["id"], start=0, limit=500)
        print(json.dumps(attachments_container))
        attachments = attachments_container['results']
        for attachment in attachments:
            fname = attachment['title']
            print(fname)
            if (fname.find("_ocr.txt") != -1):
                download_link = confluence.url + attachment['_links']['download']
                r = requests.get(download_link, auth=(BearerAuth(config.cfg["confluence"]["pat"])))
                if r.status_code == 200:
                    with open("output/ocr/" + fname, "wb") as f:
                        for bits in r.iter_content():
                            f.write(bits)    



getOCRDocsFromCF()
allids, alldata = parseOCRDocs()

tagged_data = []
for i, doc in enumerate(alldata):
    tagged_data.append(TaggedDocument(words=word_tokenize(doc.lower()),
                              tags=[allids[i]]))

#if (os.path.exists('doc2vec.model')):
#    model = g.Doc2Vec.load('doc2vec.model')
#    print('model loaded')
#else:
print('initiating model')
model = Doc2Vec(vector_size=50,
            min_count=2, epochs=100)
model.build_vocab(tagged_data)
model.train(tagged_data,
        total_examples=model.corpus_count,
        epochs=model.epochs)
 
# get the document vectors
document_vectors = [model.infer_vector(
    word_tokenize(doc.lower())) for doc in alldata]
 
#  print the document vectors
for i, doc in enumerate(alldata):
    print("Document", i+1, ":", doc)
    print("Vector:", document_vectors[i])
    print()

model.save('doc2vec.model')


def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent


#usage
#why do we have to split this?  Anyway...
testdoc = "this is the fifth document."
article = nlp(testdoc)
labels = [(x.text, x.label_) for x in article.ents]
print(Counter(labels))
print(labels)

details = [(x, x.ent_iob_, x.ent_type_) for x in article]
print(details)



tokens = word_tokenize(testdoc.lower())
new_vector = model.infer_vector(tokens)
sims = model.dv.most_similar([new_vector])
print(sims)

