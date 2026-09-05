from kokoro import KPipeline
import soundfile as sf
import sys

sys.path.insert(0, 'c:/devinpiano/') #config.json path
sys.path.insert(1, 'c:/devinpiano/music/') #config.py path Base project path
sys.path.insert(2, 'c:/devinpiano/music/mrrubato') #config.py path Base project path
import extensions.trey.tts as tts

import MeCab
tagger = MeCab.Tagger()
print(tagger.parse("test"))

#from fugashi import GenericTagger
#tagger = GenericTagger()



# Initialize pipeline for Japanese ('j')
pipeline = KPipeline(lang_code='j')

# Japanese text to synthesize
text = 'こんにちは、ココロです。'


from fast_langdetect import LangDetector, LangDetectConfig

# Create a configuration with your custom model path
config = LangDetectConfig(
    custom_model_path="./models/fast-langdetect/lid.176.bin",  # Path to local model file
#    disable_verify=True                         # Skip MD5 verification if needed
)

# Initialize the detector with the manual configuration
detector = LangDetector(config)

# Detect language
result = detector.detect("Hello world")
print("Hello World:", result)

from fast_langdetect  import detect

result = detector.detect(text, model="auto", k=3)
print(f"{text} {result}")

# Choose a Japanese voice (e.g., jf_alpha or jf_tebukuro)
voice = 'jf_alpha' 

# Generate audio generator
generator = pipeline(text, voice=voice, speed=1.0)

# Process and save the output audio
for i, (gs, ps, audio) in enumerate(generator):
    sf.write(f'output_{i}.wav', audio, 24000)
    print(f'Saved output_{i}.wav')


tts.speak(text, voice_id=voice, fname=f'./output/output_ttstest.wav')
