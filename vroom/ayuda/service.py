#!C:\Python\Python311\python.exe

#getRecent - my recently updated pages and their ancestry.  
#getSimilar - get similar from docsim.  


import cgi
import cgitb
import os
import subprocess
import datetime
import config
import json
import requests

import base64
#pip install pillow
from PIL import Image

import gensim.models as g
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

import numpy
#import spacy

#import nltk
#from nltk.tokenize import word_tokenize


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

#need to change cgi to multipart
#https://www.agiliq.com/blog/2019/09/python-multipart/

cgitb.enable()
form = cgi.FieldStorage()
#print(form)
print("Content-type: text/html\n")
ret = ""
if "op" in form:
    op = form["op"].value
    if (op == "recent"):
          id = form["id"].value
          cat = ""
          ver = ""

          if ("cat" in form):
               cat = form["cat"].value
          if ("ver" in form):
               ver = form["ver"].value
               #no use for this.  
          test = "recently reviewed documents from this category"

          all = []
          if ("id" in form):
               basepath = "uploads/videos"
               for path, currentDirectory, files in os.walk(basepath):
                    for file in files:
                         if file.startswith(id):
                              file = file.rsplit('.',1)[0]
                              all.append(file)
               
               mylist = [i.split('_') for i in all]
               mylist = sorted(
               mylist, 
               key=lambda x: x[-1], 
               reverse=True
               )
               all.clear()
               for m in mylist:
                    all.append('_'.join(m))
                    
               ret = []
               ids = []
               for a in all:
#                    print(a + ",")
#                    ids.append(a)
                    ret.append({"id": a})
#               ret = {
#                    "ids": ids, 
#                    "images": []
#               }
               print(json.dumps(ret))

          elif ("cat" in form):
               #if cat is set query Confluence for recently updated files with this parent page.  
               basepath = "uploads/videos"
               #get from confluence with all labels from CAT_CAT2_CAT3
         #if ID is set, list all files from uploads starting with ID_.  
         #ver dont need I think.  
    elif (op == "similar"):
         doc = form["doc"].value
         cat = form["cat"].value
         #find similar to this doc in this category.  
         #after document similarity model is built.           
         model = g.Doc2Vec.load('doc2vec.model')
#         print('model loaded')
#         tokens = word_tokenize(doc.lower())
         tokens = doc.lower().split()
         new_vector = model.infer_vector(tokens)
         sims = model.dv.most_similar([new_vector], topn=30)
         ids = []
         basepath = "uploads/images"
         images = []
         ret = []
         for s in sims:
             ids.append(s[0])             
             if (os.path.exists(basepath + "/" + s[0] + ".png")):
               with open(basepath + "/" + s[0] + ".png", "rb") as imgfile:
                    data = base64.b64encode(imgfile.read())
                    imageid = s[0].split('_')[-1]
                    images.append({"image": data.decode('utf-8'), "id": imageid})
                    ocr = ('_').join(s[0].split('_')[:-1]) + '_ocr.txt'
                    ocrtext = ""
                    if (os.path.exists("uploads/ocr/" + ocr)):
                      with open("uploads/ocr/" + ocr) as ocrfile:
                        ocrtext = ocrfile.read()
                    ret.append({"id": s[0], "ocr": ocrtext, "image": data.decode('utf-8'), "imgno": imageid})
             else:
               ret.append({"id": s[0], "imgno": "-1"})
#             print(s[0] + ',')
         print(json.dumps(ret))


    elif (op=="preview"):
         id = form["id"].value
         ver = form["ver"].value
         imgno = form["img"].value
         #get text surrounding this image.  
         #quick preview for mouseover.  same as load for now.  
         fntranscript = 'uploads/transcripts/' + id + "_" + ver + ".txt"
         with open(fntranscript, "r+") as file1:
          transcript = file1.read()
         fnocr = 'uploads/ocr/' + id + "_" + ver + "_ocr.txt"
         with open(fnocr, "r+") as file2:
          ocrtranscript = file2.read()
         basepath = "uploads/images"
         images = []
#         testing = """
         for path, currentDirectory, files in os.walk(basepath):
          for file in files:
             if file.startswith(id + "_" + ver):
                with open(basepath + "/" + file, "rb") as imgfile:
                    data = base64.b64encode(imgfile.read())
                    file = file.split('.')[0]
                    imageid = file.split('_')[-1]
                    images.append({"image": data.decode('utf-8'), "id": imageid})
         ret = {
             "transcript": transcript, 
             "ocr": ocrtranscript,
             "images": images
         }
         print(json.dumps(ret))

    elif (op == "load"):
         id = form["id"].value
         ver = form["ver"].value
         #find similar to this doc in this category.  
         #after document similarity model is built.  
         #send imagelist uploads/images.  
         #send ocr text uploads/ocr and send comment text uploads/transcripts.  
         fntranscript = 'uploads/transcripts/' + id + "_" + ver + ".txt"
         with open(fntranscript, "r+") as file1:
          transcript = file1.read()
         fnocr = 'uploads/ocr/' + id + "_" + ver + "_ocr.txt"
         with open(fnocr, "r+") as file2:
          ocrtranscript = file2.read()
          #get images.  
         basepath = "uploads/images"
         images = []
#         testing = """
         for path, currentDirectory, files in os.walk(basepath):
          for file in files:
             if file.startswith(id + "_" + ver):
                with open(basepath + "/" + file, "rb") as imgfile:
                    data = base64.b64encode(imgfile.read())
                    file = file.split('.')[0]
                    imageid = file.split('_')[-1]
                    images.append({"image": data.decode('utf-8'), "id": imageid})
#                    images.append(file)
#          """
         ret = {
             "transcript": transcript, 
             "ocr": ocrtranscript,
             "images": images
         }
         print(json.dumps(ret))

    elif (op=="whoami"):
        url = config.cfg["confluence"]["url"] + '/rest/api/user/current'
        r = requests.get(url, auth=(BearerAuth(form["pat"].value)))
        if r.status_code == 200:
             print(r.text)