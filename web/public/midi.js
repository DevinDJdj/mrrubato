//var midiarray = [[]]; //[{}]; //array of [user][language][array of notes]
var notes = [];
var lastmidirecent = [];
var ispaused = 0;
var midioffset = 0;

//this was meant for the same.  
var midienabled = 0;
//var playfeedback = true; //dont actually play the feedback by default.  
//add to config.js

var obj = {"note": 0, "velocity": 0, "time": 0, "duration": 0, "user": 0};

//create sound easy
const audioContext = new AudioContext();
let mainGainNode = null;
const wavePicker = "triangle" //document.querySelector("select[name='waveform']");
//add logic to get a nicer sound.  Can get piano sounds or other perhaps.  
//i.e. https://www.gregjopa.com/2023/03/piano-sounds-with-web-audio-api

let sineTerms = null;
let cosineTerms = null;

let attackTime = 0.2;
let sustainLevel = 0.8;
let releaseTime = 0.2;

let recentTime = 4000;



var commandLog = [];
var pendingCommands = [];
var lastcommand = "";
var lastcommandtime = 0;


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

var midimessagecallback = null;
var midiUIcallback = null;

var mySynthOutputs = null;



function getPedal(){
	return pedal;
}


//called from clock.js every second.  
//open-ended definitions must end with midi 60, 60.  
//add language, add word etc.  But 60, 60 not stored in keymap.  
//others will be defined in keymap.  
function checkCommands(lang="meta"){
    let cl = FUNCS.SPEECH.getPendingCommand(getPedal());


    let midi = getMidiRecent();
    let executed = false;
    //if most recent is too recent wait some more.  
    //otherwise we assume this is a completed command.  
    //also if we have punctuation/end command, we can continue.  
    if (midi != null){
        //clear out any midi or pending commands with 0,0,0
        //why ispaused here?  
        if (midi.length > 2 && midi[midi.length-1].note -keybot["meta"] == 0 && midi[midi.length-2].note -keybot["meta"] == 0 && midi[midi.length-3].note -keybot["meta"] == 0){
            for (let i=0; i<midi.length; i++){
                midi[i].complete = true;
            }
            FUNCS.SPEECH.deletePendingCommand();
            cl = null;
            completeMidi(midi, "meta");
            return "";
        }

        completeMidi(midi);
    }
    let transcript = "";
    let pending = false;
    let callback = null;
    if (cl != null){
                //we have a command.  
            //try to find if we have something to do with the midi.  
            //recurse to find the transcript needed.  
            //we will find scroll, then we need those parameters.  
        console.log(cl);
        transcript = cl.transcript;
        let prevtranscript = "";
        pending = cl.pending;
        let done = 1;
        while (done > 0 && midi !=null && midi.length > 0 && executed==false){
            transcript = transcript.trimStart();
            prevtranscript = transcript;
            //find words in current language.  

            [transcript, lang, found] = findCommand(transcript, midi, prevtranscript, lang);
            if (transcript != prevtranscript){

                done = completeMidi(midi, lang);
				lastspokenword = transcript.trim();
                //refresh midi with only incomplete commands.  
                if (transcript.endsWith(" ")){  //use space as indicator of more parameters needed.
                    //still waiting.  
                    cl.transcript = transcript;
                    //we have added to the pending command.  
                    //can continue the command with more midi
                    //no use case at the moment for this.  
                }
                else{
                    //attempt to execute complete command.  
                    executed = FUNCS.SPEECH.Chat(transcript, callback, pending); //add waspendingflag

                    transcript = "";
                }
            }
            else{
                if (transcript != cl.transcript){
                    cl.transcript = transcript;
                    cl.time = Date.now();
                }
                done = 0;
            }
        }
        
        //when does this occur? when we dont have midi.  
        if ((midi ==null || midi.length == 0) && transcript != ""){
            executed = FUNCS.SPEECH.Chat(transcript, callback, pending); //add waspendingflag
//            transcript = "";

        }

        //get rid of executed commands.  
        if (executed){
            commandLog.pop();
            transcript = "";
        }

        //get rid of incomplete commands.  
        if (Date.now() - cl.time > recentTime*2){ //recentTime in midi.js
            //allow for double the time to complete the command.  
            //pop from the pending commands?  Why keep useless history?  
            commandLog.pop();
            transcript = "";
        }

    }
    else{
        if ((midi != null && midi.length > 0)){
            console.log(midi);


            let prevtranscript = "";
            //get command.  
            let done = 1;
            while (done > 0 && midi.length > 0 && executed==false){
                prevtranscript = transcript;
                //get parameters.  
                [transcript, lang, found] = findCommand(transcript, midi, prevtranscript, lang);
                //have to set .complete to true.  
                //we add space to this
                if (transcript != prevtranscript){
                    done = completeMidi(midi, lang);
					lastspokenword = transcript.trim();
					
                    if (transcript.endsWith(" ")){  //use space as indicator of more parameters needed.
                        //still waiting.  in this case perhaps extend the pendingTime.  
                    }
                    else{
                        executed = FUNCS.SPEECH.Chat(transcript, callback, pending); //add waspendingflag
                        transcript = "";
                    }
                }
                else {
                    //we have 4 seconds to add the parameters for this call if .  
                    //still pending.  Just add pending command.  
                    //or ignore.  
                    done = 0;
                }
            }

            if (transcript !=""){
                if (transcript.endsWith(" ")){ //add pending command.  
                    FUNCS.SPEECH.addCommandLog(transcript, null, true, lang);
                    //single command.  Must have at least half a second open here or whatever the timer is open time in order to execute this command.  
                    //add a pending command, and if no more midi comes within half a second, we execute.  
                    //will need to adjust this timer for the user.  
                }
                else{
                    //should never end up here.  
                    executed = FUNCS.SPEECH.Chat(transcript, callback, pending); 
                    transcript = "";
                }
            }

        }
    }
    
    return transcript;

}


function completeMidi(midi, lang=""){
    let ret = 0;
    let reftime = getReferenceTime();
    while (midi.length > 0 && (midi[0].time < reftime-recentTime || midi[0].complete == true)){
        //complete midi commands that are too old.  
        
        midi[0].complete = true;
        //why did we have this here?  
        if (lang != currentlanguage){
            insertNote(midi[0], lang);
            removeNote(midi[0], currentlanguage);
        }
        midi.shift();
        ret++;
    }
    return ret;
}



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
//	audioFeedback(60, 100, 500);
//	audioFeedback(64, 100, 500);
//	audioFeedback(68, 100, 500);
	
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

function setFeedbackVolume(vol){
	//this is way too loud.  
	vol = vol/2;
	mainGainNode.gain.value = vol.toFixed(1);

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
  

function load(data, feedback=false, cb=null) {
	if (cb == null){
		cb = midimessagecallback;
	}
  try {

	var langstoload = [];
//	data = data.substring(data.indexOf(',')+1);
    smf = JZZ.MIDI.SMF(data);
	console.log(smf.dump());
	console.log(smf);
	console.log(smf[0].smfBPM());
	//
	//smf[trknum][0].dd;  //this is track name.  Not sure if we can use smfSeqName for this.
	for (trknum=0; trknum<smf.length; trknum++){
		lang = smf[trknum][0].dd;

		if (lang == "Feedback"){
			lang = "base";
		}
		else if (typeof(lang) == "undefined"){
			//not sure what this is, but doesnt really matter, there are no notes.  
			//seems to be loading twice somehow.  
			lang = "base";
		}
		//initialize midiarray for this track.  

		if (typeof(midiarray[currentmidiuser][lang]) === "undefined"){
			midiarray[currentmidiuser][lang] = [];
			langstoload.push(lang);
		}

		console.log("Load " + lang + ": " + smf[trknum].length);
		for (var li=0; li<smf[trknum].length;li++){
			if (smf[trknum][li][1] == 107 || smf[trknum][li][1] == 108 || smf[trknum][li][1] == 21){ //notes
//				console.log(smf[0][i]);
				//pass original as language to not display as feedback, maybe change in the future?  
				getMIDIMessage(smf[trknum][li], Math.round(smf[trknum][li].tt*10), "iterations", cb); 

				//use this as the timing basis, then just use TT variable here.  
				//match up with start/end times.  
				//smf[0][i].tt
			}
			if (feedback == true && (smf[trknum][li][0] == 144 || smf[trknum][li][0] == 128)){ //midicommands ON OFF
				//add to the right language.  
				
				getMIDIMessage(smf[trknum][li], Math.round(smf[trknum][li].tt*10), lang, cb); 
				//*10 because we have 100 ppqn and 60 bpm and we need milliseconds
			}
			else if (!feedback && (smf[trknum][li][0] == 144 || smf[trknum][li][0] == 128)){ //midicommands ON OFF
				getMIDIMessage(smf[trknum][li], Math.round(smf[trknum][li].tt*10), "original", cb); 
			}
			//0 = 144?  channel 1
			//1 = note
			//2 = velocity (0=off)
		}
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
	return langstoload;
//	return smf;
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

function getFile(url, cb1=null, cb2=null){
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
			if (cb1 !== null || cb2 !== null){
				midisetcallbacks(cb1, cb2);
			}
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
	langstoload = [];
	if (mid !==null && mid !=""){
		//this is feedback
		langstoload = load(JZZ.lib.fromBase64(mid), true);
		//clear notes
	}
	return langstoload;
}

function getMidiFeedback(midiuser=0){

	//
	var smf = new JZZ.MIDI.SMF(1, 100); //this second param is ppqn pulses per quarter note

	// Add MIDI file tracks for each language:
	//for each lang in midiarray[midiuser][lang]
	var tracks = {};
    for (const [lang, value] of Object.entries(midiarray[midiuser])) {
		tracks[lang] = new JZZ.MIDI.SMF.MTrk(); smf.push(tracks[lang]); // First track in Type 1 MIDI file is normally used for tempo changes
		tracks[lang].smfSeqName(lang)
		.smfBPM(60); // Tempo. Normally set at clock 0, but can be also changed later
		let trk = tracks[lang];

		prevtime = 0;
		if (midiarray[midiuser][lang].length == 0){
			//should never occur
		}
		else{		
			console.log("Save " + lang + ": " + midiarray[midiuser][lang].length);
			for (var mi=0; mi< midiarray[midiuser][lang].length; mi++){
				tick = Math.round((midiarray[midiuser][lang][mi].time-prevtime)/10);
			
				if (tick < 0){ tick = 0;console.log(midiarray[midiuser][lang][mi]);}
				if (midiarray[midiuser][lang][mi].duration < 0){midiarray[midiuser][lang][mi].duration = 0;console.log(midiarray[midiuser][lang][mi]);}
				trk = trk.ch(0).program(0x0b).tick(tick).note(midiarray[midiuser][lang][mi].note, midiarray[midiuser][lang][mi].velocity, Math.round(midiarray[midiuser][lang][mi].duration/10));
//				console.log(midiarray[midiuser][lang][mi]);
				prevtime = midiarray[midiuser][lang][mi].time;
				//set to complete.  This is so we dont continually look for commands.  
				//need to check if functioning as expected.  
				midiarray[midiuser][lang][mi].complete = true;
			}
			trk.tick(100).smfEndOfTrack(); // otherwise it will end on clock 1690
		}
	}
	//logic below for each

	/*
	var trk0 = new JZZ.MIDI.SMF.MTrk(); smf.push(trk0); // First track in Type 1 MIDI file is normally used for tempo changes
	trk0.smfSeqName('Feedback')
    .smfBPM(60); // Tempo. Normally set at clock 0, but can be also changed later
	
	trk = trk0;
	prevtime = 0;
	if (midiarray[midiuser].length == 0){
		return "";
		
	}
	
	for (i=0; i< midiarray[midiuser].length; i++){
		tick = Math.round((midiarray[midiuser][i].time-prevtime)/10);
	
		if (tick < 0){ tick = 0;console.log(midiarray[midiuser][i]);}
		if (midiarray[midiuser][i].duration < 0){midiarray[midiuser][i].duration = 0;console.log(midiarray[midiuser][i]);}
		trk = trk.ch(0).program(0x0b).tick(tick).note(midiarray[midiuser][i].note, midiarray[midiuser][i].velocity, Math.round(midiarray[midiuser][i].duration/10));
		console.log(midiarray[midiuser][i]);
		prevtime = midiarray[midiuser][i].time;
	}
	trk.tick(100).smfEndOfTrack(); // otherwise it will end on clock 1690
	*/

	var str = smf.dump(); // MIDI file dumped as a string
	var b64 = JZZ.lib.toBase64(str); // convert to base-64 string
	var uri = 'data:audio/midi;base64,' + b64; // data URI

	// Finally, write it to the document as a link and as an embedded object:
//	document.getElementById('out').innerHTML = 'New file: <a download=my.mid href=' + uri + '>DOWNLOAD</a> <embed src=' + uri + ' autostart=false>';
    return uri;
}


function midisetcallbacks(midicb=null, UIcb=null){
	midimessagecallback = midicb;
	midiUIcallback = UIcb;
}

function getMIDIMessage(message, mytime=0, lang="", midicb=null) {

	if (midicb == null){	
		midicb = midimessagecallback;
	}
	var tempDiv = $('#devices');
	var devhtml = "";
	WebMidi.inputs.forEach((device, index) => {
		devhtml += `${index}: ${device.name} (${device.state}) `;

//		document.body.innerHTML+= `${index}: ${device.name} <br>`;
		//device.octaveOffset
	  });

	if (lang == ""){
		//load languages.js before midi.js so this exists.  
		lang = currentlanguage;
	}
	//set current language.  Should be fine if this remains current language?  
	//best is if we keep track of the age of the tracks.  too much...
	//this screws things up.  
	//we can pass to the right track now.  
//		currentlanguage = lang;

	if (midicb !== null){	
		midicb(message, mytime, currentmidiuser, lang);
	}
	if (lang=="original" || lang=="iterations"){
		//just loading original piece here.  
		//could have a load function to find 
		return;
	}
	//other special language cases.  

	var command = message[0];
	if (command == 144 || command == 128){
		devhtml += " LastNote: " + message[1] + " (" + currentlanguage + ")";
	}
	else if (command > 144 && command < 160){
		devhtml += " LastNote: " + message[1] + " (" + currentlanguage + ")";
	}

	tempDiv.html(devhtml);

	var note = message[1];
	var velocity = (message.length > 2) ? message[2] : 0; // a velocity value might not be included with a noteOff command

    if (mytime > 0){
		abstime = mytime;
	}
	else{
		abstime = getReferenceTime(mytime);
		//we are generating the time, but do we want to 
	}
		
	switch (command) {
		case 144: // noteOn
		case 145:
		case 146:
		case 147:			
		case 148:
		case 149:
		case 150:			
		case 151:
		case 152:
		case 153:			
		case 154:			
		case 155:
		case 156:
		case 157:
		case 158:
		case 159:
			if (velocity > 0) {
				noteOn(note, velocity, abstime, mytime, lang);
				prevvelocity = velocity;
				prevtime = abstime;
			} 
			else {
				noteOff(note, abstime, lang);
			}
			break;
		case 128: // noteOff
		case 129:
		case 130:
		case 131:			
		case 132:
		case 133:
		case 134:			
		case 135:
		case 136:
		case 137:			
		case 138:			
		case 139:
		case 140:
		case 141:
		case 142:
		case 143:
			noteOff(note, abstime, lang);
			break;
		case 176: // pedal?  
			if (velocity > 0){
				pedal = false;
				triggerCheckCommands();
			}
			else{
				pedal = true;
			}

			break;
		// we could easily expand this switch statement to cover other types of commands such as controllers or sysex
	}
}

function removeNote(note, lang=""){
	if (lang==""){
		lang = currentlanguage;
	}
	//remove note from midiarray
	i=midiarray[currentmidiuser][lang].length-1;
	while (i >-1 && midiarray[currentmidiuser][lang][i].time > note.time){
		i--;
	}

	if (i > -1 && midiarray[currentmidiuser][lang][i].time == note.time && midiarray[currentmidiuser][lang][i].note == note.note){
		midiarray[currentmidiuser][lang].splice(i, 1);
	}

}

function insertNote(note, lang=""){
	//usually inserting last.  
	//fine for now.  
	//use currentlanguage
	//i = midiarray[currentmidiuser][currentlanguage].length-1;

	if (lang == ""){
		lang = currentlanguage;	
	}
	i=midiarray[currentmidiuser][lang].length-1;

	while (i >-1 && note.time < midiarray[currentmidiuser][lang][i].time){		
		i--;
	}
//	if (i == midiarray[currentmidiuser][lang].length-1 && note.time == midiarray[currentmidiuser][lang][i].time && note.note == midiarray[currentmidiuser][lang][i].note){
		//this note is already existing in the current language.  
		//this is a common scenario as we are adding to the current language.  
//	}
//	else{
		midiarray[currentmidiuser][lang].splice(i+1, 0, note);
	
	//updateFeedbackUI();
	if (midiUIcallback !== null){
		midiUIcallback(currentmidiuser, note);
	}
//	}
	
}

function noteOn(note, velocity, abstime, mytime=0, lang=""){ //mytime is the original time in the midi file, or 0 when playing live.  
	if (lang==""){
		lang = currentlanguage;
	}
	
//    console.log("Note On " + note + " at " + abstime + " vel " + velocity);
	//make sound here.  
	osc = null;
	pnote = null;
	if (mytime <= 0 && playfeedback){ //no feedback sound for existing midi files except in time.  Probably need to rewrite this area to read midi files.  
		osc = playTone(midiToFreq(note, velocity));
		pnote = playNote(note, Math.round(velocity/2)); //dont want this to be loud to detract from the ongoing video.  
	}
	var obj = {"note": note, "velocity": velocity, "time": abstime, "duration": 0, osc: osc, pnote: pnote, complete: false, user: currentmidiuser, created: Date.now()};
	
	if (mytime > 0){
		//this is loaded data.  
		obj.complete = true;
	}
	notes[note] = obj;
//	midiarray.push(obj);
}

function noteOff(note, abstime, lang=""){
	if (lang==""){
		lang = currentlanguage;
	}

	var obj = notes[note];
	if (obj.osc != null)
		obj.osc.stop();
	if (obj.pnote != null)
		obj.pnote.stop();
	let clone = Object.assign({}, obj);
	clone.duration = abstime - obj.time;
//	console.log("Note Off " + note + " at " + abstime);
	//midiarray.push(clone);

	if (lastnote !== null && lastnote.note == obj.note && lastnote.time == obj.time){
	}
	else{
		lastnote = obj;	
		insertNote(clone, lang);
		obj.velocity = 0;
		notes[note] = obj;
	}


	
}

function getReferenceTime(mytime=0){

	if ((useyoutube || watch) && player.getCurrentTime){
		var temptime = player.getCurrentTime();
	    abstime = Math.round(temptime * 1000);
	}
	else if (player2.currentTime){
		//use the other player time.  
		var temptime = player2.currentTime;
	    abstime = Math.round(temptime * 1000);

	}
	else{
		//if we cant get player time, we are getting seconds since page load essentially.  
		const now = Date.now();
		return now-start;
	}

	//need to clean this up maybe.  Think it should work ok.  
	//concern is when sending messages prior to starting video.  
	//potential to destroy logical sequences if there is overlap.  
	if (ispaused==1 && mytime<=0){
		midioffset +=1;
	}
	else{
		midioffset = 0;
		//probably should reset here if not paused.  
	}
	return abstime+midioffset; //add midioffset for when paused we can still get commands.  

}

function getMidiRecent(){
	//get the most recent midi notes
	//use video time as reference.  


	i=midiarray[currentmidiuser][currentlanguage].length-1;
	j=midiarray[currentmidiuser][currentlanguage].length-1;
	lasttime = getReferenceTime();
	//need window not just future.  
	while (i >-1 && midiarray[currentmidiuser][currentlanguage][i].time > lasttime-recentTime*2){
//		lasttime = midiarray[currentmidiuser][currentlanguage][i].time; //why -start?  
		if (midiarray[currentmidiuser][currentlanguage][i].time >= lasttime){
			j--;
		}
		i--;
		//now all midi is context if it is within the last 4 seconds of the previous midi and not complete.  
		//need 4 second gap to clear midi.  
	}
	if (i == midiarray[currentmidiuser][currentlanguage].length-1){
		return null;
	}
	else{
		retarray = [];
		temp = midiarray[currentmidiuser][currentlanguage].slice(i+1, j+1);
		for (j=0; j<temp.length; j++){
			if (temp[j].complete !== true){
				retarray.push(temp[j]);
			}
		}
		return retarray;
	}
}

//something like this need to test.  
function sendNote(note, velocity, lang=""){
	//preprocessor for language?  
	mySynthOutputs = mySynth.outputs;
	for (var output of mySynthOutputs.values()) {
		if (output.name == "Seaboard Block"){	
			output.playNote("C3", {duration:1000});
		}
		else{
			output.playNote("C3", {duration:1000});
		}
	}

}


      function onEnabled() {

		setupAudioFeedback();
		var tempDiv = $('#devices');
        if (WebMidi.inputs.length < 1) {
			tempDiv.html("No device detected.");
			document.addEventListener("keydown", function onPress(event) {
				msg = [];
				msg.push(144);

				var key = 0;
				var validkeys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='];
				if ((key = validkeys.indexOf(event.key)) > -1){
					if (event.shiftKey){
						key += 12;
					}						
					msg.push(key+keybot[currentlanguage]);
					getMIDIMessage(msg);
				}
			});

			document.addEventListener("keyup", function onPress(event) {
				msg = [];
				msg.push(128);

				var key = 0;
				var validkeys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='];
				if ((key = validkeys.indexOf(event.key)) > -1){
					if (event.shiftKey){
						key += 12;
					}						
					msg.push(key+keybot[currentlanguage]);
					getMIDIMessage(msg);
				}
				
			});
			
//			document.body.innerHTML+= "No device detected.";
        } else {
			var tempDiv = $('#devices');
			var devhtml = "";
			WebMidi.inputs.forEach((device, index) => {
				devhtml += `${index}: ${device.name} ( ${device.state} )<br>`;
		
		//		document.body.innerHTML+= `${index}: ${device.name} <br>`;
				//device.octaveOffset
			  });
			  tempDiv.html(devhtml);

			}

      	for (var input of WebMidi.inputs.values()) {
			if (input.name == "Seaboard Block"){
				console.log(input);
//				input.onmidimessage = (event) => {console.log(event); getMIDIMessage(event.data); };
				for (var i=2; i<16; i++){
					input.channels[i].addListener("midimessage", (event) => {console.log(event); getMIDIMessage(event.data, -(event.timestamp)); });
					//ok getting messages, but no idea the meaning.  

				}
			}
			else{
				input.channels[1].addListener("midimessage", (event) => {console.log(event); getMIDIMessage(event.data, -(event.timestamp)); });
			}
	//		input.channels[1].addListener("midimessage", (event) => {console.log(event); getMIDIMessage(event.data); });
			
			//input.onmidimessage = getMIDIMessage;
		}
		
        const mySynth = WebMidi.inputs[1];
		mySynthOutputs = WebMidi.outputs;

        // const mySynth = WebMidi.getInputByName("TYPE NAME HERE!")

//        mySynth.channels[1].addListener("noteon", e => {
//          document.body.innerHTML+= `${e.note.name} <br>`;
//		  console.log(e);
//        });

      }


	  function setupMidi(){

			midiarray = [{"base": []}]; //reinitialize necessary?  
			currentmidiuser = 0;

			reinitLanguages();
			loadUserConfig(); //have to do this in case there is a new language keybot.  
			loadDictionaries(currentmidiuser);
			for (const [lang, value] of Object.entries(midiarray[currentmidiuser])) {
		//        loadLanguage(lang, currentmidiuser);
		//        initLangData(lang, user);
			}

			//selectLanguage("doodle");
			keybot["base"] = 24; //one-key commands cause issues.  
					
	  }

	  WebMidi
	  .enable()
	  .then(onEnabled)
	  .catch(err => alert(err));
