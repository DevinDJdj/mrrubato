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
from rapidfuzz import fuzz

import languages.helpers.timewindow as timewindow


logger = logging.getLogger(__name__)


class transcriber:
    def __init__(self, lang_helper=None, mk=None, qr_queue=None):
        self.lang_helper = lang_helper
        self.defstring = r"[~!@#$%^&*<>/:;\-\+=]"
        self.BOOK_FOLDER = '../books/' #intentonally use outside of git struct, too much data.  
        #only copy to ./books if really want..
        self.TRANSCRIPT_FOLDER = '../transcripts/'
        self.CTXT_FOLDER = '../ctxt/' #context data for topics, stored in shared memory for now, but could also be stored in files or database as needed.  use shared memory for simplicity and speed, but need to manage memory usage and cleanup as needed.
        self.allcmds = {} #lang -> {cmds, start_time, end_time, list of cmds in order..
        self.langmap = {}
        self.kg = {}
        self.allmidi = []
        self.filtered_topics = []
        self.fuzzmap = {} #store fuzz scores for midi search to avoid redundant calculations, since we may want to sort by score later.
        self.qr_queue = qr_queue
        self.mykeys = mk
        self.mydic = {}
        self.typedefmap = {}
        self.mytime = time.time() #use to search all elements.. search_midi
        self.allneedles = []
        self.current_topic = None
        self.current_context = None
        self.current_book = None
        self.futuretree = None
        self.similar = None
        self.timewindow = timewindow.timewindow(self) #initialize timewindow for transcriber, shared..

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


    def set_current_book(self, book):
        self.current_book = book
        if (self.current_book not in self.langmap):
            self.langmap[self.current_book] = {'lang':self.current_book, 'topic': self.current_topic, 'topics': {}, 'kg': nx.Graph()}

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
                        file_path.mkdir(parents=True, exist_ok=True)
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
                        file_path.mkdir(parents=True, exist_ok=True)
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

      if save: #save to transcript and book(s)
        today = datetime.now().strftime("%Y%m%d")
        folder = self.TRANSCRIPT_FOLDER + lang + '/'
        os.makedirs(folder, exist_ok=True)
        with open(folder + today + '.txt', 'a', encoding='utf-8') as f:
          f.write(ret)
        """
        #dont want to write here except for certain data 
        # --write_topic          
        folder = self.BOOK_FOLDER + topic + '/'
        os.makedirs(folder, exist_ok=True)
        with open(folder + today + '.txt', 'a', encoding='utf-8') as f:
          f.write(ret)

        if (self.current_book is not None):
            folder = self.BOOK_FOLDER + self.current_book + '/'
            os.makedirs(folder, exist_ok=True)
            with open(folder + today + '.txt', 'a', encoding='utf-8') as f:
                f.write(ret)

        #dont worry about duplication at this point, we have 3 copies of the same info but its not a big deal
        # and it simplifies retrieval later.  could optimize this later if needed by tracking what has been written to each book/topic and only writing new info, 
        # but for now just write everything to all relevant files for simplicity.
        """
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

        if (lang not in self.allcmds or len(self.allcmds[lang]['&&']) == 0):
            logger.warning(f'No existing commands for {lang}, returning empty list')
            return []
        
        start_idx = self.allcmds[lang]['start_idx']
        logger.info(f'Finding start index for {start_time} starting at index {start_idx} with cmds {self.allcmds[lang]["&&"]}')
        if (start_time.timestamp() < self.allcmds[lang]['&&'][start_idx]['timestamp']):            
            for (i, cmd) in enumerate(reversed(self.allcmds[lang]['&&'][:start_idx])):
                if (cmd['timestamp'] >= start_time.timestamp()):
                    start_idx -= 1
                else:
                    break
        else:
            for (i, cmd) in enumerate(self.allcmds[lang]['&&'][start_idx:]):
                if (cmd['timestamp'] <= start_time.timestamp()):
                    start_idx += 1
                else:
                    break   
        
        end_idx = self.allcmds[lang]['end_idx']
        if (end_time.timestamp() < self.allcmds[lang]['&&'][end_idx]['timestamp']):
            for (i, cmd) in enumerate(reversed(self.allcmds[lang]['&&'][:end_idx])):
                if (cmd['timestamp'] >= end_time.timestamp()):
                    end_idx -= 1
                else:
                    break
        else:
            for (i, cmd) in enumerate(self.allcmds[lang]['&&'][end_idx:]):
                if (cmd['timestamp'] <= end_time.timestamp()):
                    end_idx += 1
                else:
                    break
#        self.current_topic = self.allcmds[lang]['&&'][end_idx-1]['topic'] if end_idx > 0 else self.current_topic
        if (end_idx >= len(self.allcmds[lang]['&&'])):
            end_idx = len(self.allcmds[lang]['&&'])-1
        if (start_idx > end_idx):
            start_idx = end_idx
        if (start_idx < 0):
            start_idx = 0
        if (end_idx < 0):
            end_idx = 0


        self.allcmds[lang]['start_idx'] = start_idx
        self.allcmds[lang]['end_idx'] = end_idx
        return self.allcmds[lang]['&&'][start_idx:end_idx]

    def search_midi(self, midiarray, current_time):
        #search for similar key structures
        similar = []
        self.fuzzmap = {} #store fuzz scores for each item to avoid redundant calculations, since we may want to sort by score later.
        #for now reset each time we search..
        self.mytime = current_time #update time for referential searches..
        if (self.futuretree is not None):
            #do we need to search midi?  
            #for now do every time..
            words = self.mykeys.get_spoken_words()
            totcount = 0
            for lang, events in self.futuretree.items():
                self.futuretree[lang] = [x for x in self.futuretree[lang] if not (x['..'] == 1)]
                events = self.futuretree[lang]
                for e in events:
                    e['..'] -= 1 #decrement the order in sequence
                    #evaluate if this is still likely based on words_
                    #for now, just return order of words without calculation
                totcount += len(events)

            if (totcount > 5):
                return self.similar
            
        #if dont have enough info..
        print(f'Searching {len(self.allmidi['midi'])} MIDI for {str(midiarray)} at time {datetime.fromtimestamp(current_time).isoformat()}')
        lag = time.time()
        for item in self.allmidi['midi']:
            timestamp = item['timestamp']
            notes = item['notes']
            msgs = item['msgs']
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

            #find seqstart 110 if possible.. dont want to start in middle of transcript      
            prevnotes = notes[:mystart]  #get notes leading up to mystart, which is the start of the matched sequence, and search for last occurrence of 110 in this sublist, which is the EOW note in mykeys, so we can get the transcript text for the sequence leading up to this point if possible, which can be useful for display and searching later.  if not found, will return -1, so we can just use mystart as the start of the sequence in that case.
            prevtranstart = len(prevnotes) - 1 - prevnotes[::-1].index(110) if 110 in prevnotes else -1
            prevtranend = len(prevnotes) - 1 - prevnotes[::-1].index(111) if 111 in prevnotes else -1

#            prevtranstart = notes.rfind(110, 0, mystart) #find last occurrence of note 110 before mystart, which is the EOW note in mykeys, so we can get the transcript text for the sequence leading up to this point if possible, which can be useful for display and searching later.  if not found, will return -1, so we can just use mystart as the start of the sequence in that case.
#            prevtranend = notes.rfind(111, 0, mystart) #find last occurrence of note 111 before mystart, which is the SOW note in mykeys, so we can get the transcript text for the sequence leading up to this point if possible, which can be useful for display and searching later.  if not found, will return -1, so we can just use mystart as the start of the sequence in that case.
            if (prevtranstart != -1 and prevtranstart > prevtranend):
                mystart = prevtranstart


            transcript = self.mykeys.seq2text(notes[mystart:]) if self.mykeys is not None else "" #get transcript text for these notes if possible, could be useful for display and searching later, but for now just get the keys.
            similar.append({'timestamp': timestamp, 'notes': notes, 'msgs': msgs, 'transcript': transcript, 'score': ff.score * 0.7 + lengthscore * 0.1 + timescore * 0.2, 'start': ff.dest_start}) #combine fuzz score, length score, and time score, with weights of 0.7, 0.1, and 0.2 respectively, could adjust as needed.
        
        similar.sort(key=lambda x: x['score'], reverse=True)
        print(f'LAG: {time.time() - lag} seconds to search MIDI')      

        lag = time.time()  

        #generate a next most likely events list..
        futuretree = {}
        self.mykeys.lasttick = time.time() #workaround to indicate we need to process msgs, mykeys object separate from user keys..
        for item in similar[:10]: #just print top 10 for now, could adjust as needed.
            #next sequence..
            #count time..
            #for now assume we get a proper match.. starting after EOW, and assuming we have no mistakes..
            words = self.enscribe(item['notes'][item['start']+50:item['start']+200]) #enscribe next 150 notes after the match, could adjust as needed.

            #here time is not significant..
            #but find time..
            cnt = 0
            timepassed = 0
            #tree
            for msg in item['msgs']:
                timepassed += msg.time /1000.0 #convert to seconds, may need to adjust based on actual timing of midi files, but for now just use this as a rough estimate.
#                print(f'MIDI msg {msg} at time {timepassed} seconds after matched event')
                if hasattr(msg, 'type') and msg.type=='note_on':
                    cnt += 1
                    if (cnt == 50):
                        #now..
                        t = item['timestamp']
                        t += timepassed
                        print(f'Similar event at {datetime.fromtimestamp(t).isoformat()} with score {item["score"]} and transcript "{item["transcript"]}"')                        
                        if (words is not None and len(words) > 0):
                            wcnt = 0
                            for w in words:
                                wcnt += 1
                                lang = w['langna'] if 'langna' in w else 'unknown'
                                if (lang not in futuretree):
                                    futuretree[lang] = []
                                kb = -1
                                if (hasattr(self.mykeys, 'languages') and lang in self.mykeys.languages and hasattr(self.mykeys.languages[lang], 'keybot')):
                                    kb = self.mykeys.languages[lang].keybot
                                if (kb != -1): #usable lang?
                                    futuretree[lang].append({'<<': lang, '..': wcnt, '&&': w['word'], '##': w['ss'], '__': kb})
    
                        #get index for this language..
            item['msgs'] = None #clear msgs to save memory, we have the info we need from them at this point, also causes json.dump issue
            for lang, events in futuretree.items():
                print(f'Next likely events for language {lang}:')
                sorted_events = sorted(events, key=lambda x: x['..']) #sort by order in sequence, which is stored in '..' key, could adjust as needed.
                for e in sorted_events:
                    print(f'> <{e['<<']}>{e["&&"]} [{e["##"]}]')


            #find 
        print(f'LAG2: {time.time() - lag} seconds to process top similar MIDI events')  

        self.futuretree = futuretree #store this for later retrieval if needed, could also write to file or database as needed, but for now just store in memory for simplicity. 
        self.similar = similar[:10] #store top 10 similar events for later retrieval if needed, could also write to file or database as needed, but for now just store in memory for simplicity.
        return similar[:10] #return first 10 top 10 for now, could adjust as needed.

    def enscribe_callback(self, cmd):
        #for now just print the notes, but could do some processing here to extract any text info from the midi files if available, and associate with the commands in the transcript, to create a more complete picture of what was happening at this time.
#        print(f'{cmd}')
        print(f'> <{cmd["<<"]}>{cmd["&&"]} [{cmd["##"]}]')
#        logger.info(f'> <{cmd['<<']}>{cmd['&&']} [{cmd['##']}]')


    def enscribe(self, notes):
        #for now just print the notes, but could do some processing here to extract any text info from the midi files if available, and associate with the commands in the transcript, to create a more complete picture of what was happening at this time.  could also use this info to help with searching and sorting later, by associating certain key patterns with certain commands or topics in the transcript, to help identify relevant information more quickly.  for now just get the keys and timestamps, but could do more processing here as needed.
        ret = []        
        if self.mykeys is None:
            return
        msgs = self.mykeys.get_msgs(notes)
        wordsb = len(self.mykeys.get_spoken_words())
        for m in msgs:            
#            self.mykeys.key(m.note, m, self.enscribe_callback, doact=False) #dont act on these keys, 
            self.mykeys.key(m.note, m, None, doact=False) #dont act on these keys, dont actually need callback
        wordsa = len(self.mykeys.get_spoken_words())
        #get copy of words..
        if (wordsa > wordsb):
            for i in range(wordsb, wordsa):
                 ret.append(self.mykeys.get_spoken_words().pop()) #get a copy of the new words and remove from mykeys queue, so we can associate with midi data without worrying about duplicates or missing data in the future.  could also do this with a separate function in mykeys to get and clear the queue directly, but for now just pop from the spoken words list as we process them here.
                 #does this actually pop from mykeys.words_
        #clear queue
        ret.reverse() #reverse to get in order of occurrence, since we pop from the end of the list.
        clearqueue = [60,60,60]
        msgs = self.mykeys.get_msgs(clearqueue)
        for m in msgs:            
            self.mykeys.key(m.note, m, None, doact=False) #dont act on these keys, just clear the queue for next time.  could also do this with a separate function in mykeys to clear the queue directly, but for now just use a dummy note that is unlikely to be used in actual music to clear the queue.
        return ret

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
        totmsgs = 0
        totnotes = 0
        date_format = "%Y%m%d%H%M%S"
        for y in range(start_time.year, end_time.year+1):
            folder = self.TRANSCRIPT_FOLDER + str(y) + '/'
            files = []
            for m in range(start_time.month, end_time.month+1):
                sm = str(m).zfill(2)
#                files.extend([f for f in os.listdir(folder) if f.endswith('.mid') and f.startswith(str(y) + sm) and os.path.getmtime(folder + f) >= start_time.timestamp() and os.path.getctime(folder + f) <= end_time.timestamp()])
                files.extend([f for f in os.listdir(folder) if f.endswith('.mid') and f.startswith(str(y) + sm)]) #just use names..

            sorted_files = sorted(files, key=lambda f: f) #sort by modification time, oldest first.  could also sort by creation time if needed.
            numloaded = 0
            print(f'MIDI Read: {folder}')
            print(sorted_files)
            logger.info(f'> MIDI Load {len(files)} files found')
            ret = []
            last_time = start_time.timestamp()
            ctime = None
            for f in sorted_files:
        #      if (f.startswith(yesterday) or f.startswith(today)):
                if (f.endswith('.mid')): #dont open wav files.. maybe rethink sharing directory..
#                    ctime = os.path.getctime(folder + f)
                    ctime = datetime.strptime(f[:14], date_format).timestamp()
                    if (ctime < start_time.timestamp() or ctime > end_time.timestamp()):
                        continue

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
                    totmsgs += len(msgs)
                    totnotes += len(notes)

        logger.info(f'MIDI Loaded {numloaded} files, {totmsgs} messages and {totnotes} notes')
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
    

    #single character for representation of type
    def get_cmd_type(self, cmd):
        if (cmd['_'] == '**'):
            return '*'
        elif (cmd['_'] == '> '):
            return '>'
        elif (cmd['_'] == '$$'):
            return '$'
        elif (cmd['_'] == '#'):
            return '#'
        else:
            #analyze type
            return '_' #default to underscore for unknown types, could also do some analysis here to try to categorize types based on content if needed.
        
    def get_cmd(self, lang, type, command, vars):
        t = self.get_time_var(vars)

        lines = []
        return {'lang': lang, 'type': type, 'cmd': command, 'topic': self.current_topic, 'vars': vars, 'timestamp': t, 'lines': lines, 
                    '<<': lang, '_': type, '&&': command, '**': self.current_topic, '$$': vars, '..': t} #add timestamp for sorting later, and topic for reference, and vars for any variables associated with this command, and lines for any lines associated with this command, which can be used for context when executing the command later.  also add the raw command as '&&' for easy reference later, and topic as '**' for easy reference later.  could also add other metadata here as needed.


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
#                logger.info(f'Adding topic {topc["cmd"]} with vars {topc["vars"]}')
                ret.append(topc)
                currenttopc = topc
                currenttopc['lines'].append(line)
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
                        value = "=".join(parts[1:]).strip()
                        vars[key] = value

                        #prioritize vars here.  
                        #not really notable..  
                        if (currentcmdobj is not None and 'vars' in currentcmdobj):
                            currentcmdobj['vars'][key] = value
                            currentcmdobj['$$'][key] = value
                            if (key == 'TIME'):
                                currentcmdobj['timestamp'] = self.get_time_var(vars)
                                currentcmdobj['..'] = currentcmdobj['timestamp'] #duplicate for easy reference later, could also just use timestamp directly but this is more explicit.  could also add other metadata here as needed.

                        #add to topic as well..                                        
                        elif (currenttopc is not None and 'vars' in currenttopc):
                            currenttopc['vars'][key] = value
                            currenttopc['$$'][key] = value
                            if (key == 'TIME'):
                                currenttopc['timestamp'] = self.get_time_var(vars)
                                currenttopc['..'] = currenttopc['timestamp'] #duplicate for easy reference later, could also just use timestamp directly but this is more explicit.  could also add other metadata here as needed.
                    else:
                        #we have a date here?  special parsing for date/line
                        #references for date/line
                        if (self.is_yyyymmdd(line[2:10].strip())):
                            if (currenttopc is not None and 'vars' in currenttopc):
                                if (len(line) > 10 and line[10] == ':'):
                                    linenum = line[10:].strip()
                                    if (not linenum.isdigit()):
                                        linenum = '0'
                                else:
                                    linenum = '0'
                                if ('..' not in currenttopc['vars']):
                                    currenttopc['$$']['..'] = line[2:10].strip()
                                    currenttopc['$$'][':'] = linenum
                                else:
                                    currenttopc['$$']['..'] += ',' + line[2:10].strip()
                                    currenttopc['$$'][':'] += ',' + linenum
                                    
            if (type[0] == '#'):
                #link here.. list for reading..
                cmd = line[1:].strip()
                obj = self.get_cmd(lang, '#', cmd, {'TIME': now.strftime('%Y%m%d_%H%M%S')})
                ret.append(obj)


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
        try:
            with open(contextmemory, "w+b") as f:
                # memory-map the file, size 0 means whole file
                #append to file.  

                f.write(data.encode('utf-8')) #write data to file, this will also create the file if it doesn't exist

#                mm = mmap.mmap(f.fileno(), 0)
                # read content via standard file methods
#                mdata = data.encode('utf-8')
#                mm[len(mdata):] = mdata #append

#                mm.close()        
        except Exception as e:
            logger.error(f'Error writing to context memory file {contextmemory}: {e}')

    def get_context_memory(self, name, size=1024*1024):
        #handler
        #starts with \
        #starts with .
        #starts with /
        # 1. Attempt to create a new shared memory block
        name = name.replace('\\', '/')
        if (name.startswith('/')):
            name = name[1:] #remove leading slash if present
        #check if exists.  
        if (name.endswith('/')):
            name = name[:-1] #remove trailing slash if present

        name = self.CTXT_FOLDER + name + ".ctx" #add .ctx extension?
        try:
            file_path = pathlib.Path(f'{name}')
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if (not os.path.exists(f'{name}')):
                with open(f'{name}', 'w+b') as f:
                    f.write(b'\n')
        except Exception as e:
            logger.error(f'Error creating context memory file {name}: {e}')

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
            logger.info(f'Opening book {bookname} from {start_time} to {end_time}')
            return self.read(bookname, start_time=start_time, end_time=end_time, myfolder=bookname + "/") #load book into transcripts for reference, this will also update the knowledge graph with any topics/commands found in the book, which can be useful for searching and display later.  could also do some processing here to extract relevant sections or create embeddings for searching later, but for now just load and return the text.

        except Exception as e:
            logger.error(f'!!> Open book [{bookname}]\n !!{e}\n')
        return None
        
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
        
    def get_chromatic(self, array, start_time=None, end_time=None):
        #get chromatic cmds from this struct, which is a nested dict with '&&' for cmds and subfolders for nested books.  this will allow us to get all cmds from a book and its subbooks recursively, with optional time filtering.  could also add topic filtering if needed, but for now just get all cmds.
        ret = []
        if (array is None):
            return ret
        for s in array.values():
            if (s['&&'] is not None and s['('] != s[')']):
                ret.extend(s['&&'][s['(']:s[')']]) #get cmds for this struct, which should already be filtered by time in read_existing, so we can just get the cmds between start_idx and end_idx.  could also add topic filtering here if needed, but for now just get all cmds.

        ret.sort(key=lambda x: x['timestamp']) #sort by timestamp 
        return ret
    
    def get_last_topic_cmd(self, lang, topic, timestamp):
        ret = None
        #keep data in time order..
        if (lang in self.langmap and topic in self.langmap[lang]['topics'] and self.langmap[lang]['topics'][topic]['data'] is not None and len(self.langmap[lang]['topics'][topic]['data']) > 0):
            for cmd in reversed(self.langmap[lang]['topics'][topic]['data']):
                if cmd['type'] == '**':
                    ret = cmd
                    if (cmd['timestamp'] <= timestamp):
                         break
        return ret

    def relevant_topic_array(self, lang='_meta', topicfilter="", timestamp=None):
        if (timestamp is None):
            timestamp = time.time()
        #get just name here..
        ret = []
        #not most efficient.. but should be filtered list..
        for (k,v) in self.langmap[lang]['topics'].items():
            if topicfilter == "":
                #get latest..
                latest = self.get_last_topic_cmd(lang, k, timestamp=timestamp)
                if (latest is not None):
                    ret.append(latest)
            else:
                #not efficient, but want fuzzy search result..
                ff = fuzz.partial_ratio_alignment(topicfilter, k)
                if (ff.score > 80): #threshold for relevance, could adjust as needed.
                    latest = self.get_last_topic_cmd(lang, k, timestamp=timestamp)
                    if (latest is not None):
                        ret.append(latest)

        return ret
    
    #recursive search, could be painful..#save us some time for now just 3 depth
    def relevant_book_array(self, searchbooks=None, namefilter="", maxdepth=3, currentdepth=0): 
        #get just name here..
        ret = []
        for k,v in searchbooks.items():
            if (k == '&&' or k == '**' or k == '(' or k == ')' or k=='..'):
                continue
            if (currentdepth < maxdepth):
                ret.extend(self.relevant_book_array(searchbooks=v, namefilter=namefilter, maxdepth=maxdepth, currentdepth=currentdepth+1))
        if (searchbooks['&&'] is not None):         
            #if we have commands, include this book..

            if namefilter == "":            
                ret.append(searchbooks)
            else:
                #not efficient, but want fuzzy search result..
                ff = fuzz.partial_ratio_alignment(namefilter, searchbooks['**'])
                if (ff.score > 80): #threshold for relevance, could adjust as needed.
                    ret.append(searchbooks)
                #search within the books as well?  
                for cmd in searchbooks['&&']:
                    if '**' in cmd and cmd['**'] is not None:
                        book = self.get_from_nested(self.allbooks, cmd['**'].split('/'))
                        ret.extend(self.relevant_book_array(searchbooks=book, namefilter=namefilter, maxdepth=maxdepth, currentdepth=currentdepth+1))                        


        return ret


    def filter_books_recursive(self, folder="books", searchbooks=None, start_time=None, end_time=None):
        #get just name here..
        if (searchbooks is None):
            tree = folder.split('/')
            if (len(tree) == 1 and tree[0] == "books"):
                tree = tree[1:] #tree search if not default value.  
            logger.info(f'Filtering book {folder} with tree {tree}')
            searchbooks = self.get_from_nested(self.allbooks, tree) #tree = [], searchbooks = self.allbooks
        if (searchbooks is None):
            return {'**': folder, '&&': None, '(': 0, ')': 0} #if we dont have this book, return empty struct with just the folder name for reference, this will allow us to build the struct as we search and find books, and also handle cases where we have a book in the file system but not in our allbooks struct for some reason, this way we can still get the cmds for that book if it exists, and if not we just return an empty struct for it.
        retstruct = {'**': folder, '&&': None, '(': 0, ')': 0} #store cmds for this book here, and also store start and end idx for filtering by time later.  could also store topic info here if needed, but for now just store cmds and time info.

        logger.info(f'{folder} searchbooks: {searchbooks}')
        for k,v in searchbooks.items():
            if (k == '&&' or k == '**' or k == '(' or k == ')' or k=='..'):
                continue
            retstruct[k] = self.filter_books_recursive(folder+"/"+k, searchbooks=v, start_time=start_time, end_time=end_time)
        if (searchbooks['&&'] is not None):            
#            searchbooks['&&'] = self.read_existing(searchbooks['**'], start_time=start_time, end_time=end_time) #get existing cmds filter time..
#            searchbooks['start_idx'] = self.allcmds[searchbooks['**']]['start_idx']
#            searchbooks['end_idx'] = self.allcmds[searchbooks['**']]['end_idx']
#            logger.info(f'Filtering {folder} cmds from {searchbooks["**"]} {start_time} to {end_time}')
#            logger.info(f'{self.allcmds[searchbooks["**"]]["&&"]}')
            a = self.read_existing(searchbooks['**'], start_time=start_time, end_time=end_time) #get existing cmds filter time..
            
            logger.info(f'After filtering {folder} cmds from {searchbooks["**"]} got {len(a)} cmds {self.allcmds[searchbooks["**"]]["start_idx"]} to {self.allcmds[searchbooks["**"]]["end_idx"]}')
#            logger.info(f'After filtering {folder} cmds from {searchbooks["**"]} start_idx {self.allcmds[searchbooks["**"]]["start_idx"]} end_idx {self.allcmds[searchbooks["**"]]["end_idx"]}')
            if (searchbooks['&&'] is not None and len(a) > 0):
                retstruct['&&'] = searchbooks['&&'] #get cmds for this struct
                #dont update searchbooks['&&'], just set the start_idx and end_idx for filtering, this way we can keep the original cmds in searchbooks for reference and just use the start_idx and end_idx to filter by time when we get the chromatic cmds later.  this will also allow us to handle cases where we have a book in the file system but not in our allbooks struct for some reason, this way we can still get the cmds for that book if it exists, and if not we just return an empty struct for it.
                retstruct['('] = self.allcmds[searchbooks['**']]['start_idx']
                retstruct[')'] = self.allcmds[searchbooks['**']]['end_idx']+1
                retstruct['..'] = self.allcmds[searchbooks['**']]['last_mtime'] #last modified..

            
        return retstruct
    
    def open_books(self, folder="books", days=365):
        #check recursively and if there are any files in the folder, open them as books.  
        #only include the immediate files in the book.  
        #closing book will close all subbooks as well for now..

        retstruct = {'**': folder, '&&': None, '(': 0, ')': 0} #store cmds for this book here, and also store start and end idx for filtering by time later.  could also store topic info here if needed, but for now just store cmds and time info.
        #get just name here..
        subfolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]
        for subfolder in subfolders:
            logger.info(f'Opening book {subfolder} from folder {folder}')
            print(f'Opening book {subfolder} from folder {folder}')
            bookname = subfolder #books/worldhistory/worldwar2/YYYYmmdd.txt
            #retstruct = books['worldhistory']['worldwar2']['&&'] #get cmd struct for this subbook..
            #if we have other subfolders, load them..
            tempfolder = folder + "/" + subfolder
            retstruct[subfolder] = self.open_books(tempfolder, days=days) #recursively open subbooks as well, this will allow for nested book structures
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

#        self.allcmds[lang] = {'**': lang, '&&': ret, 'cmds': ret, '..': last_mtime, 'last_mtime': last_mtime, 'start_time': start_time, 'end_time': end_time, 'start_idx': 0, 'end_idx': len(ret)-1, 'open': True}
#        self.update_kg(lang, ret)
        self.merge_cmds(lang, ret, start_time, end_time, last_mtime)
        logger.info(f'Loaded {numloaded} files for {lang} with {len(ret)} commands')
        return ret

    def merge_cmds(self, lang, ret, start_time, end_time, last_mtime):

        if (lang in self.allcmds and self.allcmds[lang]['&&'] is not None):
            #merge with existing cmds, keeping only unique cmds and sorting by timestamp.  this will allow us to keep the existing cmds in memory and just add any new cmds from the new files, which should be more efficient than reloading all cmds every time we open a book, especially if we have a lot of data.  could also implement a more sophisticated merging strategy if needed, but for now just merge and sort.
            existing_cmds = self.allcmds[lang]['&&']
            existing_start_time = self.allcmds[lang]['start_time']
            existing_end_time = self.allcmds[lang]['end_time']
            existing_cmds_dict = {cmd['timestamp']: cmd for cmd in existing_cmds} #use timestamp as key for uniqueness, this assumes we dont have duplicate timestamps which should be rare but could happen, if we do have duplicates we will just keep the last one we see which should be fine for now.
            for cmd in ret:
                existing_cmds_dict[cmd['timestamp']] = cmd #this will overwrite any existing cmd with the same timestamp, which should be fine for now.

            merged_cmds = list(existing_cmds_dict.values())
            merged_cmds.sort(key=lambda x: x['timestamp']) #sort by timestamp just in case.
            
            if (existing_start_time < start_time):
                start_time = existing_start_time
            if (existing_end_time > end_time):
                end_time = existing_end_time

            start_idx = 0
            end_idx = len(merged_cmds)-1
            self.allcmds[lang] = {'**': lang, '&&': merged_cmds, 'cmds': merged_cmds, '..': last_mtime, 'last_mtime': last_mtime, 'start_time': start_time, 'end_time': end_time, 'start_idx': start_idx, 'end_idx': end_idx, 'open': True}            
            self.update_kg(lang, merged_cmds)
        else:
            self.allcmds[lang] = {'**': lang, '&&': ret, 'cmds': ret, '..': last_mtime, 'last_mtime': last_mtime, 'start_time': start_time, 'end_time': end_time, 'start_idx': 0, 'end_idx': len(ret)-1, 'open': True}
            self.update_kg(lang, ret)

    def set_current_topic(self):
        lastlang = None
        lastmtime = 0
        for (k, v) in self.allcmds.items():
            if (v['..'] is not None and v['..'] > lastmtime):
                lastmtime = v['..']
                lastlang = k
            else:
                #if we dont have a lastmtime, just get the most recent topic from this lang if it has cmds, this will allow us to set a current topic even if we dont have mtime data for some reason, which should be rare but could happen.
                #what is this data?  
                logger.info(f'No mtime for {k}, checking for most recent topic from cmds')                
        if (lastlang is not None and len(self.allcmds[lastlang]['&&']) > 0):
            self.current_topic = self.allcmds[lastlang]['&&'][-1]['**']
        else:
            self.current_topic = None
