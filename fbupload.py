#pip install google-cloud-storage
#pip install firebase
#pip install firebase_admin

#from firebase import Firebase
#ok upload to fb and then use this midi file along with the youtube video.  
#youtube video needs to specify the filename
#does this work 
#insert_request.headers["Slug"] = fileName

import sys
sys.path.insert(0, 'c:/devinpiano/')
 
 
import cred


#firebase = Firebase(fbconfig)

from firebase_admin import credentials, initialize_app, storage
# Init firebase with your credentials
cred = credentials.Certificate("../misterrubato-test.json")
initialize_app(cred, {'storageBucket': 'misterrubato-test.appspot.com'})

# Put your local file path 
fileName = "mrrubatolarge.png"
bucket = storage.bucket()
blob = bucket.blob('midi/' + fileName)
blob.upload_from_filename(fileName)

# Opt : if you want to make public access from the URL
blob.make_public()

print("your file url", blob.public_url)