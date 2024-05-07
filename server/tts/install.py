git clone https://github.com/coqui-ai/TTS

cd TTS
python3 ./setup.py install

cd ./TTS/recipes/ljspeech
vi ./download_ljspeech.sh
remove --mv LJSpeech-1.1 $RUN_DIR/
sudo bash ./download_ljspeech.sh (not sure why launch directory is important to this script, ideally that would be egal.  )

python3 ./TTS/recipes/ljspeech/tacotron2-DCA/train_tacotron_dca.py


vi ./TTS/recipes/ljspeech/tacotron2-DCA/train_tacotron_dca.py
batch_size=16


If training stops:
go to latest train directory
delete test_sentences

vi "./TTS/recipes/ljspeech/tacotron2-DDC//run-April-15-2024_09+59PM-0000000/config.json"
Dont delete the variable, just make it an empty array.  
--test_sentences[]

python3 ../../../../TTS/bin/train_tts.py --continue_path .

