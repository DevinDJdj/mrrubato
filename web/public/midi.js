var midiarray = [];
var notes = [];
var midienabled = 0;
var obj = {"note": 0, "velocity": 0, "time": 0, "duration": 0};

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

function getMIDIMessage(message) {
	if (midienabled==0){
		return;
	}
	var command = message.data[0];
	var note = message.data[1];
	var velocity = (message.data.length > 2) ? message.data[2] : 0; // a velocity value might not be included with a noteOff command

    const now = Date.now();
	abstime = now - start;
    if (player.getCurrentTime)
		var temptime = player.getCurrentTime();
	    abstime = Math.round(temptime * 1000);

	switch (command) {
		case 144: // noteOn
			if (velocity > 0) {
				noteOn(note, velocity, abstime);
				prevvelocity = velocity;
				prevtime = abstime;
			} else {
				noteOff(note, abstime);
			}
			break;
		case 128: // noteOff
			noteOff(note, abstime);
			break;
		// we could easily expand this switch statement to cover other types of commands such as controllers or sysex
	}
}

function noteOn(note, velocity, abstime){
	
    console.log("Note On " + note + " at " + abstime + " vel " + velocity);
	var obj = {"note": note, "velocity": velocity, "time": abstime, "duration": 0};
	notes[note] = obj;
//	midiarray.push(obj);
}

function noteOff(note, abstime){
	var obj = notes[note];
	let clone = Object.assign({}, obj);
	clone.duration = abstime - obj.time;
	
	console.log("Note Off " + note + " at " + abstime);
	midiarray.push(clone);
	
	obj.velocity = 0;
	notes[note] = obj;
	
}


      function onEnabled() {

        if (WebMidi.inputs.length < 1) {
          document.body.innerHTML+= "No device detected.";
        } else {
          WebMidi.inputs.forEach((device, index) => {
            document.body.innerHTML+= `${index}: ${device.name} <br>`;
          });
        }

      	for (var input of WebMidi.inputs.values()) {
			input.channels[1].addListener("midimessage", (event) => {console.log(event); getMIDIMessage(event);});
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
