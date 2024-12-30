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

sys.path.insert(0, 'c:/devinpiano/music/')

import config 
import subprocess
from oauth2client.tools import argparser, run_flow



if __name__ == '__main__':
    argparser.add_argument("--url", help="GIT URL", default=config.cfg['git']['url'])
    argparser.add_argument("--branch", help="GIT BRANCH", default=config.cfg['git']['branch'])

    args = argparser.parse_args()

    giturl = args.url
    gitbranch = args.branch
    cmd = 'git log --since="last month" --pretty=format:"%H,%an,%as,%at,%s" > log.csv'
    print(cmd)
    subprocess.call('git log --pretty=format:"%H,%an,%as,%at,%s" > log.csv', shell=True)

    #from here take data we need and store in DB.  





