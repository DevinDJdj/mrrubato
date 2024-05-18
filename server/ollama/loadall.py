
from os import path
import subprocess
import glob
import os

myhome = "/home/devin"
DATA_PATH="data/"
DATA_PATH=myhome + "/data/transcription/output/"

if __name__=="__main__":
    list_of_files = glob.glob(DATA_PATH + "*") # * means all if need specific format then *.csv
    for file in list_of_files:
        video = os.path.splitext(os.path.basename(file))[0]
        subprocess.call('python3 ' + myhome + '/mrrubato/server/ollama/load.py --video ' + video, shell=True)
