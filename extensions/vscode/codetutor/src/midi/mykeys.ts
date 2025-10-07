//adopt from mykeys.py
//def 
import { AudioContext, OscillatorNode, GainNode } from 'node-web-audio-api';

let playfeedback = true;
let pedal = false;
let volumeControl = "0.1";
const ATTACK_TIME = 0.2;
const SUSTAIN_LEVEL = 0.8;
const RELEASE_TIME = 0.2;


export class MyKeys {
    keys: Number[]; //array of ints
    sequence: Number[]; //array of ints
    config: any;
    words: string[];
    languages: any;
    currentlang: string;
    transcripts: any;
    currentseqno: number = 0;
    startseqno: number = 0;
    lastnote: any;
    lastnotetime: number = 0;
    currentcmd: string = '';
    currentmidiuser: number = 0;
    start: number = (new Date()).getTime();
    notes: any[];
    audioContext: AudioContext;
    mainGainNode = null;
    midiarray: any;
    keybot: any = {};
    midiUICallback = null;
    constructor(config = {}) {
        this.keys = [];
        this.config = config;
        this.sequence = [];
        this.words = [];
        this.languages = {};
        this.currentlang = '';
        this.transcripts = {};
        this.currentseqno = 0;
        this.startseqno = 0;
        this.lastnotetime = 0;
        this.lastnote = null;
        this.currentcmd = '';
        this.currentmidiuser = 0;
        this.midiarray = [{}]; //user, lang, array of notes


        this.notes = Array(120).fill({
            note: 0,
            velocity: 0,
            time: 0,
            duration: 0,
            user: 0
        });
        this.audioContext = new AudioContext(); //(window.AudioContext || (window as any).webkitAudioContext)();
        this.setupAudioFeedback();
        this.setupMidi();

        if (config['keymap']['languages']) {
            for (const [lang, val] of Object.entries(config['keymap']['languages'])) {
                //dynamically load languages.  
                console.log("loading language", lang, val);
                //web/public/languages/base.js
                this.languages[lang] = val;
                this.transcripts[lang] = [];
            }
            this.currentlang = Object.keys(this.languages)[0];
        }

    }    

    key(msg, myTime = 0, midiCb = null){
        console.log("key", msg);
        this.lastnotetime = (new Date()).getTime();

        if (myTime === 0){
            myTime = - (this.lastnotetime - this.start);  //current time in ms
        }
        let lang = this.currentlang;
        let midiuser = this.currentmidiuser;
        if (midiCb) {
            midiCb(msg, myTime, lang, midiuser);
        }
        
        const command = msg[0];
        const note = msg[1];
        const velocity = msg.length > 2 ? msg[2] : 0;
        const absTime = myTime > 0 ? myTime : myTime;

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
                if (note%12 === 0){
                    //check commands here.  
//                    triggerCheckCommands();
                }
                break;

            case 176: // pedal
                pedal = velocity > 0;
                if (!pedal) {
                    //triggerCheckCommands();
                }
                break;
        }

        //get detailed note of message and push to sequence.  
        //right now only sequence is significant.  
    }

    noteOn(note, velocity, abstime, myTime = 0, lang = "") {
        if (lang==""){
            lang = this.currentlang;
        }
            
        let osc = null;
        let pnote = null;
        
        if (myTime <= 0 && playfeedback) {
            osc = this.playTone(this.midiToFreq(note, velocity));
        }

        var obj = {"note": note, "velocity": velocity, "time": abstime, "duration": 0, osc: osc, pnote: pnote, complete: false, user: this.currentmidiuser, created: Date.now()};

        if (myTime > 0) {
            obj.complete = true;
        }

        this.notes[note] = obj;
    }

    noteOff(note, abstime, lang = "") {
        if (lang==""){
            lang = this.currentlang;
        }
    
        const obj = this.notes[note];
        if (obj.osc) {
            obj.osc.stop();
        }
        if (obj.pnote) {
            obj.pnote.stop();
        }

        let clone = Object.assign({}, obj);
        clone.duration = abstime - obj.time;
    
        if (this.lastnote && this.lastnote.note === obj.note && this.lastnote.time === obj.time) {
        }
        else{
            this.lastnote = obj;
            this.insertNote(clone, lang);
            obj.velocity = 0;
            this.notes[note] = obj;
    
        }

    }

    insertNote(note, lang = "") {
        if (lang == ""){
            lang = this.currentlang;	
        }
        let i=this.midiarray[this.currentmidiuser][lang].length-1;

        while (i >-1 && note.time < this.midiarray[this.currentmidiuser][lang][i].time){		
            i--;
        }
    
		this.midiarray[this.currentmidiuser][lang].splice(i+1, 0, note);

        if (this.midiUICallback) {
            this.midiUICallback(this.currentmidiuser, note);
        }
    }
 
    playTone(freq) {
//        return null; //disable for now.
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

    setupAudioFeedback() {
        this.mainGainNode = this.audioContext.createGain();
        this.mainGainNode.connect(this.audioContext.destination);
        this.mainGainNode.gain.value = volumeControl;



    }

    setupMidi() {
        this.midiarray = [{"base": [], "meta": []}];
        this.keybot["base"] = 48;
        this.keybot["meta"] = 48;
        this.currentmidiuser = 0;
        this.start = Date.now();
//        reinitLanguages();
//        loadUserConfig();
//        loadDictionaries(currentmidiuser);

    }
    
}

