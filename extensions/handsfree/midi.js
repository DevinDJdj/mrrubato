var midiarray = [];
var notes = [];
var midienabled = 0;
var obj = {"note": 0, "velocity": 0, "time": 0, "duration": 0};

//create sound easy
const audioContext = new AudioContext();
let mainGainNode = null;
const wavePicker = "triangle" //document.querySelector("select[name='waveform']");
//add logic to get a nicer sound.  Can get piano sounds or other perhaps.  
//i.e. https://www.gregjopa.com/2023/03/piano-sounds-with-web-audio-api
const volumeControl = "0.1" //document.querySelector("input[name='volume']");
let sineTerms = null;
let cosineTerms = null;

let attackTime = 0.2;
let sustainLevel = 0.8;
let releaseTime = 0.2;

let recentTime = 4000;


//for notes.  
var _instr = [
'Acoustic Grand Piano', 'Bright Acoustic Piano', 'Electric Grand Piano', 'Honky-tonk Piano', 'Electric Piano 1', 'Electric Piano 2', 'Harpsichord', 'Clavinet', 
'Celesta', 'Glockenspiel', 'Music Box', 'Vibraphone', 'Marimba', 'Xylophone', 'Tubular Bells', 'Dulcimer', 
'Drawbar Organ', 'Percussive Organ', 'Rock Organ', 'Church Organ', 'Reed Organ', 'Accordion', 'Harmonica', 'Tango Accordion', 
'Acoustic Guitar (nylon)', 'Acoustic Guitar (steel)', 'Electric Guitar (jazz)', 'Electric Guitar (clean)', 'Electric Guitar (muted)', 'Overdriven Guitar', 'Distortion Guitar', 'Guitar Harmonics', 
'Acoustic Bass', 'Electric Bass (finger)', 'Electric Bass (pick)', 'Fretless Bass', 'Slap Bass 1', 'Slap Bass 2', 'Synth Bass 1', 'Synth Bass 2', 
'Violin', 'Viola', 'Cello', 'Contrabass', 'Tremolo Strings', 'Pizzicato Strings', 'Orchestral Harp', 'Timpani', 
'String Ensemble 1', 'String Ensemble 2', 'Synth Strings 1', 'Synth Strings 2', 'Choir Aahs', 'Voice Oohs', 'Synth Choir', 'Orchestra Hit', 
'Trumpet', 'Trombone', 'Tuba', 'Muted Trumpet', 'French Horn', 'Brass Section', 'Synth Brass 1', 'Synth Brass 2', 
'Soprano Sax', 'Alto Sax', 'Tenor Sax', 'Baritone Sax', 'Oboe', 'English Horn', 'Bassoon', 'Clarinet', 
'Piccolo', 'Flute', 'Recorder', 'Pan Flute', 'Blown Bottle', 'Shakuhachi', 'Whistle', 'Ocarina', 
'Lead 1 (square)', 'Lead 2 (sawtooth)', 'Lead 3 (calliope)', 'Lead 4 (chiff)', 'Lead 5 (charang)', 'Lead 6 (voice)', 'Lead 7 (fifths)', 'Lead 8 (bass + lead)', 
'Pad 1 (new age)', 'Pad 2 (warm)', 'Pad 3 (polysynth)', 'Pad 4 (choir)', 'Pad 5 (bowed)', 'Pad 6 (metallic)', 'Pad 7 (halo)', 'Pad 8 (sweep)', 
'FX 1 (rain)', 'FX 2 (soundtrack)', 'FX 3 (crystal)', 'FX 4 (atmosphere)', 'FX 5 (brightness)', 'FX 6 (goblins)', 'FX 7 (echoes)', 'FX 8 (sci-fi)', 
'Sitar', 'Banjo', 'Shamisen', 'Koto', 'Kalimba', 'Bagpipe', 'Fiddle', 'Shanai', 
'Tinkle Bell', 'Agogo', 'Steel Drums', 'Woodblock', 'Taiko Drum', 'Melodic Tom', 'Synth Drum', 'Reverse Cymbal', 
'Guitar Fret Noise', 'Breath Noise', 'Seashore', 'Bird Tweet', 'Telephone Ring', 'Helicopter', 'Applause', 'Gunshot'
];


for (let i=0; i<120;i++){
	obj.note = i;
	notes.push(obj);
}

var prevtime = 0;
var prevvelocity = 0;
var start = 0;
var audioSamples = {'p': [], 'link': [], 'image': [], 'text':[]};


function loadSample(url){
    return (
      fetch(url)
        .then((response) => response.arrayBuffer())
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        .then((buffer) => audioContext.decodeAudioData(buffer))
    );
  }

function loadPianoSounds() {
	//probably should load all actual sounds, but good enough for now.  
	//not great audio quality.  
    const fileNames = ["C2v10", "C3v10", "C4v10", "C5v10", "C6v10", "C7v10"];

    Promise.all(
      fileNames.map((fileName) =>
        loadSample(
          './audio/' + fileName + '.mp3'
		)
      )
    ).then((audioBuffers) => {
	    audioSamples['p'] = audioBuffers;
    });

}

function loadSounds(folder = 'link', mapstr = 'link') {
	//probably should load all actual sounds, but good enough for now.  
	//not great audio quality.  
    const fileNames = ["C3", "C4", "C5"];

    Promise.all(
      fileNames.map((fileName) =>
        loadSample(
          './audio/' + folder + '/' + fileName + '.mp3'
		)
      )
    ).then((audioBuffers) => {
	    audioSamples[mapstr] = audioBuffers;
    });

}

function audioFeedback(midinote=60, velocity=100, timeout=500){
	//not sure why this is not playing?  Interaction with page?  
	//how do we get better timing for this?  Or is this good enough?  
	//we may need a callback to call the next note.  
	var a = playNote(midinote, velocity); //indicate we have loaded the page.  
	setTimeout(() => {
	  a.stop();
	  //callback to call next note.  Is there a better mechanism?  
	  //should think about this a bit more.  
	}, timeout);

}

function setupAudioFeedback(){
	mainGainNode = audioContext.createGain();
	mainGainNode.connect(audioContext.destination);
	mainGainNode.gain.value = volumeControl;
	const now = Date.now();
	start = now;

	loadPianoSounds();
	loadSounds('link', 'link');
	loadSounds('frenchhorn', 'image');
	loadSounds('viola', 'text');
	audioFeedback(60, 100, 500);
	audioFeedback(64, 100, 500);
	audioFeedback(68, 100, 500);

  
}

function midiToFreq(midinum, velocity=0){
	freq = 440;
	if (velocity > 0){
		freq *= Math.pow(2, (midinum - 69) / 12); 
		console.log(freq);
		return freq;
	}
	else{
		return 0;
	}

}

function playNote(midinum, velocity=0){
//	return null;
	octave = Math.round(midinum/12);
	//C4 is 60
	notevalue = midinum%12;
	if (notevalue > 5) {
		notevalue -= 12;
		//this rounds up from 6-11
	}	

	if (octave > 1 && octave < 8 && velocity > 0){
		sample = audioSamples['p'][octave-2];
		const source = audioContext.createBufferSource();
		source.buffer = sample;
		// first try to use the detune property for pitch shifting
		if (source.detune) {
			source.detune.value = notevalue * 100;
		} else {
			// fallback to using playbackRate for pitch shifting
			source.playbackRate.value = 2 ** (noteValue / 12);
		}

		

		const panNode = audioContext.createStereoPanner()
		panNode.pan.value = Math.random(); // center -1 left, 1 right
		if (Math.random() > 0.5) {
			panNode.pan.value = -panNode.pan.value;
		}
		source.connect(mainGainNode).connect(panNode).connect(audioContext.destination)

//		source.connect(audioContext.destination);
		source.start();
		notes[midinum].pnote = source;
		return source;

	}
	/*
	if (midinum > 40 && midinum < 80 && velocity > 0){
		fetch("./audio/C4v10.mp3")
		.then((response) => response.arrayBuffer())
		.then((buffer) => audioContext.decodeAudioData(buffer))
		.then((sample) => {
		const source = audioContext.createBufferSource();
		source.buffer = sample;
		source.connect(audioContext.destination);
		source.start();
		notes[midinum].pnote = source;
		return source;
		});
	}
	*/
}

function playTone(freq) {
	return null;
	console.log("playing feedback " + freq);
	const osc = audioContext.createOscillator();
	osc.connect(mainGainNode);
  
	mainGainNode.gain.setValueAtTime(0, 0);
	  mainGainNode.gain.linearRampToValueAtTime(sustainLevel, audioContext.currentTime + attackTime);
	  mainGainNode.gain.setValueAtTime(sustainLevel, audioContext.currentTime + 1 - releaseTime);
	  mainGainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 1);
  
	const type = wavePicker;
  
	if (type === "custom") {
	  osc.setPeriodicWave(customWaveform);
	} else {
	  osc.type = type;
	}
  
	osc.frequency.value = freq;
	osc.start();
  
	return osc;
  }
  

function load(data, feedback=false) {
  try {
//	data = data.substring(data.indexOf(',')+1);
    smf = JZZ.MIDI.SMF(data);
	console.log(smf.dump());
	console.log(smf);
	console.log(smf[0].smfBPM());
	//smf[0]
	for (i=0; i<smf[0].length;i++){
		if (smf[0][i][1] == 107 || smf[0][i][1] == 108 || smf[0][i][1] == 21){
			console.log(smf[0][i]);
			//use this as the timing basis, then just use TT variable here.  
			//match up with start/end times.  
			//smf[0][i].tt
		}
		if (feedback == true && (smf[0][i][0] == 144 || smf[0][i][0] == 128)){
			
			getMIDIMessage(smf[0][i], Math.round(smf[0][i].tt*10)); 
			//*10 because we have 100 ppqn and 60 bpm and we need milliseconds
		}
		//0 = 144?  channel 1
		//1 = note
		//2 = velocity (0=off)
	}
	/*
	MidiParser.parse( smf.toUint8Array(), function(obj){
		// Your callback function
		console.log(obj);
		console.log(obj.track[0].event[0]);

//            document.getElementById("output").innerHTML = JSON.stringify(obj, undefined, 2);
	});
	*/
	//ok so now we have to utilize this.  
	//load into midiarray somehow.  
	return smf;
  }
  catch (e) {
    console.log(e);
  }
}


function getWords(b){
	//need to do same as analyze.py and get the Words.  
	//then match up across iterations.  
	//analyze.py getNgrams
	//not sure this is the best sample.  Maybe rethink this.  
	//what struct do we want.  
	//javascript int is accurate to 15 digits.  
	//maybe just use 7-letter word held in int using MIDI key numbers.  
	//this can be used along with other structs.  
	//then we can compare after/before to have a sequence of same or not same.  
	//have a running count as we build the similartity struct.  
    //still build the pgram struct, and signgram
	//seqngram is ok I guess.  
	//pgram and seqngram distinguish the structure.  
	//what rythm ngram do we want?  
	//relative time based on longest note.  
//	window.open(b, '_blank', 'resizable, width=1020,height=600');
	load(b);
	//not sure if this works.  Really we want more detailed info here, but for now whatever we can load.  
	//JZZ load failing for some reason.  
	//I think JZZ and MIDO are somehow incompatible.  
	/*
	const uint8array = new Uint8Array(b.length);
	for (let i = 0; i < b.length; i++) {
	  uint8array[i] = b.charCodeAt(i);
	}
	var decoder = new TextDecoder('utf8');
	var b64encoded = btoa(uint8array);

	load(JZZ.lib.fromBase64(b64encoded));
*/
	

	
}

function getFile(url){
	//getting the original midi file for the video
		var xhr = new XMLHttpRequest();
		xhr.open('GET', url, true);
		xhr.overrideMimeType("application/x-binary; charset=ISO-8859-1");
//		xhr.responseType = 'binary';
		xhr.onload = function(e) {
		  if (this.status == 200) {
			var myBlob = this.response;
			// myBlob is now the blob that the object URL pointed to.
			/*
			let reader = new FileReader();
			reader.readAsDataURL(myBlob); // converts the blob to base64 and calls onload
			reader.onload = function() {
			  console.log(reader.result);
			  getWords(reader.result);
			}
			*/
			/*
			const myFile = new File([myBlob], 'current.mid', {
				type: myBlob.type,
			});
			
			console.log(myFile);
			*/
			console.log(myBlob);
			getWords(myBlob);
		  }
		};
		xhr.send();
}


function showMidi(){
	var source = document.getElementById('filereader');
	MidiParser.parse( source, function(obj){
		// Your callback function
		console.log(obj);
		console.log(obj.track[0].event[0]);

//            document.getElementById("output").innerHTML = JSON.stringify(obj, undefined, 2);
	});

}

function loadMidiFeedback(mid){
	if (mid !==null && mid !=""){
		//this is feedback
		load(JZZ.lib.fromBase64(mid), true);
		//clear notes
	}
}

function getMidiFeedback(){
	//
	var smf = new JZZ.MIDI.SMF(1, 100); //this second param is ppqn pulses per quarter note

	// Add MIDI file tracks:
	var trk0 = new JZZ.MIDI.SMF.MTrk(); smf.push(trk0); // First track in Type 1 MIDI file is normally used for tempo changes
	trk0.smfSeqName('Feedback')
    .smfBPM(60); // Tempo. Normally set at clock 0, but can be also changed later
	
	trk = trk0;
	prevtime = 0;
	if (midiarray.length == 0){
		return "";
		
	}
	
	for (i=0; i< midiarray.length; i++){
		tick = Math.round((midiarray[i].time-prevtime)/10);
	
		if (tick < 0){ tick = 0;console.log(midiarray[i]);}
		if (midiarray[i].duration < 0){midiarray[i].duration = 0;console.log(midiarray[i]);}
		trk = trk.ch(0).program(0x0b).tick(tick).note(midiarray[i].note, midiarray[i].velocity, Math.round(midiarray[i].duration/10));
		console.log(midiarray[i]);
		prevtime = midiarray[i].time;
	}
	trk.tick(100).smfEndOfTrack(); // otherwise it will end on clock 1690
	var str = smf.dump(); // MIDI file dumped as a string
	var b64 = JZZ.lib.toBase64(str); // convert to base-64 string
	var uri = 'data:audio/midi;base64,' + b64; // data URI

	// Finally, write it to the document as a link and as an embedded object:
//	document.getElementById('out').innerHTML = 'New file: <a download=my.mid href=' + uri + '>DOWNLOAD</a> <embed src=' + uri + ' autostart=false>';
    return uri;
}

function getMIDIMessage(message, mytime=0) {
	if (midienabled==0 && mytime==0){
		return;
	}
	var command = message[0];
	var note = message[1];
	var velocity = (message.length > 2) ? message[2] : 0; // a velocity value might not be included with a noteOff command

    if (mytime > 0){
		abstime = mytime;
	}
    else{
		if (typeof player !=='undefined' && player.getCurrentTime){
			var temptime = player.getCurrentTime();
			abstime = Math.round(temptime * 1000);
		}
		else{
			const now = Date.now();
			abstime = now - start;
		}
	}
		
	switch (command) {
		case 144: // noteOn
			if (velocity > 0) {
				noteOn(note, velocity, abstime);
				prevvelocity = velocity;
				prevtime = abstime;
			} 
			else {
				noteOff(note, abstime);
			}
			break;
		case 128: // noteOff
			noteOff(note, abstime);
			break;
		// we could easily expand this switch statement to cover other types of commands such as controllers or sysex
	}
}

function insertNote(note){
	//usually inserting last.  
	//fine for now.  
	i=midiarray.length-1;
	while (i >-1 && note.time < midiarray[i].time){		
		i--;
	}
	midiarray.splice(i+1, 0, note);
	
}

function noteOn(note, velocity, abstime){
	
    console.log("Note On " + note + " at " + abstime + " vel " + velocity);
	//make sound here.  
	osc = playTone(midiToFreq(note, velocity));
	pnote = playNote(note, velocity);
	//mark complete after used in transcript command.  
	var obj = {"note": note, "velocity": velocity, "time": abstime, "duration": 0, osc: osc, pnote: pnote, complete: false};
	
	notes[note] = obj;
//	midiarray.push(obj);
}

function noteOff(note, abstime){
	var obj = notes[note];
	if (obj.osc != null)
		obj.osc.stop();
	if (obj.pnote != null)
		obj.pnote.stop();
	let clone = Object.assign({}, obj);
	clone.duration = abstime - obj.time;
	
	console.log("Note Off " + note + " at " + abstime);
	//midiarray.push(clone);
	insertNote(clone);
	
	obj.velocity = 0;
	notes[note] = obj;
	
}

function getMidiRecent(){
	//get the most recent midi notes
	i=midiarray.length-1;
	while (i >-1 && midiarray[i].time > Date.now()-start-recentTime && midiarray[i].complete !== true){		
		i--;
	}
	if (i == midiarray.length-1){
		return null;
	}
	else{
		retarray = [];
		temp = midiarray.slice(i+1);
		for (j=0; j<temp.length; j++){
			retarray.push(temp[j]);
		}
		return retarray;
	}
}

      function onEnabled() {

		setupAudioFeedback();
		var tempDiv = $('#midi');
        if (WebMidi.inputs.length < 1) {
			tempDiv.after("No device detected.");
			document.body.innerHTML+= "No device detected.";
        } else {
          WebMidi.inputs.forEach((device, index) => {
			tempDiv.after(`${index}: ${device.name} <br>`);
            document.body.innerHTML+= `${index}: ${device.name} <br>`;
          });
        }

      	for (var input of WebMidi.inputs.values()) {
			input.channels[1].addListener("midimessage", (event) => {console.log(event); getMIDIMessage(event.data); });
			
			//input.onmidimessage = getMIDIMessage;
		}
		
        const mySynth = WebMidi.inputs[1];


		// const mySynth = WebMidi.getInputByName("TYPE NAME HERE!")

//        mySynth.channels[1].addListener("noteon", e => {
//          document.body.innerHTML+= `${e.note.name} <br>`;
//		  console.log(e);
//        });

      }

		  WebMidi
			.enable()
			.then(onEnabled)
			.catch(err => alert(err));
