#transcribe commands into timeline.
from datetime import datetime, timedelta
import os
import logging
import time
import pathlib
import re

import mido
import sys
import ast

#Local imports
sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
import config 
import mykeys

import networkx as nx

from multiprocessing.shared_memory import SharedMemory
import mmap


logger = logging.getLogger(__name__)


class transcriber:
    def __init__(self, lang_helper=None, mk=None, qr_queue=None):
        self.lang_helper = lang_helper
        self.defstring = r"[~!@#$%^&*<>/:;\-\+=]"
        self.BOOK_FOLDER = '../books/'
        self.TRANSCRIPT_FOLDER = '../transcripts/'
        self.allcmds = {} #lang -> {cmds, start_time, end_time, list of cmds in order..
        self.langmap = {}
        self.kg = {}
        self.allmidi = []
        self.fuzzmap = {} #store fuzz scores for midi search to avoid redundant calculations, since we may want to sort by score later.
        self.qr_queue = qr_queue
        self.mykeys = mk
        self.mydic = {}
        self.typedefmap = {}

        self.allneedles = []
        self.current_topic = None
        self.current_context = None
        self.current_book = None

        self.kg_ignorevars = ['TIME', 'WINDOW', 'START', 'END', 'FNAME', 'FILE', 'DURATION', 'LAG'] #vars to ignore in display of info, used for time window commands.

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
      folder = self.TRANSCRIPT_FOLDER + lang + '/'
      os.makedirs(folder, exist_ok=True)
      with open(folder + today + '.txt', 'a', encoding='utf-8') as f:        
        f.write(f'{text}\n') 

    def speak(self, lang, command, params, save=False):
      ret = ""
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
      return ret



    def write_topic(self, lang, topic="", extra="", saveTranscript=True, saveBook=False):

        ret = ""
        today = datetime.now().strftime("%Y%m%d")
        if (topic == ""):
            topic = self.current_topic
        if (topic != self.current_topic and topic is not None):                
            ret += f'**{topic}\n'
            ret += f'$$TIME={self.getTimeString()}\n'

            self.current_topic = topic

        if (extra != ""):
            ret += f'<<{lang}>>\n{extra}\n'
            if (topic not in self.langmap[lang]['topics']):
                self.langmap[lang]['topics'][topic] = {'mem': self.get_context_memory(f'{topic}', size=10*1024), 'extra': extra, 'data': []} 
            mybytes = extra.encode('utf-8')

            file_path = pathlib.Path(f'temp/{topic}')
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(f'temp/{topic}', 'w', encoding='utf-8') as f:
                f.write(extra)
            self.write_context_memory(self.langmap[lang]['topics'][topic]['mem'], extra) #store extra info in shared memory for access by other processes if needed.  could also store in a file or database if needed, but for now just use shared memory for simplicity.  need to manage memory usage and cleanup as needed.
            #self.langmap[lang]['topics'][topic]['mem'].buf[:len(mybytes)] = mybytes #store extra info in shared memory 

            if (saveBook):
                #write to permanent topic
                #write to permanent selected book/topic..
                if (self.current_book is not None):
                    topicstr = ""
                    if (self.current_book not in self.langmap):
                        self.langmap[self.current_book] = {'lang':self.current_book, 'topic': topic, 'topics': {}, 'kg': nx.Graph()}
                        topicstr = f'**{topic}'
                    try:
                        file_path = pathlib.Path(f'{self.BOOK_FOLDER}{self.current_book}')
                        # Create parent directories if they don't exist
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(f'{self.BOOK_FOLDER}{self.current_book}/{today}.txt', 'a', encoding='utf-8') as f:
                            if (topic != self.langmap[self.current_book]['topic']):
                                topicstr = f'**{topic}'
                            if (topicstr != ""): #had to change topics..
                                f.write(topicstr + '\n')
                            f.write(extra + '\n')
                        self.langmap[self.current_book]['topic'] = topic
                    except Exception as e:
                        logger.error(f'Error writing to book file for current book {self.current_book}: {e}')
                    #write also to topic file
                    if (topic not in self.langmap):
                        self.langmap[topic] = {'lang':topic, 'topic': self.current_book, 'topics': {}, 'kg': nx.Graph()}
                        topicstr = f'**{self.current_book}'
                    elif (self.langmap[topic]['topic'] == self.current_book):
                        topicstr = "" #dont rewrite topic if its the same as current book, to avoid confusion in topic history.
                    try:
                        file_path = pathlib.Path(f'{self.BOOK_FOLDER}{topic}')
                        # Create parent directories if they don't exist
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(f'{self.BOOK_FOLDER}{topic}/{today}.txt', 'a', encoding='utf-8') as f:
                            if (topicstr != ""): #had to change topics..
                                topicstr = f'**{self.current_book}'
                                f.write(topicstr + '\n')
                            f.write(extra + '\n')
                            #dont worry about time of day for this, not worth the space..
                    except Exception as e:
                        logger.error(f'Error writing to book file for topic {topic}: {e}')

        if saveTranscript:
            
            folder = self.TRANSCRIPT_FOLDER + lang + '/'
            os.makedirs(folder, exist_ok=True)
            with open(folder + today + '.txt', 'a', encoding='utf-8') as f:
                f.write(ret)


        return ret

    #    
    def write(self, lang, command, params, topic=None, save=True):
      #write to transcript file.  
      #for now just one time param.  
      if (topic is None):
        topic = self.current_topic
      else:
        if (save):
            self.current_topic = topic
            print('Updating current topic to ' + topic)
      #add utf-8?  
      ret = ""
      if (lang not in self.langmap or self.langmap[lang]['lang'] != lang):
        self.langmap[lang] = {'lang':lang, 'topic': topic, 'topics': {}, 'kg': nx.Graph()}
        ret += f'<<{lang}>>\n'
        ret += f'**{topic}\n'
      elif (self.langmap[lang]['topic'] is not None and self.langmap[lang]['topic'] != topic):
        if (save): #dual purpose.. save to file and save current topic in langmap for future reference.  OK for now..
            self.langmap[lang]['topic'] = topic
        ret += f'**{topic}\n'
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
        folder = self.TRANSCRIPT_FOLDER + lang + '/'
        os.makedirs(folder, exist_ok=True)
        with open(folder + today + '.txt', 'a', encoding='utf-8') as f:
          f.write(ret)
        #dont worry about duplication at this point.
      return ret


    #filter for just this topic
    def filter_topics(self, lang, topics, type='**'):
        ret = []
        topiccmds = self.read_existing(lang) #get existing cmds..
        for idx, cmd in enumerate(topiccmds):
            if (cmd['type'] == type and cmd['topic'] in topics):
                ret.append(cmd)
#        ret.sort(key=lambda x: x['timestamp']) #sort by timestamp just in case, should be sorted..
        return ret

    def read_existing(self, lang, start_time=None, end_time=None):
        logger.info(f'Using cached commands for {lang} from {self.allcmds[lang]["start_time"]} to {self.allcmds[lang]["end_time"]}')
        #find startidx
        if (start_time is None):
            if (lang in self.allcmds and 'start_time' in self.allcmds[lang]):
                start_time = self.allcmds[lang]['start_time']
                end_time = self.allcmds[lang]['end_time']
            else:
                start_time = self.getTime(-30) #default to last 30 days, should be close enough for sorting topics.
                end_time = self.getTime()
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
        
        if (end_time < self.allcmds[lang]['end_time']):
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
#        self.current_topic = self.allcmds[lang]['cmds'][end_idx-1]['topic'] if end_idx > 0 else self.current_topic
        if (end_idx >= len(self.allcmds[lang]['cmds'])):
            end_idx = len(self.allcmds[lang]['cmds'])-1
        if (start_idx > end_idx):
            start_idx = end_idx
        if (start_idx < 0):
            start_idx = 0
        if (end_idx < 0):
            end_idx = 0


        self.allcmds[lang]['start_idx'] = start_idx
        self.allcmds[lang]['end_idx'] = end_idx
        return self.allcmds[lang]['cmds'][start_idx:end_idx]

    def search_midi(self, midiarray, current_time):
        #search for similar key structures
        similar = []
        self.fuzzmap = {} #store fuzz scores for each item to avoid redundant calculations, since we may want to sort by score later.
        #for now reset each time we search..
        print(f'Searching {len(self.allmidi['midi'])} MIDI for {str(midiarray)} at time {datetime.fromtimestamp(current_time).isoformat()}')
        lag = time.time()
        for item in self.allmidi['midi']:
            timestamp = item['timestamp']
            notes = item['notes']
            #binary levenshtein or similar between midiarray and notes, for now just check if any keys match for simplicity.
            #search levenshtein distance and location..
            from rapidfuzz import fuzz
            ff = fuzz.partial_ratio_alignment(midiarray, notes)
            self.fuzzmap[timestamp] = ff
            #can be negative in rare cases with very short files..
            lengthscore = 1 - (len(midiarray) / (1+len(notes)))
            lengthscore *= 100
            #time score based on distance from current time, with a decay based on window size, so items within the window have a higher score, and items outside the window have a lower score.  could adjust this formula as needed.
            timescore = max(0, 1 - abs(current_time - timestamp) / (self.allmidi['end_time'] - self.allmidi['start_time']).total_seconds()) 
            timescore *= 100 #scale to 100 to match fuzz score, could adjust as needed.

            #get time from timestamp and notes.  for now forgoe this calculation..
            mystart = ff.dest_start if ff.dest_start is not None else 0
            transcript = self.mykeys.seq2text(notes[mystart:]) if self.mykeys is not None else "" #get transcript text for these notes if possible, could be useful for display and searching later, but for now just get the keys.
            similar.append({'timestamp': timestamp, 'notes': notes, 'transcript': transcript, 'score': ff.score * 0.7 + lengthscore * 0.1 + timescore * 0.2, 'start': ff.dest_start}) #combine fuzz score, length score, and time score, with weights of 0.7, 0.1, and 0.2 respectively, could adjust as needed.
        
        similar.sort(key=lambda x: x['score'], reverse=True)
        print(f'LAG: {time.time() - lag} seconds to search MIDI')        
        return similar[:10] #return first 10 top 10 for now, could adjust as needed.

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
                    if (act):
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
            folder = self.TRANSCRIPT_FOLDER + str(y) + '/'
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
                            if (hasattr(msg, 'type') and msg.type == 'note_on'):
                                notes.append(msg.note) #no time/velocity for simplicity in searching..

                    except Exception as e:
                        logger.error(f'!!> Read {f}\n !!{e}\n')
                        continue
                        
                    last_time = ctime
                    numloaded += 1
                    ret.append({'timestamp': round(ctime), 'notes': notes, 'msgs': msgs})

        logger.info(f'MIDI Loaded {numloaded} files')
        self.allmidi = {'midi': ret, 'start_time': start_time, 'end_time': end_time}
        #maybe want to play these back in order to associate with words in the transcript, but for now just load and search as needed.  could also do some processing here to extract any text info from the midi files if available, but for now just get the keys and timestamps.
#        self.play_midi(ret, act=False) #get words without acting on them, to associate with midi data.
            
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


    def get_time_var(self, vars):
        t = time.time()
        if ('TIME' in vars):
            timestr = vars['TIME']
            try: 
                if (timestr.isdigit()):
                    #assume its a timestamp in seconds.
                    t = float(timestr)
                elif (timestr[8] == '_' and timestr.replace('_', '').isdigit()):
                    t = time.mktime(datetime.strptime(timestr, '%Y%m%d_%H%M%S').timetuple())
            except:
                pass
        return t
    def get_cmd(self, lang, type, command, vars):
        t = self.get_time_var(vars)

        lines = []
        return {'lang': lang, 'type': type, 'cmd': command, 'topic': self.current_topic, 'vars': vars, 'lines': lines, 'timestamp': t}


    def get_seq(self, command):
        #for now just return command, but could do some parsing here to extract variables if needed.  
        #could also do some normalization here if needed.  
        #potentially want to extract variables here as well, but for now just pass raw command and vars in get_cmd.
        seq = []
        vars = {}
        sp = command.find('[')
        ep = command.rfind(']')
        if (sp != -1 and ep != -1 and ep > sp):
            #has embedded variable, parse out and add to vars.
            varstr = command[sp+1:ep]
            command = command[:sp].strip() #remove assumed white space
            seq = varstr.split(',')
            for (i, s) in enumerate(seq):
                try:
                    seq[i] = int(s)

                except ValueError:
                    try:
                        seq[i] = float(s)
                    except ValueError:
                        #keep as string, not worth to check white space
                        seq[i] = s                        
                    pass

            vars['SEQ'] = seq #can be strings, for now prioritize numbers

        return command, seq
    


        
    def read_lines(self, lang, lines, last_time=None, mtime=None):
        ret = []
        currentcmd = ""
        currentcmdobj = None
        currenttopc = None
        if (mtime is None):
            mtime = time.time()
            last_time = mtime - 86400 #default to last 24 hours if no time provided, should be close enough for sorting topics.

        if (lang not in self.langmap or self.langmap[lang]['lang'] != lang):
            self.langmap[lang] = {'lang':lang, 'topic': self.current_topic, 'topics': {}, 'kg': nx.Graph()} 

        vars = {}
        topc = None
        numlines = len(lines)
        now = datetime.fromtimestamp(mtime)
        daysdiff = 0
        if (last_time is not None):
            daysdiff = mtime - last_time
            daysdiff = int(daysdiff / 86400)
        pdays = (1 / numlines) * daysdiff
        now += timedelta(days=-daysdiff) #start at last_time and increment by pdays for each line, so we can have a timestamp for each line even if they dont have one explicitly.  could be useful for sorting topics/commands later.  not perfect, but should be good enough for now.  ideally would want to parse out actual timestamps from lines if available, but this is a start.
        for idx, line in enumerate(lines):
            now += timedelta(days=pdays)
            #add bookmark manually.  
            if (len(line) < 2):
                continue
            type = line[0:2]
            if (type=='**'):
                #topic definition.  
                #use file modification time for the time being..
                #get days since last file mod time.  
                self.current_topic = line[2:].strip() #update current topic to this topic. then get_cmd with new topic.
                topc = self.get_cmd(lang, type, line[2:].strip(), {'TIME': now.strftime('%Y%m%d_%H%M%S')})
                logger.info(f'Adding topic {topc["cmd"]} with vars {topc["vars"]}')
                ret.append(topc)
                currenttopc = topc
            else:
                if (topc is not None and 'lines' in topc):
                    topc['lines'].append(line)
                if (currentcmdobj is not None and 'lines' in currentcmdobj):
                    currentcmdobj['lines'].append(line)

            if (type == '> '):
                #command line internal command
                if (currentcmd != ""):
                    #save previous command if exists with no params..
#                                    c = self.get_cmd(lang, type, currentcmd, vars)
#                                    ret.append(c)
                    ret.append(currentcmdobj)
                    currentcmd = ""
                    currentcmdobj = None

                currentcmd = line[2:].strip()
                currentcmd,seq = self.get_seq(currentcmd)
                currentcmdobj = self.get_cmd(lang, type, currentcmd, {'TIME': now.strftime('%Y%m%d_%H%M%S'), 'SEQ': seq})
                currentcmdobj['lines'].append(line)
                vars = {}
            if (type == '$$'):
                #special trey data line
                if (len(line) == 2):
                    #execute command
                    if (currentcmd != ""):
                        type = '> '
                        ret.append(currentcmdobj)

#                                    c = self.get_cmd(lang, type, currentcmd, vars)
#                                    ret.append(c)
#                    logger.info(f'Adding QR {type}: {currentcmd}')
                    currentcmd = ""
                    currentcmdobj = None
                    vars = {}

                else:
                    parts = line[2:].split('=')
                    if (len(parts) >= 2):
                        key = parts[0]
                        #in case we have = within the value..
                        value = "".join(parts[1:]).strip()
                        vars[key] = value

                        #prioritize vars here.  
                        #not really notable..  
                        if (currentcmdobj is not None and 'vars' in currentcmdobj):
                            currentcmdobj['vars'][key] = value
                            if (key == 'TIME'):
                                currentcmdobj['timestamp'] = self.get_time_var(vars)

                        #add to topic as well..                                        
                        elif (currenttopc is not None and 'vars' in currenttopc):
                            currenttopc['vars'][key] = value
                            if (key == 'TIME'):
                                currenttopc['timestamp'] = self.get_time_var(vars)

        if (currentcmd != "" and currentcmdobj is not None):
            ret.append(currentcmdobj)
            print(f'Adding final command {currentcmd} with vars {vars}')

        return ret


    #not used at the moment, but best if we put into dot lang as well probably..
    def gen_DOT(self, cmds):
        #for now just generate a DOT file for the knowledge graph, could also generate for individual topics or languages if needed.  
        dot = "digraph G {\n"
        for cmd in cmds:
            cmd_node = f'"{cmd["cmd"]}"'

            dot += f'{cmd["type"]}{cmd_node} [topic="{cmd["topic"]}", lang="{cmd["lang"]}"];\n'

            for var_key, var_value in cmd['vars'].items():
                var_node = f'"{var_key}={var_value}"'
                topic = cmd["topic"] if cmd["topic"] is not None else "None"
                dot += f'  {var_node} [topic="{topic}", lang="{cmd["lang"]}"];\n'
                dot += f'  {cmd_node} -> {var_node} [label="$$"];\n'
                dot += f'  {topic} -> {var_node} [label="$$"];\n'
        dot += "}\n"
        #nx.nx_pydot.from_pydot(PG)
        return dot
    
    def update_kg(self, lang, cmds):
        #for now just add commands and topics as nodes, and edges between topics and commands, and commands and their variables.  could also add edges between commands based on sequence in transcript, but for now just direct edges to topic and variables.
        for idx, cmd in enumerate(cmds):
            #add to array.  
            if (cmd['topic'] not in self.langmap[lang]['topics']):
                self.langmap[lang]['topics'][cmd['topic']] = {'mem': self.get_context_memory(f'{cmd["topic"]}', size=10*1024), 'extra': "", 'data': []} #store extra info in langmap for reference, and also store in shared memory for access by other processes if needed.  could also store in a file or database if needed, but for now just use shared memory for simplicity.  need to manage memory usage and cleanup as needed, but for now just create a new block for each topic and overwrite as needed.
            self.langmap[lang]['topics'][cmd['topic']]['data'].append(cmd) #store topic data in langmap for reference, could be useful for display and searching later, but for now just store in memory.  could also store in shared memory or a file/database if needed.

            if ('**' not in self.kg):
                self.kg['**'] = nx.Graph()
            if (cmd['type'] not in self.kg):
                self.kg[cmd['type']] = nx.Graph()
            #add topics and cmds..
            self.kg[cmd['type']].add_node(cmd['cmd'], label=cmd['type']+cmd['cmd'], type=cmd['type'], lang=cmd['lang'], topic=cmd['topic'])
            for var_key, var_value in cmd['vars'].items():
                if (var_key in self.kg_ignorevars):
                    continue
                var_node = f"{var_key}={var_value}"
                self.kg[cmd['type']].add_node(var_node, label=var_node, type='$$', lang=cmd['lang'], cmd=cmd['cmd'], topic=cmd['topic'])
                self.kg[cmd['type']].add_edge(cmd['cmd'], var_node, type='$$')
                if (cmd['topic'] is not None):
                    if (not self.kg['**'].has_node(cmd['topic'])):
                        self.kg['**'].add_node(cmd['topic'], label=cmd['topic'], type='**', lang=cmd['lang'], topic=cmd['topic'])
                    self.kg['**'].add_node(cmd['topic'], label=cmd['topic'], type='**', lang=cmd['lang'], topic=cmd['topic'])
                    self.kg['**'].add_edge(cmd['topic'], var_node, type='$$')
            if (idx > 0):
                for prev_idx in range(max(0, idx-5), idx-1): #add edges to previous 5 commands for context, could adjust this number as needed.
                    self.kg[cmd['type']].add_edge(cmds[prev_idx]['cmd'], cmd['cmd'], type=cmd['type'], topic=cmd['topic'], lang=cmd['lang'])


    def get_kg_DOT(self, type):
        if (type not in self.kg):
            return ""
        dot = nx.nx_pydot.to_pydot(self.kg[type]).to_string()
        return dot

    def is_yyyymmdd(self, date_text):
        try:
            # %Y = 4-digit year, %m = 2-digit month, %d = 2-digit day
            datetime.strptime(date_text, "%Y%m%d")
            return True
        except ValueError:
            return False
        

    def write_context_memory(self, contextmemory, data):
        #write data to shared memory block, with some basic management to avoid overflow.  for now just overwrite from the beginning if we exceed the size, but could implement a more sophisticated approach if needed.  need to manage memory usage and cleanup as needed, but for now just write to the block and overwrite as needed.
        """
        mybytes = data.encode('utf-8')
        if (len(mybytes) > contextmemory.size):
            logger.warning(f'Context memory overflow: data size {len(mybytes)} exceeds block size {contextmemory.size}, truncating data')
            mybytes = mybytes[:contextmemory.size] #truncate data to fit in block
        contextmemory.buf[:len(mybytes)] = mybytes
        """
        #use mmap
        with open(contextmemory, "r+b") as f:
            # memory-map the file, size 0 means whole file
            mm = mmap.mmap(f.fileno(), 0)
            # read content via standard file methods
            mdata = data.encode('utf-8')
            mm[:len(mdata)] = mdata

            mm.close()        

    def get_context_memory(self, name, size=1024*1024):
        # 1. Attempt to create a new shared memory block
        name = name.replace('\\', '/')
        if (name.startswith('/')):
            name = name[1:] #remove leading slash if present
        return name
#            return SharedMemory(name=name, create=True, size=size)



    def close_book(self, bookname, folder = "books"):
        #for now clear from alllangs.  
        if (bookname in self.allcmds):
            #for now no clearing, just mark as closed for searches..
            self.allcmds[bookname]['open'] = False
        
    def open_book(self, bookname, start_time, end_time, folder = "books"):
        #for now just read the book and return the text, but could also do some processing here to extract relevant sections or create embeddings for searching later.  could also store in shared memory or a file/database if needed, but for now just read and return the text.
        try:
            self.read(bookname, start_time=start_time, end_time=end_time, myfolder=bookname) #load book into transcripts for reference, this will also update the knowledge graph with any topics/commands found in the book, which can be useful for searching and display later.  could also do some processing here to extract relevant sections or create embeddings for searching later, but for now just load and return the text.

        except Exception as e:
            logger.error(f'!!> Open book [{bookname}]\n !!{e}\n')

        
    def get_from_nested(self, data_dict, key_list):
        try:
            for key in key_list:
                data_dict = data_dict[key]
        except KeyError:
            return None
        return data_dict

    def get_single_book(self, folder="books"):
        book = self.get_from_nested(self.allbooks, folder.split('/'))
        if (book is not None and '&&' in book and book['&&'] is not None):
            return self.read_existing(book['&&']['**'])
        
    def get_chromatic(self, struct, start_time=None, end_time=None):
        #get chromatic cmds from this struct, which is a nested dict with '&&' for cmds and subfolders for nested books.  this will allow us to get all cmds from a book and its subbooks recursively, with optional time filtering.  could also add topic filtering if needed, but for now just get all cmds.
        ret = []
        if (struct is None):
            return ret
        for s in struct:
            if (s['cmds'] is not None and s['start_idx'] != s['end_idx']):
                ret.extend(s['cmds'][s['start_idx']:s['end_idx']]) #get cmds for this struct, which should already be filtered by time in read_existing, so we can just get the cmds between start_idx and end_idx.  could also add topic filtering here if needed, but for now just get all cmds.

        return ret
    def filter_books_recursive(self, folder="books", searchbooks=None, start_time=None, end_time=None):
        #get just name here..
        if (searchbooks is None):
            tree = folder.split('/')
            searchbooks = self.get_from_nested(self.allbooks, tree)
        if (searchbooks is None):
            return []
        retstruct = []
        for k,v in searchbooks.items():
            if (k == '&&' or k == '**'):
                continue
            retstruct.extend(self.filter_books_recursive(folder+"/"+k, searchbooks=v, start_time=start_time, end_time=end_time))
        if (searchbooks['&&'] is not None):            
            self.read_existing(searchbooks['&&']['**'], start_time=start_time, end_time=end_time) #get existing cmds filter time..
            if (searchbooks['&&']['cmds'] is not None and searchbooks['&&']['start_idx'] != searchbooks['&&']['end_idx']):
                retstruct.append(searchbooks['&&']) #get existing cmds with filtered time..

            
        return retstruct
    
    def open_books(self, folder="books", days=365):
        #check recursively and if there are any files in the folder, open them as books.  
        #only include the immediate files in the book.  
        #closing book will close all subbooks as well for now..

        retstruct = {'&&': None}
        #get just name here..
        subfolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]
        for subfolder in subfolders:
            logger.info(f'Opening book {subfolder} from folder {folder}')
            print(f'Opening book {subfolder} from folder {folder}')
            bookname = subfolder #books/worldhistory/worldwar2/YYYYmmdd.txt
            #retstruct = books['worldhistory']['worldwar2']['&&'] #get cmd struct for this subbook..
            #if we have other subfolders, load them..
            retstruct[subfolder] = self.open_books(folder+"/"+subfolder) #recursively open subbooks as well, this will allow for nested book structures
            #load data for this book..
        retstruct['&&'] = self.open_book(folder, start_time=self.getTime(-days), end_time=self.getTime(), folder=folder) #open all books with last year of data, could adjust as needed.
        return retstruct

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
        folder = self.TRANSCRIPT_FOLDER + lang + '/'
        if (myfolder != ""):
            folder = myfolder
        os.makedirs(folder, exist_ok=True)

                

        files = [f for f in os.listdir(folder) if os.path.getmtime(folder + f) >= start_time.timestamp() and os.path.getctime(folder + f) <= end_time.timestamp()]

        sorted_files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(folder, f))) #sort by modification time, oldest first.  could also sort by creation time if needed.
        numloaded = 0
        print(f'Reading {lang} transcripts from:')
        print(sorted_files)
        ret = []
        currentcmd = ""
        currentcmdobj = None
        currenttopc = None

        vars = {}
        topc = None
        last_time = start_time.timestamp()
        mtime = None
        last_mtime = None
        for f in sorted_files:
    #      if (f.startswith(yesterday) or f.startswith(today)):
            if (f.endswith('.txt')): #dont open wav files.. maybe rethink sharing directory..
                #get name without extension

                if (self.is_yyyymmdd(f[:8])):
                    mtime = time.mktime(datetime.strptime(f[:8], '%Y%m%d').timetuple())
                    mtime += 86400 #add one day to end of day for better sorting
                else:
                    mtime = os.path.getmtime(folder + f)

                last_mtime = mtime
                if (mtime < last_time):
                    last_time = mtime - 86400 #set to start of day if we have data issue..

                try:
                    with open(folder + f, encoding='utf-8') as ff:
                        lines = ff.readlines()
                        if (len(lines) < 2):
                            continue

                        self.current_topic = f[:-4] #file name without extension
                        test = self.read_lines(lang, lines, last_time, mtime)
                        ret.extend(test) 
                        logger.info(f)                       
#                        logger.info(test)
                except Exception as e:
                    logger.error(f'!!> Read [{f}]\n !!{e}\n')

                last_time = mtime
                numloaded += 1

        ret.sort(key=lambda x: x['timestamp']) #sort by timestamp just in case.

        self.allcmds[lang] = {'**': lang, 'cmds': ret, 'last_mtime': last_mtime, 'start_time': start_time, 'end_time': end_time, 'start_idx': 0, 'end_idx': len(ret)-1, 'open': True}
        self.update_kg(lang, ret)
        logger.info(f'Loaded {numloaded} files for {lang} with {len(ret)} commands')
        return ret
