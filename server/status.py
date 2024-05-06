#check here each 5 mins from crontab and restart the services if they are not responding.  
#cant be bothered with containers right now.
#sudo apt-get install -y systemd
#sudo systemctl daemon-reload
#/etc/systemd/system/tts.service
#[Unit]
#Description=My TTS Service
#After=multi-user.target
#[Service]
#Type=simple
#Restart=always
#ExecStart=/usr/bin/python3 /home/me/mrrubato/server/tts/server.py
#[Install]
#WantedBy=multi-user.target

#/etc/sudoers.d/me
#%me ALL=NOPASSWD: /bin/systemctl restart tts.service

#/etc/crontab
#5 5 * * * me /home/me/mrrubato/server/status.py

#ping
#systemctl restart tts.service
#systemctl restart ollama.service
#systemctl restart transcription.service


