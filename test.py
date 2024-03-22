# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import google_auth_oauthlib.flow
from oauth2client.file import Storage

from oauth2client.tools import argparser, run_flow
import googleapiclient.discovery
import googleapiclient.errors

import sys
sys.path.insert(0, 'c:/devinpiano/')
 
import json 
import cred

import firebase_admin
from firebase_admin import db


from firebase_admin import credentials


#https://misterrubato-test-default-rtdb.firebaseio.com/

def test():
    cred = credentials.Certificate("../misterrubato-test.json")
    databaseURL = "https://misterrubato-test-default-rtdb.firebaseio.com/"
    firebase_admin.initialize_app(cred, {
	'databaseURL':databaseURL
	})
    ref = db.reference("/")
    print(ref)

def testjson():
    f = open("../testing/ollamaresponse.json", 'r')
    data = json.loads(f.read())
    print(data)

def main():
#    test()
    testjson()
if __name__ == "__main__":
    main()