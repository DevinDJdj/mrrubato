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


class AudioSnapper {
    
    /**
     * Capture audio feedback from the user.
     * @param {HTMLElement} video element 
     * @param {Object} options = width of screen, height of screen, time to seek
     * @param {Function} handle function with canvas element in param
     */
    constructor(lang="base") {
      // Initiate variables
      this.audioarray = [{lang: []}]; //audioarray[user][lang][entrynum] = {"audio": audio, "time": time, "lang": lang}
      this.audioPlaying = false;
  
      this.record = document.querySelector('.audio-record');
      this.stop = document.querySelector('.audio-stop');
      this.canvas = document.querySelector('.audio-visualizer');
      this.audioCtx = null;
      this.player = document.getElementById('my-audio');
      this.player.volume = 0.5; //default volume
      this.chunks = [];
      this.lang = lang;

      const constraints = { audio: true };
      navigator.mediaDevices.getUserMedia(constraints).then(this.onSuccess, this.onError);

    }

    onSuccess = function(stream) {
        const mediaRecorder = new MediaRecorder(stream);

        
        as[myaslang].visualize(stream);
    
        as[myaslang].record.onclick = function() {
          mediaRecorder.start();
          console.log(mediaRecorder.state);
          console.log("recorder started");
          as[myaslang].record.style.background = "red";
    
          as[myaslang].stop.disabled = false;
          as[myaslang].record.disabled = true;
        }
    
        as[myaslang].stop.onclick = function() {
          mediaRecorder.stop();
          console.log(mediaRecorder.state);
          console.log("recorder stopped");
          as[myaslang].record.style.background = "";
          as[myaslang].record.style.color = "";
          // mediaRecorder.requestData();
    
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
  
  