// Add at the top of the file

// Constants
const RECENT_TIME = 4000;
const ATTACK_TIME = 0.2;
const SUSTAIN_LEVEL = 0.8;
const RELEASE_TIME = 0.2;

// MIDI instrument names
const INSTRUMENTS = [
    'Acoustic Grand Piano', 'Bright Acoustic Piano', 'Electric Grand Piano', 'Honky-tonk Piano', 
    'Electric Piano 1', 'Electric Piano 2', 'Harpsichord', 'Clavinet',
    'Celesta', 'Glockenspiel', 'Music Box', 'Vibraphone', 'Marimba', 'Xylophone', 
    'Tubular Bells', 'Dulcimer',
    'Drawbar Organ', 'Percussive Organ', 'Rock Organ', 'Church Organ', 'Reed Organ', 
    'Accordion', 'Harmonica', 'Tango Accordion',
    'Acoustic Guitar (nylon)', 'Acoustic Guitar (steel)', 'Electric Guitar (jazz)', 
    'Electric Guitar (clean)', 'Electric Guitar (muted)', 'Overdriven Guitar', 
    'Distortion Guitar', 'Guitar Harmonics',
    'Acoustic Bass', 'Electric Bass (finger)', 'Electric Bass (pick)', 'Fretless Bass',
    'Slap Bass 1', 'Slap Bass 2', 'Synth Bass 1', 'Synth Bass 2',
    'Violin', 'Viola', 'Cello', 'Contrabass', 'Tremolo Strings', 'Pizzicato Strings',
    'Orchestral Harp', 'Timpani',
    'String Ensemble 1', 'String Ensemble 2', 'Synth Strings 1', 'Synth Strings 2',
    'Choir Aahs', 'Voice Oohs', 'Synth Choir', 'Orchestra Hit',
    'Trumpet', 'Trombone', 'Tuba', 'Muted Trumpet', 'French Horn', 'Brass Section',
    'Synth Brass 1', 'Synth Brass 2',
    'Soprano Sax', 'Alto Sax', 'Tenor Sax', 'Baritone Sax', 'Oboe', 'English Horn',
    'Bassoon', 'Clarinet',
    'Piccolo', 'Flute', 'Recorder', 'Pan Flute', 'Blown Bottle', 'Shakuhachi',
    'Whistle', 'Ocarina',
    'Lead 1 (square)', 'Lead 2 (sawtooth)', 'Lead 3 (calliope)', 'Lead 4 (chiff)',
    'Lead 5 (charang)', 'Lead 6 (voice)', 'Lead 7 (fifths)', 'Lead 8 (bass + lead)',
    'Pad 1 (new age)', 'Pad 2 (warm)', 'Pad 3 (polysynth)', 'Pad 4 (choir)',
    'Pad 5 (bowed)', 'Pad 6 (metallic)', 'Pad 7 (halo)', 'Pad 8 (sweep)',
    'FX 1 (rain)', 'FX 2 (soundtrack)', 'FX 3 (crystal)', 'FX 4 (atmosphere)',
    'FX 5 (brightness)', 'FX 6 (goblins)', 'FX 7 (echoes)', 'FX 8 (sci-fi)',
    'Sitar', 'Banjo', 'Shamisen', 'Koto', 'Kalimba', 'Bagpipe', 'Fiddle', 'Shanai',
    'Tinkle Bell', 'Agogo', 'Steel Drums', 'Woodblock', 'Taiko Drum', 'Melodic Tom',
    'Synth Drum', 'Reverse Cymbal',
    'Guitar Fret Noise', 'Breath Noise', 'Seashore', 'Bird Tweet', 'Telephone Ring',
    'Helicopter', 'Applause', 'Gunshot'
];

/**
 * Controller class for handling MIDI input/output and audio feedback
 */
export class MidiController {
    /**
     * Creates a new MidiController instance
     */
    constructor() {
        this.notes = Array(120).fill().map(() => ({
            note: 0,
            velocity: 0,
            time: 0,
            duration: 0,
            user: 0
        }));
        this.lastMidiRecent = [];
        this.isPaused = 0;
        this.midiOffset = 0;
        this.midiEnabled = 0;
        this.commandLog = [];
        this.pendingCommands = [];
        this.lastCommand = "";
        this.lastCommandTime = 0;
        this.start = Date.now();
        this.audioContext = new AudioContext();
        this.mainGainNode = null;
        this.audioSamples = {
            'p': [],
            'link': [],
            'image': [],
            'text': []
        };
        this.midiMessageCallback = null;
        this.midiUICallback = null;

    }


    getPedal(){
        return pedal;
    }
    /**
     * Loads a MIDI sample from a URL
     * @param {string} url - The URL of the audio sample
     * @returns {Promise<AudioBuffer>} The decoded audio data
     */
    async loadSample(url) {
        const response = await fetch(url);
        const buffer = await response.arrayBuffer();
        return await this.audioContext.decodeAudioData(buffer);
    }

    async loadPianoSounds() {
        const fileNames = ["C2v10", "C3v10", "C4v10", "C5v10", "C6v10", "C7v10"];
        const audioBuffers = await Promise.all(
            fileNames.map(fileName => this.loadSample(`./audio/${fileName}.mp3`))
        );
        this.audioSamples['p'] = audioBuffers;
    }

    async loadSounds(folder = 'link', mapstr = 'link') {
        const fileNames = ["C3", "C4", "C5"];
        const audioBuffers = await Promise.all(
            fileNames.map(fileName => 
                this.loadSample(`./audio/${folder}/${fileName}.mp3`)
            )
        );
        this.audioSamples[mapstr] = audioBuffers;
    }

    setupAudioFeedback() {
        this.mainGainNode = this.audioContext.createGain();
        this.mainGainNode.connect(this.audioContext.destination);
        this.mainGainNode.gain.value = volumeControl;

        this.start = Date.now();

        // Load all sound samples
        this.loadPianoSounds();
        this.loadSounds('link', 'link');
        this.loadSounds('frenchhorn', 'image');
        this.loadSounds('viola', 'text');
    }

    midiToFreq(midiNum, velocity = 0) {
        if (velocity > 0) {
            return 440 * Math.pow(2, (midiNum - 69) / 12);
        }
        return 0;
    }

    setFeedbackVolume(vol) {
        vol = vol / 2;
        this.mainGainNode.gain.value = vol.toFixed(1);
    }

    playNote(midiNum, velocity = 0) {
        const octave = Math.round(midiNum / 12);
        let noteValue = midiNum % 12;
        if (noteValue > 5) {
            noteValue -= 12;
        }

        if (octave > 1 && octave < 8 && velocity > 0) {
            const sample = this.audioSamples['p'][octave - 2];
            const source = this.audioContext.createBufferSource();
            source.buffer = sample;

            if (source.detune) {
                source.detune.value = noteValue * 100;
            } else {
                source.playbackRate.value = 2 ** (noteValue / 12);
            }

            const panNode = this.audioContext.createStereoPanner();
            panNode.pan.value = Math.random() * 2 - 1; // Random value between -1 and 1

            source.connect(this.mainGainNode)
                  .connect(panNode)
                  .connect(this.audioContext.destination);

            source.start();
            this.notes[midiNum].pnote = source;
            return source;
        }
        return null;
    }

    getReferenceTime() {
        //move to video.js get ref time from video player.  
        const vref = vgetReferenceTime();
        if (vref < 0){
            return Date.now() - this.start;
        }
        else{
            return vref + this.midiOffset;
        }
    }

    getMidiRecent() {
        const currentLang = midiarray[currentmidiuser][currentlanguage];
        let i = currentLang.length - 1;
        let j = currentLang.length - 1;
        const lastTime = this.getReferenceTime();

        while (i > -1 && currentLang[i].time > lastTime - RECENT_TIME * 2) {
            if (currentLang[i].time >= lastTime) {
                j--;
            }
            i--;
        }

        if (i === currentLang.length - 1) {
            return null;
        }

        const retArray = [];
        const temp = currentLang.slice(i + 1, j + 1);
        for (const note of temp) {
            if (note.complete !== true) {
                retArray.push(note);
            }
        }
        return retArray;
    }

    noteOn(note, velocity, absTime, myTime = 0, lang = "") {
        lang = lang || currentlanguage;
        
        let osc = null;
        let pNote = null;
        
        if (myTime <= 0 && playfeedback) {
            osc = this.playTone(this.midiToFreq(note, velocity));
            pNote = this.playNote(note, Math.round(velocity / 2));
        }

        const obj = {
            note,
            velocity,
            time: absTime,
            duration: 0,
            osc,
            pnote: pNote,
            complete: false,
            user: currentmidiuser
        };

        if (myTime > 0) {
            obj.complete = true;
        }

        this.notes[note] = obj;
    }

    noteOff(note, absTime, lang = "") {
        lang = lang || currentlanguage;

        const obj = this.notes[note];
        if (obj.osc) {
            obj.osc.stop();
        }
        if (obj.pnote) {
            obj.pnote.stop();
        }

        const clone = { ...obj, duration: absTime - obj.time };

        if (lastnote && lastnote.note === obj.note && lastnote.time === obj.time) {
            return;
        }

        lastnote = obj;
        this.insertNote(clone, lang);
        obj.velocity = 0;
        this.notes[note] = obj;
    }

    insertNote(note, lang = "") {
        lang = lang || currentlanguage;
        const currentLang = midiarray[currentmidiuser][lang];
        
        let i = currentLang.length - 1;
        while (i > -1 && note.time < currentLang[i].time) {
            i--;
        }

        currentLang.splice(i + 1, 0, note);

        if (this.midiUICallback) {
            this.midiUICallback(currentmidiuser, note);
        }
    }

    removeNote(note, lang = "") {
        lang = lang || currentlanguage;
        const currentLang = midiarray[currentmidiuser][lang];
        
        let i = currentLang.length - 1;
        while (i > -1 && currentLang[i].time > note.time) {
            i--;
        }

        if (i > -1 && 
            currentLang[i].time === note.time && 
            currentLang[i].note === note.note) {
            currentLang.splice(i, 1);
        }
    }

    getMIDIMessage(message, myTime = 0, lang = "", midiCb = null) {
        midiCb = midiCb || this.midiMessageCallback;
        
        if (this.isPaused === 1 && myTime <= 0) {
            this.midiOffset += 1;
        }

        lang = lang || currentlanguage;

        if (midiCb) {
            midiCb(message, myTime, currentmidiuser, lang);
        }

        if (lang === "original" || lang === "iterations") {
            return;
        }

        const command = message[0];
        const note = message[1];
        const velocity = message.length > 2 ? message[2] : 0;
        const absTime = myTime > 0 ? myTime : this.getReferenceTime();

        switch (command) {
            case 144: // noteOn
            case 145: case 146: case 147: case 148: case 149:
            case 150: case 151: case 152: case 153: case 154:
            case 155: case 156: case 157: case 158: case 159:
                if (velocity > 0) {
                    this.noteOn(note, velocity, absTime, myTime, lang);
                } else {
                    this.noteOff(note, absTime, lang);
                }
                break;

            case 128: // noteOff
            case 129: case 130: case 131: case 132: case 133:
            case 134: case 135: case 136: case 137: case 138:
            case 139: case 140: case 141: case 142: case 143:
                this.noteOff(note, absTime, lang);
                break;

            case 176: // pedal
                pedal = velocity > 0;
                if (!pedal) {
                    triggerCheckCommands();
                }
                break;
        }
    }

    getPendingCommand() {
        if (this.commandLog.length > 0 && this.commandLog[this.commandLog.length - 1].pending) {
            if (Date.now() - this.commandLog[this.commandLog.length - 1].time > RECENT_TIME * 2 && !pedal) {
                this.commandLog.pop();
                transcript = "";
                return null;
            }
            return this.commandLog[this.commandLog.length - 1];
        }
        return null;
    }

    checkCommands(lang = "meta") {
        let cl = this.getPendingCommand();
        let midi = this.getMidiRecent();
        let executed = false;

        if (midi != null) {
            // Clear out any midi or pending commands with 0,0,0
            if (midi.length > 2 && 
                midi[midi.length - 1].note - keybot["meta"] === 0 && 
                midi[midi.length - 2].note - keybot["meta"] === 0 && 
                midi[midi.length - 3].note - keybot["meta"] === 0) {
                
                midi.forEach(note => note.complete = true);
                this.commandLog.pop();
                cl = null;
                this.completeMidi(midi, "meta");
                return "";
            }

            this.completeMidi(midi);
        }

        let transcript = "";
        let pending = false;
        let callback = null;

        if (cl != null) {
            console.log(cl);
            transcript = cl.transcript;
            let prevTranscript = "";
            pending = cl.pending;
            let done = 1;

            while (done > 0 && midi != null && midi.length > 0 && executed === false) {
                transcript = transcript.trimStart();
                prevTranscript = transcript;

                [transcript, lang, found] = findCommand(transcript, midi, prevTranscript, lang);
                
                if (transcript !== prevTranscript) {
                    done = this.completeMidi(midi, lang);
                    lastspokenword = transcript.trim();

                    if (transcript.endsWith(" ")) {
                        cl.transcript = transcript;
                    } else {
                        executed = FUNCS.SPEECH.Chat(transcript, callback, pending);
                        transcript = "";
                    }
                } else {
                    if (transcript !== cl.transcript) {
                        cl.transcript = transcript;
                        cl.time = Date.now();
                    }
                    done = 0;
                }
            }

            if ((midi == null || midi.length === 0) && transcript !== "") {
                executed = FUNCS.SPEECH.Chat(transcript, callback, pending);
            }

            if (executed) {
                this.commandLog.pop();
                transcript = "";
            }

            if (Date.now() - cl.time > RECENT_TIME * 2) {
                this.commandLog.pop();
                transcript = "";
            }
        } else if (midi != null && midi.length > 0) {
            console.log(midi);
            let prevTranscript = "";
            let done = 1;

            while (done > 0 && midi.length > 0 && executed === false) {
                prevTranscript = transcript;
                let found = false;
                [transcript, lang, found] = findCommand(transcript, midi, prevTranscript, lang);

                if (transcript !== prevTranscript) {
                    done = this.completeMidi(midi, lang);
                    lastspokenword = transcript.trim();

                    if (transcript.endsWith(" ")) {
                        // Still waiting
                    } else {
                        executed = FUNCS.SPEECH.Chat(transcript, callback, pending);
                        transcript = "";
                    }
                } else {
                    done = 0;
                }
            }

            if (transcript !== "") {
                if (transcript.endsWith(" ")) {
                    FUNCS.SPEECH.addCommandLog(transcript, null, true);
                } else {
                    executed = FUNCS.SPEECH.Chat(transcript, callback, pending);
                    transcript = "";
                }
            }
        }

        return transcript;
    }

    completeMidi(midi, lang = "") {
        let ret = 0;
        const refTime = this.getReferenceTime();

        while (midi.length > 0 && (midi[0].time < refTime - RECENT_TIME || midi[0].complete === true)) {
            midi[0].complete = true;

            if (lang !== currentlanguage) {
                this.insertNote(midi[0], lang);
                this.removeNote(midi[0], currentlanguage);
            }
            midi.shift();
            ret++;
        }
        return ret;
    }

    audioFeedback(midiNote = 60, velocity = 100, timeout = 500) {
        const note = this.playNote(midiNote, velocity);
        if (note) {
            setTimeout(() => {
                note.stop();
            }, timeout);
        }
    }

    setupMidi() {
        midiarray = [{"base": [], "meta": []}];
        keybot["base"] = 48;
        keybot["meta"] = 48;
        currentmidiuser = 0;

//        reinitLanguages();
//        loadUserConfig();
//        loadDictionaries(currentmidiuser);

    }

    load(data, feedback = false, cb = null) {
        cb = cb || this.midiMessageCallback;

        try {
            const langsToLoad = [];
            const smf = JZZ.MIDI.SMF(data);
            console.log(smf.dump());
            console.log(smf);
            console.log(smf[0].smfBPM());

            for (let trkNum = 0; trkNum < smf.length; trkNum++) {
                let lang = smf[trkNum][0].dd;

                if (lang === "Feedback") {
                    lang = "base";
                } else if (typeof lang === "undefined") {
                    lang = "base";
                }

                if (typeof midiarray[currentmidiuser][lang] === "undefined") {
                    midiarray[currentmidiuser][lang] = [];
                    langsToLoad.push(lang);
                }

                console.log(`Load ${lang}: ${smf[trkNum].length}`);
                
                for (const event of smf[trkNum]) {
                    if (event[1] === 107 || event[1] === 108 || event[1] === 21) {
                        this.getMIDIMessage(event, Math.round(event.tt * 10), "iterations", cb);
                    }
                    
                    if (feedback && (event[0] === 144 || event[0] === 128)) {
                        this.getMIDIMessage(event, Math.round(event.tt * 10), lang, cb);
                    } else if (!feedback && (event[0] === 144 || event[0] === 128)) {
                        this.getMIDIMessage(event, Math.round(event.tt * 10), "original", cb);
                    }
                }
            }

            return langsToLoad;
        } catch (e) {
            console.log(e);
        }
    }

    loadMidiFeedback(mid) {
        const langsToLoad = [];
        if (mid !== null && mid !== "") {
            langsToLoad = this.load(JZZ.lib.fromBase64(mid), true);
        }
        return langsToLoad;
    }

    getMidiFeedback(midiUser = 0) {
        const smf = new JZZ.MIDI.SMF(1, 100); // ppqn = 100
        const tracks = {};

        // Add tracks for each language
        for (const [lang, value] of Object.entries(midiarray[midiUser])) {
            tracks[lang] = new JZZ.MIDI.SMF.MTrk();
            smf.push(tracks[lang]);
            
            tracks[lang]
                .smfSeqName(lang)
                .smfBPM(60);

            let prevTime = 0;
            
            if (midiarray[midiUser][lang].length > 0) {
                console.log(`Save ${lang}: ${midiarray[midiUser][lang].length}`);
                
                for (const midiEvent of midiarray[midiUser][lang]) {
                    const tick = Math.round((midiEvent.time - prevTime) / 10);
                    
                    if (tick < 0 || midiEvent.duration < 0) {
                        console.log(midiEvent);
                        midiEvent.duration = Math.max(0, midiEvent.duration);
                    }

                    tracks[lang] = tracks[lang]
                        .ch(0)
                        .program(0x0b)
                        .tick(tick)
                        .note(
                            midiEvent.note,
                            midiEvent.velocity,
                            Math.round(midiEvent.duration / 10)
                        );

                    prevTime = midiEvent.time;
                    midiEvent.complete = true;
                }
                
                tracks[lang].tick(100).smfEndOfTrack();
            }
        }

        const str = smf.dump();
        const b64 = JZZ.lib.toBase64(str);
        return 'data:audio/midi;base64,' + b64;
    }

    getFile(url, cb1 = null, cb2 = null) {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.overrideMimeType("application/x-binary; charset=ISO-8859-1");

        xhr.onload = () => {
            if (xhr.status === 200) {
                const myBlob = xhr.response;
                console.log(myBlob);
                this.getWords(myBlob);
                this.midisetcallbacks(cb1, cb2);
            }
        };
        xhr.send();
    }

    getWords(b) {
        this.load(b);
    }

    midisetcallbacks(midicb = null, UIcb = null) {
        this.midiMessageCallback = midicb;
        this.midiUICallback = UIcb;
    }

    async setupWebMidi() {
        try {
            await WebMidi.enable();
            this.setupAudioFeedback();

            const tempDiv = $('#devices');
            
            if (WebMidi.inputs.length < 1) {
                tempDiv.html("No device detected.");
                this.setupKeyboardListeners();
            } else {
                const devHtml = WebMidi.inputs
                    .map((device, index) => `${index}: ${device.name} ( ${device.state} )<br>`)
                    .join('');
                tempDiv.html(devHtml);
                this.setupMidiInputs();
            }
        } catch (err) {
            alert(err);
        }
    }

    setupKeyboardListeners() {
        document.addEventListener("keydown", (event) => {
            const validKeys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='];
            const keyIndex = validKeys.indexOf(event.key);
            
            if (keyIndex > -1) {
                const msg = [144];
                let key = keyIndex;
                if (event.shiftKey) {
                    key += 12;
                }
                msg.push(key + keybot[currentlanguage]);
                this.getMIDIMessage(msg);
            }
        });

        document.addEventListener("keyup", (event) => {
            const validKeys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='];
            const keyIndex = validKeys.indexOf(event.key);
            
            if (keyIndex > -1) {
                const msg = [128];
                let key = keyIndex;
                if (event.shiftKey) {
                    key += 12;
                }
                msg.push(key + keybot[currentlanguage]);
                this.getMIDIMessage(msg);
            }
        });
    }

    setupMidiInputs() {
        for (const input of WebMidi.inputs.values()) {
            if (input.name === "Seaboard Block") {
                console.log(input);
                for (let i = 2; i < 16; i++) {
                    input.channels[i].addListener("midimessage", 
                        event => {
                            console.log(event);
                            this.getMIDIMessage(event.data, -(event.timestamp));
                        }
                    );
                }
            } else {
                input.channels[1].addListener("midimessage",
                    event => {
                        console.log(event);
                        this.getMIDIMessage(event.data, -(event.timestamp));
                    }
                );
            }
        }
    }

    playTone(freq) {
        if (!freq) return null;

        console.log("playing feedback " + freq);
        const osc = this.audioContext.createOscillator();
        osc.connect(this.mainGainNode);

        this.mainGainNode.gain.setValueAtTime(0, 0);
        this.mainGainNode.gain.linearRampToValueAtTime(
            SUSTAIN_LEVEL,
            this.audioContext.currentTime + ATTACK_TIME
        );
        this.mainGainNode.gain.setValueAtTime(
            SUSTAIN_LEVEL,
            this.audioContext.currentTime + 1 - RELEASE_TIME
        );
        this.mainGainNode.gain.linearRampToValueAtTime(
            0,
            this.audioContext.currentTime + 1
        );

        osc.frequency.value = freq;
        osc.start();

        return osc;
    }
}

