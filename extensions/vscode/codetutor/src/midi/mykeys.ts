//adopt from mykeys.py
//def 
import { AudioContext, OscillatorNode, GainNode } from 'node-web-audio-api';

import * as vscode from 'vscode';
import * as Book from '../book';

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
    lasttick: number;
    words: string[];
    languages: any;
    transcripts: any;
    currentseqno: number = 0;
    startseqno: number = 0;
    lastnote: any;
    lastnotetime: number = 0;
    currentcmd: string = '';
    currentlangna: string = '';
    currentlang: Object = null;
    currentmidiuser: number = 0;
    start: number = (new Date()).getTime();
    notes: any[];
    audioContext: AudioContext;
    mainGainNode = null;
    midiarray: any;
    keybot: any = {};
    keymaps: any = {};
    midwordtree: any = {};
    midiUICallback = null;

    constructor(config = {}) {
        this.keys = [];
        this.config = config;
        this.lasttick = (new Date()).getTime();
        this.sequence = []; //current sequence of notes
        this.words = []; //current sequence of words
        this.languages = {}; //lang: {lang: [keys], module: module}
        this.currentlangna = '';
        this.currentlang = null;
        this.transcripts = {}; //lang: transcript
        this.currentseqno = 0;
        this.startseqno = 0;
        this.lastnotetime = 0;
        this.lastnote = null;
        this.currentcmd = ''; 
        this.currentmidiuser = 0;
        this.midiarray = [{}]; //user, lang, array of notes with time, note, velocity, duration
        //module values:
        //keybot
        //keyoffset - offset within octave
        //funcdict
        //config contains all keydict

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
                this.languages[lang] = {"module": null, "keys": val};
                this.transcripts[lang] = [];
            }
            this.currentlang = null;
        }
        this.importLanguages();

    }    

    async importLanguages(){
        for (const lang of Object.keys(this.languages)) {
            try{
                await this.importLanguageModule(lang);
            } catch (e){
                console.error("Error loading language", lang, e);
            }
        }
    }

    async makeTree(tree, keys, word, lang="") {
        let current = tree;
        for (const key of keys) {
            if (!current[key]) {
                current[key] = {};
            }
            current = current[key];
        }
        current['word'] = {'word': word, 'lang': lang, 'keys': keys};
    }

    //gen_lang_struct
    async updateKeyMaps(lang) {
        if (this.languages[lang]["module"] !== null) {
            let module = this.languages[lang]["module"];
            for (const [len, obj] of Object.entries(module.config['languages'][lang])) {
                for (const [word, keys] of Object.entries(obj)) {
                    //adjust keys for keybot and keyoffset
                    let v2 = keys.map(x => x + module.keybot + module.keyoffset);
                    this.makeTree(this.midwordtree, v2, word, lang);
                }
            }
        }
    }

    async importLanguageModule(lang) {
        if (this.languages[lang]["module"] !== null) {
            return;
        }
        //dynamically load languages.
        console.log("loading language", lang);
        //where are we here? why are we in /out..
        try{
            const module = await import(`../../src/languages/${lang}.js`);
            const langModule = module.default;
            this.languages[lang]["module"] = new langModule();
            //initialize language if needed.  
            this.languages[lang]["module"].init(this.config);
            this.updateKeyMaps(lang);
        } catch (e){
            console.error("Error loading language module", lang, e);
        }
    }

    key(msg, myTime = 0, midiCb = null){
        console.log("key", msg);
        this.lastnotetime = (new Date()).getTime();

        if (myTime === 0){
            myTime = - (this.lastnotetime - this.start);  //current time in ms
        }
        let lang = this.currentlangna;
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
        if (lang === ""){
            lang = this.currentlangna;
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
        this.mkey(note, velocity, abstime, myTime, lang);
    }

    reset_sequence(){
        this.sequence = [];
        this.words = [];
        this.currentcmd = '';
        this.currentlangna = '';
        this.currentlang = null;
        this.startseqno = 0;
        this.currentseqno = 0;
    }   

    findWord(sequence, lang) {
        let current = this.midwordtree;
        for (const key of sequence) {
            if (!current[key]) {
                return null;
            }
            current = current[key];
        }
        return current.word || null;
    }

    mkey(note, velocity, abstime, myTime = 0, lang = "") {
        if (lang === ""){
            lang = this.currentlangna;
        }

        let unsetseq = this.config['keymap']['global']['Unset'];
        let temptime = (new Date()).getTime() - this.lasttick;
        if (temptime > 10000 && this.sequence.length > 0) {
            this.reset_sequence();
        }
        this.lasttick = (new Date()).getTime();
        this.sequence.push(note);
        this.currentseqno += 1;

        console.log("mkey", note, velocity, abstime, myTime, lang);
        console.log("sequence", this.sequence);
        console.log("languages", this.languages);

        if (this.currentcmd === ""){
            let word = this.findWord(this.sequence, lang);
            if (word){
                let langModule = this.languages[word.lang]["module"];
                this.currentcmd = word.word;
                this.currentlangna = word.lang;
                this.currentlang = langModule;
                this.startseqno = this.currentseqno;
            }
        }
        if (this.currentcmd !== "" && this.currentlangna !== "" && this.currentlang !== null) {
            let ret = (this.currentlang as any).act(this.currentcmd, this.sequence.slice(this.startseqno), this.words);
            if (ret === -1) {
                //unknown command, reset sequence.  
                this.reset_sequence();
            }
            else if (ret === 0) {
                //command executed, reset sequence.  
                console.log(`> ${this.currentcmd}\n`);
                this.reset_sequence();


            }
            else if (ret === 1) {
                //more keys needed, do nothing.  
            }

        }

    }

    noteOff(note, abstime, lang = "") {
        if (lang === ""){
            lang = this.currentlangna;
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
            lang = this.currentlangna;	
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

