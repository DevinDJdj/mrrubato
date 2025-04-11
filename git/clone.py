#copy all contents and commits from a repo
#into a struct we can use without the API.  
#git log --since="last month" --pretty=format:'%H,%an,%as,%at,%s' > log.csv
#Maybe this is enough for now?  
#Store this in DB?  
#If exists, skip.  
#Otherwise download all changes etc.  
#have clone-date stored, so that anything beyond this can be loaded directly if necessary.  

#from commit hash, get details.  
#this will take quite a few timestep.py runs to finish I suspect.  
#launch from timestep.  
#https://api.github.com/repos/DevinDJdj/mrrubato/git/commits/1a853838418830aa3aa7af1f7fe4240f67ffb026
#https://github.com/DevinDJdj/mrrubato/commit/1a853838418830aa3aa7af1f7fe4240f67ffb02

import os
import sys
import math

import glob
sys.path.insert(0, 'c:/devinpiano')
sys.path.insert(1, 'c:/devinpiano/music')


import config 
import subprocess
from oauth2client.tools import argparser, run_flow
import requests

#pip install firebase_admin
import firebase_admin
from firebase_admin import db
from firebase_admin import firestore

from firebase_admin import credentials
from firebase_admin import initialize_app, storage, auth


def getCodeHistory(giturl, gitbranch='master'):
#this should be a parameter.  
#similar functionality can be used in other ways.  
#where do we store this?  
#dont, just do this on the front-end.  
  try:
    url = giturl + '/commits?sha=' + gitbranch
    r = requests.get(url)
    arr = r.json()
    i = 0
    limit = 100
    for e in arr[:limit]:
        print(e['url'])
        print(e['html_url']) #this is the link we want to use in UI somewhere.  
        stats = requests.get(e['url']).json()
        print(stats['stats'])
        for f in stats['files']:
            print(f['filename'])
            print(f['changes'])
            #f['blob_url'
#    return r.json()    
  except Exception as e:
    print(e)


def cloneme(giturl, gitbranch, gitbook):

    #from here take data we need and store in DB.  
    #also download book.  
    #and store last download.  
    #This API has an upper limit of 1,000 files for a directory. If you need to retrieve more files, use the Git Trees API.
    url = giturl + '/contents/' + gitbook + '?ref=' + gitbranch
    print("clone " + url)
    response = requests.get(url)

    bookdata = response.json()
#    print(bookdata)
    gitbook = []
    numchecked = 0
    numdownloaded = 0
    for b in bookdata:
        page = b
#        print(page["download_url"])
        #add this to DB.  
        #get repo name
        pathArray = page["download_url"].split("/")
        gitbookname = pathArray[len(pathArray) - 1]
        gitbookname = gitbookname.split(".")[0]
        #this should be a date YYYYmmdd

#        print(pathArray)
        repopath = '/'.join(pathArray[-(len(pathArray) - pathArray.index("raw.githubusercontent.com")-1):])
        repopath = repopath.replace(".", "_")  #annoying we cant use original format.  
#        print(repopath)

        download = False
        refbook = db.reference(f'/git/' + repopath)
        refb = refbook.get()
        numchecked += 1
        if (refb is not None):
            #update contents
            #print("already exists " + page["download_url"])            
            #print(refb["size"])
            if (refb["size"] !=page["size"]):
               download=True

        else:
            download = True

        if download:
            numdownloaded += 1            
            print("downloading " + page["download_url"])
            book = requests.get(page["download_url"])
            #print(book.text)

            mybook = {"url": page["download_url"], "gitdata": page, "d": gitbookname, "content": book.text, "size": page["size"]}
            gitbook.append(mybook)

            #add to DB or update in DB
            refbook.set(mybook)
            print("Added to DB " + page["download_url"])

    print("clone " + url + " done")
    print("checked " + str(numchecked))
    print("downloaded " + str(numdownloaded))


def is_binary_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)
            if b'\x00' in chunk:
                return True
            text_characters = b''.join(
                bytes([i]) for i in range(32, 127)
            ) + b'\n\r\t\b'
            return not all(byte in text_characters for byte in chunk)
    except Exception:
        return True
    
def clonegit(gitcloneurl, gitbranch):
    
    #clone project to temp folder and upload each file to firebase.  
    outdir = 'c:/devinpiano/backup/git/output/' + gitcloneurl[ gitcloneurl.find("github.com/")+11 :]  + "_" + gitbranch
    cmd = 'git clone  ' + gitcloneurl + ' --single-branch --branch ' + gitbranch + ' ' + outdir
    print(cmd)
    subprocess.call(cmd, shell=True)
    #when completed upload to firebase same check if size different.  
    numuploaded = 0
    numchecked = 0
    for filename in glob.iglob(outdir + '**/**', recursive=True):
        if os.path.isfile(filename):
            numchecked += 1
            upload = False
            print(filename)
            repopath = filename[ filename.find("output/")+7 : ]
            repopath = repopath.replace("\\", "/")
            repopath = repopath.replace(".", "_")  #annoying we cant use original format.
            refgit = db.reference(f'/git/' + repopath)
            refg = refgit.get()
            numchecked += 1
            size = os.path.getsize(filename)
            if (refg is not None):
                #update contents
                #print("already exists " + page["download_url"])            
                #print(refb["size"])
                if (refg["size"] !=size):
                    upload=True

            else:
                upload = True

            if upload:
                if (is_binary_file(filename)):
                    #skip zip files
                    print("skipping binary " + filename)
                else:
                    numuploaded += 1            
                    print("uploading " + filename)
                    content = None
                    with open(filename, "r", encoding="utf-8") as file:
                        content = file.read()

                    myfile = {"content": content, "size": size}

                    #add to DB or update in DB
                    refgit.set(myfile)
                    print("Added to DB " + filename)        

    print("clone " + gitcloneurl + " done")
    print("checked " + str(numchecked)) 
    print("uploaded " + str(numuploaded))


if __name__ == '__main__':
    argparser.add_argument("--url", help="GIT URL", default=config.cfg['git'][0]['url'])
    argparser.add_argument("--cloneurl", help="GIT CLONE URL", default=config.cfg['git'][0]['cloneurl'])
    argparser.add_argument("--branch", help="GIT BRANCH", default=config.cfg['git'][0]['branch'])
    argparser.add_argument("--book", help="GIT BOOK", default=config.cfg['git'][0]['book'])
    argparser.add_argument("--all", help="CLONE ALL", default="false")
    args = argparser.parse_args()

    databaseURL = config.cfg["firebase"]["fbconfig"]["databaseURL"]
    # Init firebase with your credentials
    creda = credentials.Certificate(config.cfg["firebase"]["credentialsfile"])
    initialize_app(creda, {'storageBucket': config.cfg["firebase"]["fbconfig"]["storageBucket"], 'databaseURL':databaseURL})    


    giturl = args.url
    gitbranch = args.branch
    gitbook = args.book
    gitall = args.all    
    #getCodeHistory(giturl, gitbranch)

    #local git log not using yet
    cmd = 'git log --since="last month" --pretty=format:"%H,%an,%as,%at,%s" > log.csv'
    print(cmd)
    subprocess.call('git log --pretty=format:"%H,%an,%as,%at,%s" > log.csv', shell=True)

    #clone all repos in config.  
    if (gitall == "true"):
        print("clone all")
        print(config.cfg['git'])
        for g in config.cfg['git']:
            cloneme(g['url'], g['branch'], g['book'])
            clonegit(g['cloneurl'], g['branch'])
    else:
        cloneme(giturl, gitbranch, gitbook)
    #print(gitbook)



