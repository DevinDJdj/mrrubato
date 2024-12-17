#lets just generate the summary and edit the files.  
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


from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

import itertools as IT

pat = config.cfg["confluence"]["pat"]
confluence = Confluence(url=config.cfg["confluence"]["url"], 
                        token=pat)


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def getSummary(transcript):
    parser = PlaintextParser.from_string(transcript, Tokenizer("english"))

    # Create an LSA summarizer
    summarizer = LsaSummarizer()

    # Generate the summary
    summary = summarizer(parser.document, sentences_count=3)  # You can adjust the number of sentences in the summary

    # Output the summary
    ret = ""
    for sentence in summary:
        ret += str(sentence) + '<br/>'
    return ret


def updateSummaries(allids, alldocs):
    for id, doc in zip(allids, alldocs):
        sum = getSummary(doc)
        fname = "output/summaries/" + id + '_sum.txt'
        with open(fname, "w") as f:
            f.write(sum)

        #do something here to update the confluence page.  
        #have to add/remove a label to know it was updated.  So use some other label than ocr
        #this 
        rec_ver = id.split('_')
        page_id = confluence.get_page_id(config.cfg["confluence"]["space"], rec_ver[-1] + '_' + ('_').join(rec_ver[:-1]))
        mypage = confluence.get_page_by_id(page_id, "body.view", status=None, version=None)
#        print(mypage)
        myupdate = sum + mypage['body']['view']['value']
        myupdate = myupdate.replace('</span>', '</img></span>')
        print(myupdate)
#        print(sum)
#        print(doc)
        me = confluence.update_page(page_id, mypage['title'], myupdate, representation='storage', full_width=False)
        fn = os.path.basename(fname)
        confluence.attach_file(fname, name=fn, content_type=None, page_id=page_id, title=fn, space=None, comment=None)
        print("uploaded summary" + fn)

        confluence.remove_page_label(page_id, "sum")
#       attach sum to page?
        #remove SUM label
    return ""

def getTranscriptsFromCF():
    allocr = "siteSearch+~+\"file.extension:txt\"+and+type+=+\"attachment\""
    #label?IN(%22yourlabel%22,%22yourlabel2%22)

    #confluence.remove_page_label(page_id, "OCR")
    #confluence.set_page_label(page_id, "OCR")

    #go through all pages and add to our doc list.  
    result = confluence.get_all_pages_by_label("SUM", start=0, limit=100)

    print(result)

    alldocs = []
    allids = []
    for r in result:
        print(r["id"])
        #perhaps copy from here to another test location?  
        attachments_container = confluence.get_attachments_from_content(page_id=r["id"], start=0, limit=500)
        print(json.dumps(attachments_container))
        attachments = attachments_container['results']
        for attachment in attachments:
            fname = attachment['title']
            if (fname.find(".txt") != -1 and fname.find("_ocr.txt") == -1):
                print(fname)
                download_link = confluence.url + attachment['_links']['download']
                r = requests.get(download_link, auth=(BearerAuth(config.cfg["confluence"]["pat"])))
                if r.status_code == 200:
                    with open("output/transcripts/" + fname, "wb") as f:
                        for bits in r.iter_content():
                            f.write(bits)    
                    with open("output/transcripts/" + fname, "r") as f:
                        transcript = f.read()
                        fname = fname.split('.')[0]
                        allids.append(fname)
                        alldocs.append(transcript)
#                        print(transcript)

    return allids, alldocs

allids, alldocs = getTranscriptsFromCF()
updateSummaries(allids, alldocs)
