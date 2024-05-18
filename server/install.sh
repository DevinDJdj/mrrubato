#run this to set up basic RAG and transcription.  
#install.sh

#pass owner/user which will run the server
myowner=$1
#myhome should be data containing mrrubato and TTS and any other packages.  
myhome=$2

#myhome=env | grep HOME | cut -d'=' -f2
echo $myhome

#set up all data directories
mkdir -p $myhome/data/transcription/output
mkdir -p $myhome/private
mkdir -p $myhome/data/vectorstores/db

#install requirements
echo "installing requirements"
pip install -r $myhome/mrrubato/server/requirements.txt

sudo apt update
sudo apt install ffmpeg

#create services shell script.  
echo "Creating transcription service"
sudo cat > /etc/systemd/system/transcription.service << EOF
[Unit]
Description=Transcription service
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $myhome/mrrubato/server/transcription/server.py

[Install]
WantedBy=multi-user.target
EOF

#create services shell script.  
echo "Creating chat service"
sudo cat > /etc/systemd/system/chat.service << EOF
[Unit]
Description=Ollama Chat service
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $myhome/mrrubato/server/ollama/server.py

[Install]
WantedBy=multi-user.target
EOF



echo "Reloading systemctl daemon"
sudo systemctl daemon-reload
sudo systemctl enable transcription.service
sudo systemctl enable chat.service
#sudo systemctl start transcription.service
#sudo systemctl start chat.service

