#client side install scripts.  
#create certs
#openssl req -new -newkey rsa:2048 -nodes -keyout chat.misterrubato.com.key -out chat.misterrubato.com.csr
#openssl pkcs7 -print_certs -in C:\devinpiano\private\chat_misterrubato_com\chat_misterrubato_com.p7b -out C:\devinpiano\private\chat_misterrubato_com\chat_misterrubato_com.pem

#pip install flask
#pip install python-dotenv
#python ./server/transcription/server.py
#pip install moviepy
#pip install fastembed

#pip install flask.ext

#pip install chromadb
#pip install langchain
#pip install BeautifulSoup4
#pip install gpt4all
#pip install langchainhub
#pip install pypdf
#pip install chainlit
#pip install fastembed


#get existing transcripts if needed
gcloud compute scp --project misterrubato-test --zone us-west1-b --recurse deeplearning-1-vm:/home/devin/server/transcription/output c:/devinpiano/music/server/transcription/output


#copy certs if set up

gcloud compute scp --project misterrubato-test --zone europe-west4-b --recurse c:/devinpiano/private/* deeplearning-20240412:/home/devin/private


#copy model if needed.  
gcloud compute scp --project misterrubato-test --zone europe-west4-b --recurse deeplearning-20240412:/home/devin/TTS/recipes/ljspeech/tacotron2-DCA/run-April-19-2024_02+00AM-0000000 c:/devinpiano



#load transcript data, this doesnt load TTS data.  
python ./ollama/load.py

.....failing with many data files.  
cant be bothered to find this failure.  split into 
python ./load.py --video a*
python ./load.py --video b*
...


#setup firewall rules

gcloud compute firewall-rules create rule-allow-tcp-8000 --source-ranges 0.0.0.0/0 --target-tags allow-tcp-8000 --allow tcp:8000
gcloud compute firewall-rules create rule-allow-tcp-8001 --source-ranges 0.0.0.0/0 --target-tags allow-tcp-8001 --allow tcp:8001
gcloud compute firewall-rules create rule-allow-tcp-8001 --source-ranges 0.0.0.0/0 --target-tags allow-tcp-8002 --allow tcp:8002

gcloud compute instances add-tags deeplearning-1-vm --tags allow-tcp-8000
gcloud compute instances add-tags deeplearning-1-vm --tags allow-tcp-8001
gcloud compute instances add-tags deeplearning-1-vm --tags allow-tcp-8002

#set up TTS
vi ./TTS/recipes/ljspeech/tacotron2-DCA/train_tacotron_dca.py

python3 ./TTS/recipes/ljspeech/tacotron2-DCA/train_tacotron_dca.py

batch_size=16
If training stops:
go to latest train directory
delete test_sentences
Dont delete the variable, just make it an empty array.  
python3 ../../../../TTS/bin/train_tts.py --continue_path .

#need about 300000 steps to get a decent result.  
#test synthesis
python3 ./TTS/TTS/bin/synthesize.py --text "I am determined to acquire language." --model_path "./TTS/recipes/ljspeech/tacotron2-DCA/run-April-19-2024_02+00AM-0000000/best_model.pth" --config_path "./TTS/recipes/ljspeech/tacotron2-DCA/run-April-19-2024_02+00AM-0000000/config.json"

