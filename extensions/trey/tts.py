import os
    

import pyttsx3

global all_voices
global all_langs
all_voices = []
all_langs = []

import logging
logger = logging.getLogger(__name__)

def initVoices():
    global all_voices, all_langs

    if (len(all_voices) > 0):
        return all_voices
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(f"Voice: {voice.name}, ID: {voice.id}, Lang: {voice.languages}")
        for l in voice.languages:
            if l[:2] not in all_langs:
                all_langs.append(l[:2])
    all_voices = voices
    return all_voices

langmap = {'jf': 'ja', 'af': 'en', 'ef': 'es', 'em': 'es'}
def speak(text, voice_id=None, fname=None, volume=0.7, rate=150):
    global all_voices, all_langs
    engine = pyttsx3.init()
    if voice_id is not None:
        initVoices()
        #get lang.  
        lang = voice_id.split('_')[0]
        if lang in langmap:
            lang = langmap[lang]
        if (lang not in all_langs):
            print(f"Warning: Detected language {lang} is not in available languages: {all_langs}")
#            logger.warning(f"!!{lang} not in available languages: {all_langs}")
        else:
            print(f"Detected language: {lang} in {all_langs}")
            #insert at top of all_langs as last used..
            #replace entry
            all_langs.remove(lang)
            all_langs.insert(0, lang)
        #maybe pass exact ID in future?  
#        if (voice_id in [v.name for v in all_voices]):
#            voice_id = [v.id for v in all_voices if v.name == voice_id][0]
        #for now just get language right..
        for v in all_voices:
            langcodes = [l[:2] for l in v.languages]
            if (v.languages is not None and lang in langcodes):
                #use last one.. perhaps best?  
                voice_id = v.id #for now just pick first one that supports lang..
#                break
        engine.setProperty('voice', voice_id)        
        print(f"Using voice ID: {voice_id}")
#    engine.say(text)
    engine.setProperty('volume', volume)  # Volume: 0.0 to 1.0
    engine.setProperty('rate', rate)      # Speed percent (can go over 100
    if fname is not None:
        os.makedirs(os.path.dirname(fname), exist_ok=True)
        engine.save_to_file(text, fname)
    else:
        engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(f"Voice: {voice.name}, ID: {voice.id}, Lang: {voice.languages}")
