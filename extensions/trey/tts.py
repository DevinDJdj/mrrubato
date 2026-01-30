import pyttsx3

global all_voices
all_voices = []

def initVoices():
    global all_voices
    if (len(all_voices) > 0):
        return all_voices
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(f"Voice: {voice.name}, ID: {voice.id}, Lang: {voice.languages}")
    all_voices = voices
    return all_voices

def speak(text, voice_id=None, fname=None, volume=0.7, rate=150):
    engine = pyttsx3.init()
    if voice_id is not None:
        #get lang.  
        lang = voice_id.split('-')[0]
        initVoices()
        for v in all_voices:
            if (v.languages is not None and lang in v.languages):
                voice_id = v.id
                break
        engine.setProperty('voice', voice_id)        
#    engine.say(text)
    engine.setProperty('volume', volume)  # Volume: 0.0 to 1.0
    engine.setProperty('rate', rate)      # Speed percent (can go over 100
    if fname is not None:
        engine.save_to_file(text, fname)
    else:
        engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(f"Voice: {voice.name}, ID: {voice.id}, Lang: {voice.languages}")
