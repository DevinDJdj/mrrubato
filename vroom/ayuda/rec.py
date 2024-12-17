import webbrowser
import argparse
import os.path
import time
from datetime import datetime


def sendtoconfluence(f):
    print("Sending to confluence")
    subprocess.call('python ./confluenceupload.py --title "' + f + '"')
   
def waitforcompletion(f):
    try:
        while not os.path.exists(file_path):
            time.sleep(1)
        return True
    except KeyboardInterrupt:
        return False
    
def launchbrowser(f):
    url = "https://localhost/rec.html"

    webbrowser.open(url + "?id=" + f, new=0, autoraise=True)

    #once recording is saved.  


if __name__ == "__main__":
    argparser.add_argument("--id", required=False, help="Video file to upload", default="000000")  
    args = argparser.parse_args()
    
    now = datetime.now() # current date and time
#    args.file += now.strftime("_%Y%m%d_%H%M%S")
    launchbrowser(args.file)
    #all control in browser, calling CGI to upload.  #saveremote
    
    #monitor for this file.  
    #once this file is in the downloads directory complete the sequence.  
#    if (waitforcompletion(args.file)):
#        sendtoconfluence(args.file)
#    else:
#        print("Interrupted - not sent")
    