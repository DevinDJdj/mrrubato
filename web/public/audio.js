//audio control functions for saving audio feedback.  


var myaslang = "base"; //default language for audio snapper.


function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
  
      reader.onloadend = () => {
        // The result attribute contains the data as a data: URL,
        // which includes the Base64-encoded string.
        // We need to remove the "data:*/*;base64," prefix.
        const base64String = reader.result;
        if (base64String) {
          const base64Data = base64String.split(',')[1];
          resolve(base64Data);
        } else {
          reject(new Error("Failed to read Blob as Base64."));
        }
      };
  
      reader.onerror = (error) => {
        reject(error);
      };
  
      // Reads the contents of the specified Blob or File.
      // When the read operation is finished, the readyState becomes DONE,
      // and the loadend event is triggered.
      // At that time, the result attribute contains the data as a data: URL
      // representing the file's data as a base64 encoded string.
      reader.readAsDataURL(blob);
    });
  }


class AudioSnapper { //use to just read as well.  
    
    /**
     * Capture audio feedback from the user.
     * @param {HTMLElement} video element 
     * @param {Object} options = width of screen, height of screen, time to seek
     * @param {Function} handle function with canvas element in param
     */
    constructor(lang="base", concurrency=2) {
      // Initiate variables
      this.audioarray = [[], []]; //audioarray[user][entrynum] = {"audio": audio, "time": time, "lang": lang}

      this.volumearray = []; //just time and volume level, or just take the past X entities.  
      this.volumeSampleTime = 0;
      this.audioRecording = false;
      this.audioLastPlayed = 0;
      this.audioNextPlay = 0; //reset to 0 if we stop all audio etc.  
  
      this.concurrency = concurrency;


      this.record = document.querySelector('.audio-record');
      this.stop = document.querySelector('.audio-stop');
      this.canvas = document.querySelector('.audio-visualizer');
      this.audioCtx = null;
      //probably need multiple players for simultaneous audio.  
      //not sure if mixing all together or not.  

      //create concurrency # players.  0 = self, 1 = user 1, etc.  
      //then have dynamic user selection.  


      this.openplayer = 0;
      this.players = [];
      this.playeraudio = [];
      for (let i = 0; i < concurrency; i++){
        this.playeraudio.push(null);
        this.players[i] = document.createElement('audio');
        this.players[i].controls = true; //add controls to the audio player
        this.players[i].id = 'my-audio-' + i; //give it an id
        this.players[i].classList.add('my-audio');
        let div = document.getElementById('audio-div-table');
        if (div != null){
          var row = document.createElement("tr");
          var cell1 = document.createElement("td");
          var cell2 = document.createElement("td");
          cell1.appendChild(this.players[i]); //append to the audio-div
          let mylabel = div.appendChild(document.createElement('label'));
          mylabel.id = 'my-audio-label-' + i; //give it an id
          mylabel.textContent = "User " + i; //add label
          mylabel.htmlFor = 'my-audio-' + i; //link label to audio player
          cell2.appendChild(mylabel); //add label
          row.appendChild(cell1);
          row.appendChild(cell2);
          div.appendChild(row); //append to the audio-div
//          div.appendChild(this.players[i]); //append to the audio-div
        }
      }
      this.player = document.getElementById('my-audio');
      this.player.volume = 0.5; //default volume
      this.chunks = [];
      this.lang = lang;

      const constraints = { audio: true };
      navigator.mediaDevices.getUserMedia(constraints).then(this.onSuccess, this.onError);

    }


    //0kvXEzw3GSI

    loadAudioFeedback(value, useridx){
      let tempidx = this.audioarray.length;
      //init audioarray for user.  
      while (tempidx <= useridx){
        this.audioarray.push([]); //add empty array for this user
        tempidx++;
      }

      //temparray = [];
      //not sure if this comes in order or not.  
      for (const [aidx, avalue] of Object.entries(value)){
        //add audio to the array
        this.audioarray[useridx].push(avalue);
      }
      //sort by time.  
      this.audioarray[useridx].sort((a, b) => a.time - b.time); //sort by time
      for (let i = 0; i < this.audioarray[useridx].length; i++){
        this.audioarray[useridx][i].lastplayed = 0; //reset last played time
      }

    }

    onSuccess = function(stream) {
        const mediaRecorder = new MediaRecorder(stream);

        
        as[myaslang].visualize(stream);
    
        as[myaslang].record.onclick = function() {
          mediaRecorder.start();
          console.log(mediaRecorder.state);
          console.log("recorder started");
          as[myaslang].record.style.background = "red";
    
          as[myaslang].audioRecording = true;
          as[myaslang].stop.disabled = false;
          as[myaslang].record.disabled = true;
          //get video time when recording starts.  update this with the blob and time when recording stops.
          let mytime = vgetReferenceTime(); //video.js milliseconds?

          //push to self audioarray.  time here is relative video time.  
          //find insert location for this time.  
          let aa = as[myaslang].audioarray[0];
          //find the right place to insert this audio
          let i = aa.length - 1; //start from the end
          while (i > -1 && aa[i].time > mytime){
            i--; //find the closest audio before this time.  
          }
          aa.splice(i+1, 0, {"audio": null, "time": mytime, "started": Date.now(), "lang": myaslang, "audiolength": 0, "lastplayed": 0}); //insert at the right place

        }
    
        as[myaslang].stop.onclick = function() {
          mediaRecorder.stop();
          console.log(mediaRecorder.state);
          console.log("recorder stopped");
          as[myaslang].record.style.background = "";
          as[myaslang].record.style.color = "";
          // mediaRecorder.requestData();
    
          as[myaslang].audioRecording = false;
          as[myaslang].volumearray = []; //reset volume array
          as[myaslang].stop.disabled = true;
          as[myaslang].record.disabled = false;
        }
    
        mediaRecorder.onstop = function(e) {
          console.log("data available after MediaRecorder.stop() called.");
    
//          const clipName = prompt('Enter a name for your sound clip?','My unnamed clip');
    
        
          //this.player.controls = true;
          const blob = new Blob(as[myaslang].chunks, { 'type' : 'audio/ogg; codecs=opus' });
          as[myaslang].chunks = [];
          const audioURL = window.URL.createObjectURL(blob);
          as[myaslang].player.src = audioURL;
          console.log("recorder stopped");
          blobToBase64(blob)
          .then(base64Data => {
            console.log("Base64 data:", base64Data);
            //save this to the audioarray
            //eventually this will be passed through feedback and replayed. 
            let aa = as[myaslang].audioarray[0];
            let i = aa.length - 1; //start from the end
            while (i > -1){
              if (aa[i].audio == null){
                aa[i].audio = base64Data; //set the audio for the last entry
                aa[i].audiolength = Date.now() - aa[i].started; //set the length of the audio in milliseconds
                break; //found
              }
              i--; //find the closest audio before this time.  
            }

            //get video time when recording starts.  update this with the blob and time when recording stops.
            //need blob header probably so we can load into audiocontext.  
//            as[myaslang].audioarray[0][myaslang].push({"audio": base64Data, "time": Date.now(), "lang": myaslang});
          })
          .catch(error => {
            console.error("Error converting Blob to Base64:", error);
          });          
        
        }
    
        mediaRecorder.ondataavailable = function(e) {
          as[myaslang].chunks.push(e.data);
        }
      }
    
      onError = function(err) {
        console.log('The following error occured: ' + err);
      }
      
  
      detectedVolume(level){
        //try to detect silence.  
        //this will depend on environment.  
        if (level < 9) { //not sure what is the appropriate level.  
            //considered silent
            return true;
        }
        else{
            //not silent
            return false;
        }
      }

      getLeastRemainingAudioPlayer(){
        let now = Date.now();
        let leastTime = now + 500000; //set to a long time in the future
        let leastIndex = 0;
        for (let i = 0; i < this.concurrency; i++){
            if (this.playeraudio[i] == null){
                //this player is open
                return [i, 0]; //return this index and 0 remaining time
            }
            else if (this.playeraudio[i].lastplayed < leastTime){
                //not playing anything, return this index
                leastTime = this.playeraudio[i].lastplayed;
                leastIndex = i;
            }
        }

        return [leastIndex, leastTime]; //return index and remaining time in milliseconds
      }

      runAudio(t=-1){
        let mintime = 1000000000;
        let now = Date.now();
        if (t < 0){
            t = vgetReferenceTime(); //video.js milliseconds?
        }
//        let myvtime = 
        //this can keep track of simultaneous audio playing as well.  
        //just reset this when the next of concurrent audio will end.  

        //different pause needed, allow audio to run while video is paused.  
        //ispaused from midi.js
        if (now < as[myaslang].audioNextPlay || ispaused){
            return;
        }
        //eventually iterate over all users.  
        //check for higher rank users.  
        //self comments will always be first.  
        //not sure if this is the right way to do it, but for now this is ok.
        //can probably improve this search algorithm later.  
        for (j=0; j< as[myaslang].audioarray.length; j++){
            if (as[myaslang].audioarray[j] == null || as[myaslang].audioarray[j].length == 0){
                continue; //no audio for this user
            }
            //iterate over all audios for this user.
            let i = 0;
            let d = vgetDuration(); //video.js duration
            let aa = as[myaslang].audioarray[j]; //this is the user 0 = self.
            i = Math.floor((t/d) * aa.length); //find the index of the audio for this time
            while (i < aa.length && i > -1){
                if (aa[i].time < t-5000){
                    //this is a past audio, skip it.
                    //get to t-5000
                    i++;
                }
                else {
                    //this is a future audio, stop searching
                    while (i > 0 && aa[i-1].time > t - 5000){
                      i--; //find the closest audio before this time.  
                    }
                    break;
                }
            }
            if (i < 0 || i >= aa.length){
                //no audio found for this user at this time, continue to next user
            }
            else{

              for (i; i< aa.length && Math.abs(aa[i].time - t) < 5000; i++){

                  //find closest past the time.  
                  //checking every few seconds.  
                  //hopefully random enough to not play the same audio if there are overlapping audios at certain time.  
                  //otherwise have to adjust the algorithm a bit.  
                  //and dont play the same stuff over and over.  

                  
                  //give 10 second window to trigger audio if we have something available.  
                  if (aa[i].lastplayed - now < 0){ //dont play again for 5 seconds at least.  
                      mintime = Math.abs(aa[i].time - t);
                      //set last played time to now + length of audio so we dont replay it immediately.
                      aa[i].lastplayed = Date.now() + 10000+aa[i].audiolength; //add 10 seconds.  add speed calculation later. 
                      //eventually see if we have several other audios playing.  
                      //for now one at a time I guess.  
                      if (aa[i].audio != null){
                          //play this audio
                          as[myaslang].playeraudio[as[myaslang].openplayer] = aa[i];
                          as[myaslang].players[ as[myaslang].openplayer].src = "data:audio/ogg;base64," + aa[i].audio;
                          as[myaslang].players[ as[myaslang].openplayer].play();

                          if (as[myaslang].concurrency >= 1){
                              //this should always be open.  
                            //find an open player.
                          
                            
                            let [idx, rem] = as[myaslang].getLeastRemainingAudioPlayer();
                            as[myaslang].openplayer = idx; //set the open player to this index
                            as[myaslang].audioNextPlay = rem; //set next play time
                            //user is j.  

                            console.log("Playing audio from user " + j + " on player " + idx + " with remaining time " + rem);
                            let label = document.getElementById('my-audio-label-' + idx);
                            if (label != null){
                              label.textContent = "User " + j + " Audio " + i; //update label
                            }

                    
                         }
                         else{
                           as[myaslang].audioNextPlay = Date.now() + aa[i].audiolength; //set next play time
                         }
                          as[myaslang].audioLastPlayed = Date.now();



                          //as[myaslang].player.src = "data:audio/ogg;base64," + aa[i].audio;
                          //as[myaslang].player.play();

                          //set to null so we dont play it again.  
      //                    as[myaslang].audioarray[0][myaslang][i].audio = null;
                          break; //only play one at a time.  
                      }
                  }
              }
            }
          }
      }
      checkVolume(analyser, dataArray){

        let sum = 0;
        analyser.getByteFrequencyData(dataArray); // Get the frequency data
        let startFrequency = 80; //80Hz detecting human voice vs silence
        let endFrequency = 300;
        let frequencyPerBin = as[myaslang].audioCtx.sampleRate / analyser.fftSize; //frequency per bin
        let startBin = Math.round(startFrequency /frequencyPerBin);
        let endBin = Math.round(endFrequency / frequencyPerBin); //end frequency for human voice
        for (let i = startBin; i < dataArray.length && i<endBin; i++) {
            const value = dataArray[i]; // Center the values around zero
            sum += value;
        }
        const rms = Math.sqrt(sum / (endBin - startBin)); // Calculate the RMS value
        // rms will be a value representing the average amplitude
        let silent = as[myaslang].detectedVolume(rms);
        as[myaslang].volumearray.push({"time": now, "level": rms, "silent": silent}); //add a new sample

        if (as[myaslang].volumearray.length > 10){
            as[myaslang].volumearray.shift(); //remove oldest sample
        }
        //see what is the silent level in the past few.  Seems to work ok.  
        //not perfect, but good enough for now.
        let silentcount = 0;
        for (let i = as[myaslang].volumearray.length-1; i > 0 ; i--){

            if (as[myaslang].volumearray[i].silent){
                //we have a silent sample.  
                silentcount+=2;
            }
            if (as[myaslang].volumearray[i].level > as[myaslang].volumearray[i-1].level){
                silentcount-=2; //not silent, getting louder.  
            }
            else if (as[myaslang].volumearray[i].level < as[myaslang].volumearray[i-1].level){
                silentcount++; //not silent, but getting quieter.
                //this works because of the way the samples work.  
            }
             if (silentcount > 6){
                //3, or 3/4 or 4/6  etc seconds of silence out of the last 10.  
                //basically above 1/2 silence.  
                //just stop the recording.
                console.log("stopping audio recording due to prolonged silence");
                as[myaslang].stop.click();
                break;
            }
        }
      }

      visualize(stream) {
        if(!as[myaslang].audioCtx) {
            as[myaslang].audioCtx = new AudioContext();
        }
      
        const source = as[myaslang].audioCtx.createMediaStreamSource(stream);
      
        const analyser = as[myaslang].audioCtx.createAnalyser();
        analyser.fftSize = 2048;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
      
        source.connect(analyser);
        //analyser.connect(audioCtx.destination);
        ASdraw();
      
        function ASdraw() {
            const canvasCtx = as[myaslang].canvas.getContext("2d");
            const WIDTH = as[myaslang].canvas.width
            const HEIGHT = as[myaslang].canvas.height;

            //timer in draw function, probably bad practice, but time..
            let now = Date.now();
            if (as[myaslang].audioRecording && (now - as[myaslang].volumeSampleTime > 1000)){
                as[myaslang].volumeSampleTime = now;
                as[myaslang].checkVolume(analyser, dataArray);
            }
    
            requestAnimationFrame(ASdraw);
        
            analyser.getByteTimeDomainData(dataArray);
        
            canvasCtx.fillStyle = 'rgb(200, 200, 200)';
            canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
        
            canvasCtx.lineWidth = 2;
            canvasCtx.strokeStyle = 'rgb(0, 0, 0)';
        
            canvasCtx.beginPath();
        
            let sliceWidth = WIDTH * 1.0 / bufferLength;
            let x = 0;
        
        
            for(let i = 0; i < bufferLength; i++) {
        
              let v = dataArray[i] / 128.0;
              let y = v * HEIGHT/2;
        
              if(i === 0) {
                canvasCtx.moveTo(x, y);
              } else {
                canvasCtx.lineTo(x, y);
              }
        
              x += sliceWidth;
            }
        
            canvasCtx.lineTo(as[myaslang].canvas.width, as[myaslang].canvas.height/2);
            canvasCtx.stroke();
        
          }
    
      }

    
      
  }
  
  