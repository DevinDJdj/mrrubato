#transcribe commands into timeline.
from datetime import datetime, timedelta
import os
import logging
import time
import pathlib
import re

import mido
import sys

#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
import config 
import mykeys

logger = logging.getLogger(__name__)


class transcriber:
    def __init__(self, lang_helper=None, mk=None, qr_queue=None):
        self.lang_helper = lang_helper
        self.defstring = r"[~!@#$%^&*<>/:;\-\+=]"
        self.allcmds = {} #lang -> {cmds, start_time, end_time, list of cmds in order..
        self.langmap = {}
        self.allmidi = []
        self.qr_queue = qr_queue
        self.mykeys = mk
        self.mydic = {}
        self.allneedles = []
        if (self.mykeys is not None):
            allwords = self.mykeys.get_words_()
            for i, w in enumerate(allwords):            
                keys = w['keys']
                strkeys = ','.join(str(k) for k in keys)
                if (str(len(keys)) not in self.mydic):
                    self.mydic[str(len(keys))] = {}
                self.mydic[str(len(keys))][strkeys] = {'w': w['word'], 'l': w['lang'], 'k': keys, 'cnt': 0, 'vars': {}}
                if (len(keys) > 1): #dont search single for now..
                    self.allneedles.append(strkeys)

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

    def write(self, lang, command, params, save=True):
      #write to transcript file.  
      #for now just one time param.  

      #add utf-8?  
      ret = ""
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

      if save:
        today = datetime.now().strftime("%Y%m%d")
        folder = '../transcripts/' + lang + '/'
        os.makedirs(folder, exist_ok=True)
        with open(folder + today + '.txt', 'a', encoding='utf-8') as f:
          f.write(ret)
        #dont worry about duplication at this point.
      return ret

    def get_cmd(self, lang, type, command, vars):
        t = time.time()
        if ('TIME' in vars):
            timestr = vars['TIME']
            try: 
                t = time.mktime(datetime.strptime(timestr, '%Y%m%d_%H%M%S').timetuple())
            except:
                pass

        lines = []
        return {'lang': lang, 'type': type, 'cmd': command, 'vars': vars, 'lines': lines, 'timestamp': t}


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

    def play_midi(self, midi_data, act=True, speed=1.0, volume=1.0):
        #for now just print the notes with timing.  
        if self.mykeys is None:
            return
        for item in midi_data:
            timestamp = item['timestamp']
            notes = item['notes']
            msgs = item['msgs']

            #use mykeys.seq2text to get any text input, where to pass this..
            for msg in msgs:
                if ('type' in msg and (msg.type == 'note_on' or msg.type == 'note_off')):
                    self.mykeys.key(msg.note, msg, None, doact=act)
                    qrdata = self.mykeys.get_qr()
                    if (qrdata is not None and qrdata != ""):
                        #only do this if necessary, too much processing..
                        self.qr_queue.put(qrdata)
        #mykeys.words should include all words..

    def read_midi(self, start_time=None, end_time=None):
        #for now just read from transcript file all instances of this.   
        if (start_time is None):
            start_time = self.getTime(-30)  #default last 30 days
        if (end_time is None):
            end_time = self.getTime()
        logger.info(f'> MIDI Load start {start_time} to {end_time}')
        #list all files in directory
        #get year
        y = start_time.year
        for y in range(start_time.year, end_time.year+1):
            folder = '../transcripts/' + str(y) + '/'
            files = [f for f in os.listdir(folder) if os.path.getmtime(folder + f) >= start_time.timestamp() and os.path.getctime(folder + f) <= end_time.timestamp()]

            sorted_files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(folder, f))) #sort by modification time, oldest first.  could also sort by creation time if needed.
            numloaded = 0
            print(f'MIDI Read: {folder}')
            print(sorted_files)
            ret = []
            last_time = start_time.timestamp()
            ctime = None
            for f in sorted_files:
        #      if (f.startswith(yesterday) or f.startswith(today)):
                if (f.endswith('.mid')): #dont open wav files.. maybe rethink sharing directory..
                    ctime = os.path.getctime(folder + f)

                    try:
                        #read midi file and save as sequence..
                        notes = []
                        msgs = []
                        mid = mido.MidiFile(folder + f)
                        for msg in mid:
                            msgs.append(msg)
                            if ('type' in msg and msg.type == 'note_on'):
                                notes.append(msg.note) #no time/velocity for simplicity in searching..

                    except Exception as e:
                        logger.error(f'!!> Read {f}\n !!{e}\n')
                        continue
                        
                    last_time = ctime
                    numloaded += 1
                    ret.append({'timestamp': ctime, 'notes': notes, 'msgs': msgs})

        logger.info(f'MIDI Loaded {numloaded} files')
        self.allmidi = {'midi': ret, 'start_time': start_time, 'end_time': end_time}
        self.play_midi(ret, act=False) #get words without acting on them, to associate with midi data.
            
        """
        #filter for lang here potentially..
        pattern = '|'.join(map(re.escape, self.allneedles))
        logger.info(f'MIDI Search pattern: {len(pattern)} chars for {len(self.allneedles)} needles')
        for item in ret:
            timestamp = item['timestamp']
            notes = item['notes']
            #self.play_midi([item]) #for now just print the notes with timing.
            #find words..
            strnotes = ','.join(str(n) for n in notes)
#            matches = re.findall(pattern, strnotes) #may get some garbage here, but probably good enough..
            words_with_indices = [(m.start(), m.end(), m.group(0)) for m in re.finditer(pattern, strnotes)]

            print(f'MIDI {datetime.fromtimestamp(timestamp)}: -> words found: {len(words_with_indices)}')
            logger.info(f'MIDI {datetime.fromtimestamp(timestamp)}: -> words found: {len(words_with_indices)}')
            for (start, end, match) in words_with_indices:
                lngth = len(match.split(','))
                if match in self.mydic[str(lngth)]:
                    word_info = self.mydic[str(lngth)][match]
                    word_info['cnt'] += 1
                    #find passed variables.. and add vars data..
        #get all embedded text info and associate with the commands..
        #This function could be problematic with large amounts of data I suspect..
        for lngth, words in self.mydic.items():
            for match, word_info in words.items():
                if (word_info['cnt'] > 0):                    
                    logger.info(f'Word "{word_info["w"]}" found {word_info["cnt"]} times in MIDI data with keys {match} and vars {word_info["vars"]}')
        """
        return ret

    def get_word(self, seq):
        if (str(len(seq)) in self.mydic):
            if self.mydic and str(seq) in self.mydic[str(len(seq))]:
                return self.mydic[str(len(seq))][str(seq)]
        return None
    
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
                                topc = self.get_cmd(lang, type, line[2:].strip(), {'TIME': now.strftime('%Y%m%d_%H%M%S')})
                                ret.append(topc)
                                currenttopc = topc
                            else:
                                if (topc is not None and 'lines' in topc):
                                    topc['lines'].append(line)

                            if (type == '> '):
                                #command line internal command
                                if (currentcmd != ""):
                                    #save previous command if exists with no params..
                                    c = self.get_cmd(lang, type, currentcmd, vars)
                                    ret.append(c)
                                currentcmd = line[2:].strip()
                                vars = {}
                            if (type == '$$'):
                                #special trey data line
                                if (len(line) == 2):
                                    #execute command
                                    if (currentcmd != ""):
                                        type = '> '
                                    c = self.get_cmd(lang, type, currentcmd, vars)
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
                    c = self.get_cmd(lang, type, currentcmd, vars)
                    ret.append(c)
                    currentcmd = ""
                    vars = {}
                last_time = mtime
                numloaded += 1
        ret.sort(key=lambda x: x['timestamp']) #sort by timestamp just in case.

        self.allcmds[lang] = {'cmds': ret, 'start_time': start_time, 'end_time': end_time, 'start_idx': 0, 'end_idx': len(ret)-1}
        logger.info(f'Loaded {numloaded} files for {lang} with {len(ret)} commands')
        return ret
