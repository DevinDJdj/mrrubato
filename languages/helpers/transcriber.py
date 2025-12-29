#transcribe commands into timeline.
from datetime import datetime, timedelta
import os
import logging
import time

logger = logging.getLogger(__name__)


class transcriber:
    def __init__(self, lang_helper):
        self.lang_helper = lang_helper

    def getTime(self, relativedays=0):
        now = datetime.now()
        now += timedelta(days=relativedays)
        return now
    
    def getTimeString(self, relativedays=0):
        now = self.getTime(relativedays)
        return now.strftime('%Y%m%d_%H%M%S')
    
    def write(self, lang, command, params):
      #write to transcript file.  
      #for now just one time param.  

      today = datetime.now().strftime("%Y%m%d")
      folder = '../transcripts/' + lang + '/'
      os.makedirs(folder, exist_ok=True)
      #add utf-8?  
      with open(folder + today + '.txt', 'a', encoding='utf-8') as f:        
        f.write(f'<{lang}>\n')
        f.write(f'> {command}\n')
        vars = {}
        for pkey, p in params.items():
            f.write(f'$${pkey}={p}\n')
        if ('TIME' not in params):
            f.write(f'$$TIME={self.getTimeString()}\n')
        f.write(f'$$\n')
        #dont worry about duplication at this point.

    def get_cmd(self, type, command, vars):
        t = time.time()
        if ('TIME' in vars):
            timestr = vars['TIME']
            t = time.mktime(datetime.strptime(timestr, '%Y%m%d %H%M%S').timetuple())
        return {'type': type, 'cmd': command, 'vars': vars, 'timestamp': t}
    
    def read(self, lang, start_time=None, end_time=None):

      #read from transcript file all instances of this.   
        if (start_time is None):
            start_time = self.getTime(-30)  #default last 30 days
        if (end_time is None):
            end_time = self.getTime()
        logger.info(f'Loading {lang} start {start_time} to {end_time}')
        #list all files in directory
        folder = '../transcripts/' + lang + '/'
        os.makedirs(folder, exist_ok=True)

        files = [f for f in os.listdir(folder) if os.path.getctime(folder + f) >= start_time.timestamp() and os.path.getctime(folder + f) <= end_time.timestamp()]
        sorted_files = sorted(files)
        numloaded = 0
        print('Reading transcripts from:')
        print(sorted_files)
        ret = []
        currentcmd = ""
        vars = {}
        for f in sorted_files:
    #      if (f.startswith(yesterday) or f.startswith(today)):
            if (f.endswith('.txt')): #dont open wav files.. maybe rethink sharing directory..
                try:
                    with open(folder + f, encoding='utf-8') as ff:
                        lines = ff.readlines()
                        for line in lines:
                            #add bookmark manually.  
                            type = line[0:2]
                            if (type == '> '):
                                #command line internal command
                                if (currentcmd != ""):
                                    #save previous command if exists with no params..
                                    c = self.get_cmd(type, currentcmd, vars)
                                    ret.append(c)
                                currentcmd = line[2:]
                            if (type == '$$'):
                                #special trey data line
                                if (len(line) == 2):
                                    #execute command
                                    if (currentcmd != ""):
                                        type = '> '
                                    c = self.get_cmd(type, currentcmd, vars)
                                    ret.append(c)
                #                    logger.info(f'Adding QR {type}: {currentcmd}')
                                    currentcmd = ""
                                    vars = {}

                                else:
                                    parts = line[2:].split('=')
                                    if (len(parts) == 2):
                                        key = parts[0]
                                        value = parts[1]
                                        vars[key] = value

                except Exception as e:
                    logger.error(f'!!> Read [{f}]\n !!{e}')

                if (currentcmd != ""):
                    type = '> '
                    c = self.get_cmd(type, currentcmd, vars)
                    ret.append(c)
                    currentcmd = ""
                    vars = {}
        return ret
