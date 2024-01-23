openssl req -new -newkey rsa:2048 -nodes -keyout chat.misterrubato.com.key -out chat.misterrubato.com.csr
openssl pkcs7 -print_certs -in C:\devinpiano\private\chat_misterrubato_com\chat_misterrubato_com.p7b -out C:\devinpiano\private\chat_misterrubato_com\chat_misterrubato_com.pem

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


#get existing transcripts
gcloud compute scp --project misterrubato-test --zone us-west1-b --recurse deeplearning-1-vm:/home/devin/server/transcription/output c:/devinpiano/music/server/transcription/output

#load data
python ./ollama/load.py


#setup firewall rules
gcloud compute firewall-rules create rule-allow-tcp-8181 --source-ranges 0.0.0.0/0 --target-tags allow-tcp-8181 --allow tcp:8181

gcloud compute firewall-rules create rule-allow-tcp-8000 --source-ranges 0.0.0.0/0 --target-tags allow-tcp-8000 --allow tcp:8000
gcloud compute firewall-rules create rule-allow-tcp-8001 --source-ranges 0.0.0.0/0 --target-tags allow-tcp-8001 --allow tcp:8001

gcloud compute instances add-tags deeplearning-1-vm --tags allow-tcp-8000
gcloud compute instances add-tags deeplearning-1-vm --tags allow-tcp-8001
gcloud compute instances add-tags deeplearning-1-vm --tags allow-tcp-8181

