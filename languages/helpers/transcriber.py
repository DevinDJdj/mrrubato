#transcribe commands into timeline.
from datetime import datetime, timedelta
import os
import logging
import time
import pathlib
import re

logger = logging.getLogger(__name__)


class transcriber:
    def __init__(self, lang_helper=None):
        self.lang_helper = lang_helper
        self.defstring = r"[~!@#$%^&*<>/:;\-\+=]"
        self.allcmds = {} #lang -> {cmds, start_time, end_time, list of cmds in order..
        self.langmap = {}

    def getTime(self, relativedays=0):
        now = datetime.now()
        now += timedelta(days=relativedays)
        return now
    
    def getTimeString(self, relativedays=0):
        now = self.getTime(relativedays)
        return now.strftime('%Y%m%d_%H%M%S')

    def write_plain(self, lang, text):
      #write to transcript file.  
      #for now just one time param.  

      today = datetime.now().strftime("%Y%m%d")
      folder = '../transcripts/' + lang + '/'
      os.makedirs(folder, exist_ok=True)
      with open(folder + today + '.txt', 'a', encoding='utf-8') as f:        
        f.write(f'{text}\n') 

    def write(self, lang, command, params):
      #write to transcript file.  
      #for now just one time param.  

      today = datetime.now().strftime("%Y%m%d")
      folder = '../transcripts/' + lang + '/'
      os.makedirs(folder, exist_ok=True)
      #add utf-8?  
      ret = ""
      with open(folder + today + '.txt', 'a', encoding='utf-8') as f:        
        if (lang not in self.langmap or self.langmap[lang] != lang):
            self.langmap[lang] = lang
            ret += f'<<{lang}>>\n'
        ret += f'> {command}\n'
        vars = {}
        for pkey, p in params.items():
            #replace any \ndefstring with \n defstring to avoid confusion.            
            pattern = r"\n(" + self.defstring + r")" 
            #for now ok, really want \n$ or \n> to break.  
#            print(p)
            if (isinstance(p, str)):
                p = re.sub(pattern, r"\n \1", p) #untested..

            ret += f'$${pkey}={p}\n'
        if ('TIME' not in params):
            ret += f'$$TIME={self.getTimeString()}\n'
        ret += f'$$\n'
        f.write(ret)
        #dont worry about duplication at this point.
        return ret

    def get_cmd(self, type, command, vars):
        t = time.time()
        if ('TIME' in vars):
            timestr = vars['TIME']
            try: 
                t = time.mktime(datetime.strptime(timestr, '%Y%m%d_%H%M%S').timetuple())
            except:
                pass

        lines = []
        return {'type': type, 'cmd': command, 'vars': vars, 'lines': lines, 'timestamp': t}


    def read_existing(self, lang, start_time=None, end_time=None):
        logger.info(f'Using cached commands for {lang} from {self.allcmds[lang]["start_time"]} to {self.allcmds[lang]["end_time"]}')
        #find startidx
        increment = 1
        if (start_time < self.allcmds[lang]['start_time']):
            start_idx = self.allcmds[lang]['start_idx']
            for (i, cmd) in enumerate(reversed(self.allcmds[lang]['cmds'][:start_idx])):
                if (cmd['timestamp'] <= start_time.timestamp()):
                    start_idx -= 1
                else:
                    break
        else:
            start_idx = self.allcmds[lang]['start_idx']
            for (i, cmd) in enumerate(self.allcmds[lang]['cmds'][start_idx:]):
                if (cmd['timestamp'] >= start_time.timestamp()):
                    start_idx += 1
                else:
                    break   
        
        if (end_time < self.allcmds[lang]['start_time']):
            end_idx = self.allcmds[lang]['end_idx']
            for (i, cmd) in enumerate(reversed(self.allcmds[lang]['cmds'][:end_idx])):
                if (cmd['timestamp'] <= end_time.timestamp()):
                    end_idx -= 1
                else:
                    break
        else:
            end_idx = self.allcmds[lang]['end_idx']
            for (i, cmd) in enumerate(self.allcmds[lang]['cmds'][end_idx:]):
                if (cmd['timestamp'] >= end_time.timestamp()):
                    end_idx += 1
                else:
                    break
        return self.allcmds[lang]['cmds'][start_idx:end_idx]

    def read(self, lang, start_time=None, end_time=None, myfolder=""):

      #read from transcript file all instances of this.   
        if (start_time is None):
            start_time = self.getTime(-30)  #default last 30 days
        if (end_time is None):
            end_time = self.getTime()
        logger.info(f'Loading {lang} {myfolder} start {start_time} to {end_time}')

        if (lang in self.allcmds and self.allcmds[lang]['start_time'] <= start_time and self.allcmds[lang]['end_time'] >= end_time):
            return self.read_existing(lang, start_time, end_time) #get existing cmds..
        
        #list all files in directory
        folder = '../transcripts/' + lang + '/'
        if (myfolder != ""):
            folder = myfolder
        os.makedirs(folder, exist_ok=True)

        files = [f for f in os.listdir(folder) if os.path.getmtime(folder + f) >= start_time.timestamp() and os.path.getctime(folder + f) <= end_time.timestamp()]

        sorted_files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(folder, f))) #sort by modification time, oldest first.  could also sort by creation time if needed.
        numloaded = 0
        print('Reading transcripts from:')
        print(sorted_files)
        ret = []
        currentcmd = ""
        currenttopc = None
        vars = {}
        topc = None
        last_time = start_time.timestamp()
        mtime = None
        for f in sorted_files:
    #      if (f.startswith(yesterday) or f.startswith(today)):
            if (f.endswith('.txt')): #dont open wav files.. maybe rethink sharing directory..
                #get name without extension
                if (mtime is not None and mtime > last_time):
                    last_time = mtime

                mtime = os.path.getmtime(folder + f)

                try:
                    with open(folder + f, encoding='utf-8') as ff:
                        lines = ff.readlines()
                        numlines = len(lines)
                        for idx, line in enumerate(lines):
                            #add bookmark manually.  
                            if (len(line) < 2):
                                continue
                            type = line[0:2]
                            if (type=='**'):
                                #topic definition.  
                                #use file modification time for the time being..
                                #get days since last file mod time.  
                                daysdiff = 0
                                if (last_time is not None):
                                    daysdiff = mtime - last_time
                                    daysdiff = int(daysdiff / 86400)
                                pdays = ((numlines - idx) / numlines) * daysdiff
                                now = datetime.fromtimestamp(mtime)
                                relativedays = -int(pdays)
                                now += timedelta(days=relativedays)
                                topc = self.get_cmd(type, line[2:].strip(), {'TIME': now.strftime('%Y%m%d_%H%M%S')})
                                ret.append(topc)
                                currenttopc = topc
                            else:
                                if (topc is not None and 'lines' in topc):
                                    topc['lines'].append(line)

                            if (type == '> '):
                                #command line internal command
                                if (currentcmd != ""):
                                    #save previous command if exists with no params..
                                    c = self.get_cmd(type, currentcmd, vars)
                                    ret.append(c)
                                currentcmd = line[2:].strip()
                                vars = {}
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
                                    if (len(parts) >= 2):
                                        key = parts[0]
                                        #in case we have = within the value..
                                        value = "".join(parts[1:]).strip()
                                        vars[key] = value

                                        #add to topic as well..                                        
                                        if (currenttopc is not None and 'vars' in currenttopc):
                                            currenttopc['vars'][key] = value

                except Exception as e:
                    logger.error(f'!!> Read [{f}]\n !!{e}\n')

                if (currentcmd != ""):
                    type = '> '
                    c = self.get_cmd(type, currentcmd, vars)
                    ret.append(c)
                    currentcmd = ""
                    vars = {}
                last_time = mtime
                numloaded += 1
        ret.sort(key=lambda x: x['timestamp']) #sort by timestamp just in case.

        self.allcmds[lang] = {'cmds': ret, 'start_time': start_time, 'end_time': end_time, 'start_idx': 0, 'end_idx': len(ret)-1}
        logger.info(f'Loaded {numloaded} files for {lang} with {len(ret)} commands')
        return ret
