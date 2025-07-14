var MAX_COMMANDLENGTH = 6;
var currentlanguage = "base";
var EOW = 12; //end of word
var OCTAVE = _octave; //from config.js
//for now two octave structure.  12 keys per octave.  This should be changeable though.  

function text2num(s) {
    a = s.toString().split(/[\s-]+/);
    n = 0;
    g = 0;
    a.forEach(feach);
    return n + g;
}

function getNum(str){
    mynum = parseInt(str);
    if (isNaN(mynum)){
        mynum = text2num(str);
    }
    if (isNaN(mynum)){
        return -1;
    }
    else{
        return mynum;
    }
}




class Keymap{
    constructor(lang="meta"){
        this.keys = [];
        this.lang=lang;
        this.chat = null;
        this.load = null;
        this.keymap = []; //midinum - 48
        this.langdict = {}; //this should contain "lang": {"keymap": [], "keydict": {}, "funcdict": {}}
        this.vars = {};
        this.settings = {};
        this.keydict = {};
        this.keydict[""] = {};
        this.funcdict = {};
        this.funcdict[""] = function(transcript, midi, keydict, key){ return transcript;};
        this.currentprefix = "";
        this.currentsuffix = "";
    }

    //add a word to this dictionary for transcript usage.  
    addWord(key, value){
        //add entry from dictionary.  
        m = value.midi.split(",");
        if (m > 0){
            if (typeof(this.keydict[""][m.length.toString()]) === "undefined"){
                this.keydict[""][m.length.toString()] = {};
            }
            this.keydict[""][m.length.toString()][value.midi] = key;
            this.funcdict[key] = function(transcript, midi, keydict, key){            
                return transcript; //add language xxxx 2,3,4
            };
        }

    }

    loadKeys(){
        //spoken work + key = action
        //keydict["keyword"]["numkeys"]["key,key,key"] = "action"
        //find word command, if doesnt exist, we can search this blank dict, and if it keys match, we can see if the 
        //word represents a number.  If it does, we can use that number in the command.
        //i.e. "0,5,12" + "fifteen" = "tab 15"
        //lookup word command if it doesnt exist, use this map.  
        //anything ending in 0 is standalone command.  and doesnt require a word.  
        //ending in 12 requires continuation or additional word/parameter
        //otherwise it requires a word.  
        //separate these categories.   
        //blank

        //param dictionary.  1 and 2 are for parameters for functions.  Functions can take more than this, but how to demarcate end of parameters?  
        //if there is no demarcation, all midi are passed, and the function decides what to pop.  
        //This seems haphazard, but more convenient for the user.  

        //3 and 4 are for core functions themselves.  
        //5 and more are for user defined variables and functions which then can take 1-2 parameters.  
        //

        this.keydict[ "" ] = { 
            "3": { 
                "23,22,23": "play",
                "0,0,0": "erase", //erase all uncomplete midi.  not sure if this will work ok.  
                "0,11,0" : "start record", 
                "12,11,12": "stop record", //after this we should either have a name or keyset in the upper octave.  
                //this is essentially creating a commandset with all command log and midi log in time.  
                //definition should be 11 or 13 keys.  
                //for now just associate this with a word.  We can use the word to find the commandset.
                //this will be more familiar for people.  This will trigger save commandset, no this should be manual.  
                //it is 12,10,12 so should be easy to trigger in sequence.  
                "0,10,0": "open", //open a tab or a previously saved commandset.  
                "12,10,12": "save", //save a commandset.  This will be a new commandset or overwrite an existing one if it exists.
                //or maybe prompt if exists.  
                "12,5,12": "channel", //channel selector will be 13 and up to 23
                "12,7,12": "tab", //tab selector will be 13 and up to 23, 2 keys for up to 100 tabs each channel.  Need to store index of the tab in window
                //this will use channeltab variable to select from current channel.  
                "12,9,12": "bookmark", //bookmark selector will be 13 and up to 23, 5 keys or more.  
                //this will be usable in subsequent "tab commands" to open this named tab, this will also save the tab
                "0,7,0": "click",
                "0,6,0": "right click", 
                "0,5,0": "read", 
                "0,4,0": "scroll down",
                "0,3,0": "page down",
                "0,2,0": "stop", 
                "5,17,17": "set octave ",
                "12,15,15": "comment ",
            }, 
            "4": {
                "23,22,22,23": "pause",
                "23,20,22,23": "skip ",
                "23,21,21,23": "highlight ",
                "23,20,21,23": "jump ", //just use skip forward or back.  
                "0,1,1,0": "set speed ", //set speed of playback.  This will be a number from -12 to 12.  0 is normal speed.
                "12,6,6,12": "set volume ", //set volume of playback.  This will be a number from 0 to 12.  0 is mute.
                "0,7,7,0": "where am i", 
                "0,5,5,0": "tabs",
                "0,4,4,0": "scroll up",
                "0,3,3,0": "page up",
                "0,2,2,0": "continue",
                "0,4,7,0": "activate mic", "0,7,4,0": "deactivate mic", 
                "0,3,7,0": "activate piano", "0,7,3,0": "deactivate piano",
                "12,5,7,12": "change language ", //just end with 12,12, "12,7,5,12": "change language end" //need further parameter
                "12,10,11,12": "change user ", //just end with 12,12, "12,11,10,12": "change user end" //need further parameter
                "12,4,5,12": "filter add ", //just end with 12,12, "12,5,4,12": "filter end" //need further parameter
                "12,5,4,12": "filter remove "
            },
            "5": {
                "12,9,10,11,12": "add word ", //need further parameter
                "12,2,3,4,12": "add language ", //need further parameter
                "12,7,9,11,12": "add tag ", //need further parameter or word
                "12,11,9,7,12": "remove tag ", //need further parameter or word

            } 
        };
            //basic functionality all keys should come before the word is complete.  Not sure if the user can handle this consistently 
            //but maybe best to make this a rule, to avoid problems.  Basically if said at the same time, it should work.  
            //keycommand + parameter word = action.  
            //wordcommand + parameter keyset = action.  
            //keycommand + parameter keyset = action.  In this case the keyset should essentially be the upper octave.  
            //general terms are even numbers.  Identifiers are odd.  
        
        this.funcdict["updateState"] = function(transcript, midi, keydict, key){
            mytranscript = $('#mycomments').val();
            mystate = "";
            mystate += currentlanguage + ": " + midiarray[currentmidiuser][currentlanguage].length + "<br>";
            mystate += "meta: " + midiarray[currentmidiuser]["meta"].length + "<br>";
            mystate += "last entry: " + transcript + "<br>";
            mystate += "current video time: " + currentvidtime + "<br>";
            if (lastnote !==null){
                mystate += "Last Note: " + lastnote.note + "<br>";
            }
            $('#currentstate').html(mystate);                                                
        }

        this.funcdict[""] = function(transcript, midi, keydict, key){
            for (let i=MAX_COMMANDLENGTH; i>0; i--){
                if (midi != null && midi.length >=i){
                    let keyset = keydict[""][i.toString()];
                    let keys = "";
                    for (let j=0; j<i; j++){
                        keys += (midi[j].note - keybot["meta"]).toString();
//                        keys += midi[j].note.toString();
                        if (j<i-1){
                            keys += ",";
                        }
                    }
                    if (typeof(keyset) !=="undefined" && typeof(keyset[keys]) !=="undefined" && keyset[keys] != null){
                        //run this function.  
                        transcript = keyset[keys] + transcript;
                        for (j=0; j<i; j++){
                            midi[j].complete = true;
                        }
                        return transcript;
                    }
                }
            }
            return transcript;
        };


        this.keydict["highlight "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C

        this.funcdict["highlight "] = function(transcript, midi, keydict, key){
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let skip = 0;
            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "4"){
                    //BBOX
                    if (midi[0].note > midi[1].note){
                        x = midi[0].note - keybot["meta"] - OCTAVE;
                        y = midi[1].note - keybot["meta"];
                    }
                    else{
                        y = midi[0].note - keybot["meta"];
                        x = midi[1].note - keybot["meta"] - OCTAVE;
                    }

                    if (midi[2].note > midi[3].note){
                        x1 = midi[2].note - keybot["meta"] - OCTAVE;
                        y1 = midi[3].note - keybot["meta"];
                    }
                    else{
                        y1 = midi[2].note - keybot["meta"];
                        x1 = midi[3].note - keybot["meta"] - OCTAVE;
                    }

                    if (y > -1 && y < OCTAVE && x > -1 && x < OCTAVE && y1 > -1 && y1 < OCTAVE && x1 > -1 && x1 < OCTAVE){
                        y = OCTAVE - 1 - y; //reverse
                        y1 = OCTAVE - 1 - y1; //reverse
                        if (y1 < y){
                            temp = y1;
                            y1 = y;
                            y = temp;
                        }
                        if (x1 < x){
                            temp = x1;
                            x1 = x;
                            x = temp;                    
                        }

                        transcript = "highlight " + x.toString() + " " + y.toString() + " " + x1.toString() + " " + y1.toString();
                        midi[0].complete = true;
                        midi[1].complete = true;
                        midi[2].complete = true;
                        midi[3].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR highlight - incorrect parameters"
                    }
                }
                else if (commandlength == "2"){
                    if (midi[0].note > midi[1].note){
                        x = midi[0].note - keybot["meta"] - OCTAVE;
                        y = midi[1].note - keybot["meta"];
                    }
                    else{
                        y = midi[0].note - keybot["meta"];
                        x = midi[1].note - keybot["meta"] - OCTAVE;
                    }


                    if (y > -1 && y < OCTAVE && x > -1 && x < OCTAVE){
                        y = OCTAVE - 1 - y; //reverse
                        transcript = "move " + x.toString() + " " + y.toString();
                        midi[0].complete = true;
                        midi[1].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR move - incorrect parameters"
                    }
                }
            }
            return transcript; //add language xxxx 2,3,4
        };

        this.keydict["comment "] = {"2": {"min": -12, "max": 12}}; //number of increments.  from middle C

        this.funcdict["comment "] = function(transcript, midi, keydict, key){
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  

            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "2"){
                    if (midi[0].note - keybot["meta"] == EOW && midi[1].note - keybot["meta"] == EOW){
                        midi[0].complete = true;
                        midi[1].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                        return transcript + "*";
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR comment - incorrect parameters"
                    }
                }

            }
            return transcript; //add language xxxx 2,3,4
        };


        this.keydict["skip "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C

        this.funcdict["skip "] = function(transcript, midi, keydict, key){
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let skip = 0;
            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "1"){
                    skip = midi[0].note - keybot["meta"] - OCTAVE;
                    if (skip > -OCTAVE-1 && skip < OCTAVE+1){

                        skip = Math.sign(skip)*Math.pow(2, (Math.abs(skip)));
                        transcript = "skip " + skip.toFixed(2);
                        midi[0].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR skip - incorrect parameters"
                    }
                }

            }
            return transcript; //add language xxxx 2,3,4
        };

        this.keydict["jump "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C

        this.funcdict["jump "] = function(transcript, midi, keydict, key){
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let jump = 0;
            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "1"){
                    jump = midi[0].note - keybot["meta"] - OCTAVE;
                    if (jump > -OCTAVE-1 && jump < OCTAVE+1){
                        
                        transcript = "jump " + jump.toFixed(2);
                        //for now just jump to 
                        midi[0].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR skip - incorrect parameters"
                    }
                }

            }
            return transcript; //add language xxxx 2,3,4
        };

        this.keydict["set octave "] = {"1": {"min": -12, "max": 12}, "2":{"relative": 1, "lang": 2}}; //number of increments.  from middle C

        this.funcdict["set octave "] = function(transcript, midi, keydict, key){
            //if we have up/down.  black keys = meta.  white keys = current.  
            let commandlength = 0;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    if (parseInt(k) > commandlength){
                        //always want to take the longest command.  
                        commandlength = parseInt(k);
                        commanddict = v;
                    }
                };

            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let octave = 0;
            let octave1 = 0;
            if (commandlength > 0){
                //we have a command map at least.  
                if (commandlength == 1){
                    octave = midi[0].note - keybot["meta"] - OCTAVE;
                    //start at middle, only need top octave as parameter.  
                    if (octave > -1 && octave < OCTAVE+1){

                        transcript = "set octave " + octave;
                        midi[0].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR set octave - incorrect parameters"
                    }
                }

                if (commandlength == 2){
                    octave = midi[0].note - keybot["meta"] - OCTAVE;
                    octave1 = midi[1].note - keybot["meta"] - OCTAVE;
                    if (octave > -1 && octave < OCTAVE+1 && octave == octave1){                        
                        transcript = "set octave " + octave + " meta";
                        midi[0].complete = true;
                        midi[1].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else if (octave > -1 && octave < OCTAVE+1){
                        transcript = "set octave " + octave;
                        midi[0].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR set octave - incorrect parameters"
                    }
                }
            }

            return transcript; //add language xxxx 2,3,4
        };
        
        //sequential
        this.keydict["set volume "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C
        //no space means additional word is optional (can be midi).  
        this.funcdict["set volume "] = function(transcript, midi, keydict, key){
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let volume = 1;
            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "1"){
                    volume = midi[0].note - keybot["meta"] - OCTAVE;
                    if (volume > -OCTAVE-1 && volume < OCTAVE+1){
                        volume = (volume + OCTAVE)/(OCTAVE*2);
                        transcript = "set volume " + volume.toFixed(2);
                        midi[0].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR set volume - incorrect parameters"
                    }
                }

            }
            return transcript; //add language xxxx 2,3,4
        };

        this.keydict["set speed "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C
        //no space means additional word is optional (can be midi).  
        this.funcdict["set speed "] = function(transcript, midi, keydict, key){
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let speed = 1;
            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "1"){
                    speed = midi[0].note - keybot["meta"] - OCTAVE;
                    if (speed > -OCTAVE+1 && speed < OCTAVE+1){
                        if (speed < 0){
                            //1/10 increments
                            speed = Math.abs(speed+OCTAVE-1)/(OCTAVE-2);
                        }
                        else{
                            //.25 increments
                            speed = speed/4;
                            speed = 1 + speed;
                        }                 
                        transcript = "set speed " + speed.toFixed(2);
                        midi[0].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else if (speed == -OCTAVE+1){
                        transcript = "play";
                        midi[0].complete = true;
                    }
                    else if (speed == -OCTAVE){
                        transcript = "pause";
                        midi[0].complete = true;
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR set speed - incorrect parameters"
                    }
                }

            }
            return transcript; //add language xxxx 2,3,4
        };

        this.funcdict["filter clear "] = function(transcript, midi, keydict, key){
            //must end with 12,12
            //default is filter on word
            if (midi.length > 2){
                //for now this is ok, but must code for continuous speech.  
                //again here use language
                //filter clear word, filter clear language, filter clear user
                let temptr = " ";
                for (let i=0; i<midi.length-1; i++){
                    if (i>0 && midi[i].note - keybot["meta"] == EOW && midi[i+1].note - keybot["meta"] == EOW){
                        //we have a language
                        //we can add this language to the DB.  
                        //end of word indicator.  

                        let func = " word ";
                        if (i>2 && midi[i-1].note - keybot["meta"] == 10 && midi[i-2].note - keybot["meta"] == 11){
                            //filter user
                            func = " user ";
                        }
                        else if (i>2 && midi[i-1].note - keybot["meta"] == 5 && midi[i-2].note - keybot["meta"] == 7){
                            //filter language
                            func = " language ";
                        }

                        transcript += func;
                        return transcript;
                    }

                }
            }
            return transcript; //filter remove language xxxx
        };

        //no space means additional word is optional (can be midi).  
        this.funcdict["filter add "] = function(transcript, midi, keydict, key){
            //must end with 12,12
            //default is filter on word
            if (midi.length > 2){
                //for now this is ok, but must code for continuous speech.  
                let temptr = " ";
                for (let i=0; i<midi.length-1; i++){
                    //pull from transcript.  Should be able to do with just transcript.  
                    //filter add word xxxx, filter add language xxx, filter add user xxx
                    //not sure if word should be default.  
                    //maybe language should be default.
                    if (i>0 && midi[i].note - keybot["meta"] == EOW && midi[i+1].note - keybot["meta"] == EOW){
                        //we have a language
                        //we can add this language to the DB.  
                        //end of word indicator.  

                        let func = " word ";
                        if (i>2 && midi[i-1].note - keybot["meta"] == 10 && midi[i-2].note - keybot["meta"] == 11){
                            //filter user
                            func = " user ";
                        }
                        else if (i>2 && midi[i-1].note - keybot["meta"] == 5 && midi[i-2].note - keybot["meta"] == 7){
                            //filter language
                            func = " language ";
                        }

                        let end = i;
                        if (func != " word "){
                            end = i-2;
                        }
                        for (let j=0; j<i+2; j++){
                            midi[j].complete = true;
                        }
                        for (j=0; j<end; j++){
                            if (func == " user "){
                                temptr += (midi[j].note - keybot["meta"]).toString();
                            }
                            else{
                                temptr += (midi[j].note).toString();
                            }
                            if (j<end-1){
                                temptr += ",";
                            }
                        }
                        console.log(temptr);
                        transcript += func + temptr;
                        return transcript;
                    }

                }
            }
            return transcript; //filter add language xxxx
        };

        this.funcdict["filter remove "] = function(transcript, midi, keydict, key){
            //must end with 12,12
            //default is filter on word
            if (midi.length > 2){
                //for now this is ok, but must code for continuous speech.  
                let temptr = " ";
                for (let i=0; i<midi.length-1; i++){
                    if (i>0 && midi[i].note - keybot["meta"] == EOW && midi[i+1].note - keybot["meta"] == EOW){
                        //we have a language
                        //we can add this language to the DB.  
                        //end of word indicator.  

                        let func = " word ";
                        if (i>2 && midi[i-1].note - keybot["meta"] == 10 && midi[i-2].note - keybot["meta"] == 11){
                            //filter user
                            func = " user ";
                        }
                        else if (i>2 && midi[i-1].note - keybot["meta"] == 5 && midi[i-2].note - keybot["meta"] == 7){
                            //filter language
                            func = " language ";
                        }

                        let end = i;
                        if (func != " word "){
                            end = i-2;
                        }
                        for (let j=0; j<i+2; j++){
                            midi[j].complete = true;
                        }
                        for (j=0; j<end; j++){
                            if (func == " user "){
                                temptr += (midi[j].note - keybot["meta"]).toString();
                            }
                            else{
                                temptr += (midi[j].note).toString();
                            }
                            if (j<end-1){
                                temptr += ",";
                            }
                        }
                        console.log(temptr);
                        transcript += func + temptr;
                        return transcript;
                    }

                }
            }
            return transcript; //filter remove language xxxx
        };

        //no space means additional word is optional (can be midi).  
        this.funcdict["change language "] = function(transcript, midi, keydict, key){
            //must end with 12,12
            if (midi.length > 2){
                //for now this is ok, but must code for continuous speech.  
                let temptr = "";
                for (let i=0; i<midi.length-1; i++){
                    if (i>0 && midi[i].note - keybot["meta"] == EOW && midi[i+1].note - keybot["meta"] == EOW){
                        //we have a language
                        //we can add this language to the DB.  
                        //end of word indicator.  
                        for (let j=0; j<i+2; j++){
                            midi[j].complete = true;
                        }
                        for (j=0; j<i; j++){
//                            temptr += (midi[j].note).toString();
                            temptr += (midi[j].note - keybot["meta"]).toString();
                            if (j<i-1){
                                temptr += ",";
                            }
                        }
                        console.log(temptr);

                        transcript = transcript.trim() + " " + temptr;
                        return transcript;
                    }

                }
            }
            return transcript; //add language xxxx 2,3,4
        };

        //space means must have additional word in transcript.  
        this.funcdict["add language "] = function(transcript, midi, keydict, key){
            //must end with 12,12
            if (midi.length > 2){
                //for now this is ok, but must code for continuous speech.  
                let temptr = " ";
                for (let i=0; i<midi.length-1; i++){
                    if (i>0 && midi[i].note - keybot["meta"] == EOW && midi[i+1].note - keybot["meta"] == EOW){
                        //we have a language
                        //we can add this language to the DB.  
                        //end of word indicator.  
                        for (let j=0; j<i+2; j++){
                            midi[j].complete = true;
                        }
                        for (j=0; j<i; j++){
                            temptr += (midi[j].note - keybot["meta"]).toString();
//                            temptr += (midi[j].note - keybot["meta"]).toString();
                            if (j<i-1){
                                temptr += ",";
                            }
                        }
                        console.log(temptr);
                        transcript += " " + temptr;
                        return transcript;
                    }

                }
            }
            return transcript; //add language xxxx 2,3,4
        };

        //space means must have additional word in transcript.  
        this.funcdict["add word "] = function(transcript, midi, keydict, key){
            //must end with 12,12
            if (midi.length > 2){
                //for now this is ok, but must code for continuous speech.  So must find the first two 12s.  
                let temptr = " ";
                for (let i=0; i<midi.length-1; i++){
                    if (i>0 && midi[i].note - keybot["meta"] == EOW && midi[i+1].note - keybot["meta"] == EOW){
                        //we have a word
                        //we can add this language to the DB.  
                        //end of word indicator.  
                        for (let j=0; j<i+2; j++){
                            midi[j].complete = true;
                        }
                        for (j=0; j<i; j++){
                            temptr += (midi[j].note).toString();
//                            temptr += (midi[j].note - keybot["meta"]).toString();
                            if (j<i-1){
                                temptr += ",";
                            }
                        }
                        console.log(temptr);
                        transcript += " " + temptr;
                        return transcript;
                    }
                }
            }
            return transcript;
        };

        this.keydict["help"] = {
            "1": {"1": "1"} 
        }; //0 means any number, search for commands with this midi function after 1.  
        //this should also search up keywords which we have generated and correspond to this set of keys.  
        
        //this is essentially the parameters which will be passed.  This needs to be recursive in some way.  Not sure how yet.  
        //but we need to be able to play this at whatever speed we can.  
        //return the transcript and the number of midi keys which were used.  
        this.keydict["move"] = {
            "1": 0, 
            "2": 12 //expected minimum offset from 1
        }; //bottom octave = Y coord, top octave = X coord
        this.funcdict["move "] = function(transcript, midi, keydict, key){
            //input transcript and return final transcript.  
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let x = -1;
            let y = -1;
            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "2"){
                    //this is the only length but other commands will have variable lengths.  
                    //allow for out of order.  
                    if (midi[0].note > midi[1].note){
                        x = midi[0].note - keybot["meta"] - OCTAVE;
                        y = midi[1].note - keybot["meta"];
                    }
                    else{
                        y = midi[0].note - keybot["meta"];
                        x = midi[1].note - keybot["meta"] - OCTAVE;
                    }


                    if (y > -1 && y < OCTAVE && x > -1 && x < OCTAVE){
                        y = OCTAVE - 1 - y; //reverse
                        transcript = "move " + x.toString() + " " + y.toString();
                        midi[0].complete = true;
                        midi[1].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR move - incorrect parameters"
                    }
                }
            }
            //or just pop from midi as we use?  Is this good enough?  
            //if we have an error in any function it will cause problems downstream.  
            //I guess this is ok.  
            return transcript;
        };
        this.keydict["scroll"] = {"1": {"min": -12, "max": -1}, "2": {"min": 1, "max": 12}}; //number of increments.  from middle C
        //need a min/max for parameters.  
        this.funcdict["scroll"] = function(transcript, midi, keydict, key){
            //input transcript and return final transcript.  
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let x = 0;
            let y = 0;
            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "1"){
                    y = midi[0].note - keybot["meta"] - OCTAVE;;
                    if (y > -OCTAVE-1 && y < OCTAVE+1){
                        y = -y; //reverse
                        transcript = "scroll " + y.toString();
                        midi[0].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR scroll - incorrect parameters"
                    }
                }

                if (commandlength == "2"){
                    //this is the only length but other commands will have variable lengths.  
                    //allow for out of order.  
                    //scroll up or down 
                    if (midi[0].note > midi[1].note){
                        x = midi[0].note - keybot["meta"] - OCTAVE - OCTAVE/2;
                        y = midi[1].note - keybot["meta"] - OCTAVE/2;
                    }
                    else{
                        y = midi[0].note - keybot["meta"] - OCTAVE/2;
                        x = midi[1].note - keybot["meta"] - OCTAVE - OCTAVE/2;
                    }


                    if (y > -(OCTAVE/2)-1 && y < (OCTAVE/2)+1 && x > -(OCTAVE/2)-1 && x < (OCTAVE/2)+1){
                        y = -y; //reverse
                        transcript = "scroll " + y.toString() + " " + x.toString();
                        midi[0].complete = true;
                        midi[1].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "ERROR scroll - incorrect parameters"
                    }
                }
            }
            return transcript;
        };

        
        this.keydict["page"] = {"1": {}}; //number of pages to scroll.  from middle C
        this.keydict["search"] = {"8": {}}; 
        this.keydict["channel"] = {"5": {}}; //keywords are sets of 5 or 7 and more
        this.keydict["tabs"] = {};
        this.keydict["tab"] = {"7": {}}; //use the channel with another two keys
        this.keydict["bookmark"] = {"9": {}}; //probably just use the tab which we have defined with another two keys.  
        //then we can go to a bookmark without needing to go to the tab first.  
        this.keydict["commandset"] = {"11": {}, "13": {}}; //probably just use the tab which we have defined with another two keys.  
        //when running a commandset, how do we speed up?  

    }


    findCommand(transcript, midi, lang=""){

        //return transcript
        //if transcript startswith any of these commands or equals anything in the keydict, prioritize this
        //if we can translate the midi return transcript, otherwise return ""
        //right now only using meta commands.  
        //we should add to the right language in the midiarray.  
        //generally this will be currentlanguage, but could be meta or other.  
        //we can have overlapping languages I suspect.  
        //we need this to be this.funcdict[lang][key] = function
        //right now all commands are meta. 
        if (lang == ""){
            lang = this.lang;
        } 
        let found = false;
        if (midi != null){
            for (const [key, value] of Object.entries(keymaps[lang].funcdict)) {
                let prevtranscript = transcript;
                //maybe dont need this.  
                //this return transcript goes forward one command.  
                if (transcript !=""){
                    if (key !="" && ((transcript + " ").startsWith(key))){
                        found = true;
                        let f = value;
                        let r = f(transcript, midi, keymaps[lang].keydict, key);
                        return [r, lang, found];
                    }
                    else if (key == ""){
                        let f = value;
                        let r = f(transcript, midi, keymaps[lang].keydict, key);
                        if (r !="" && r != prevtranscript){
                            found = true;
                            return [r, lang, found];
                        }
                    }
                }
                else{
                    if (key ==""){
                        let f = value;
                        let r = f(transcript, midi, keymaps[lang].keydict, key);
                        if (r !="" && r != prevtranscript){
                            found = true;
                            return [r, lang, found];
                        }
//                        return [ret, lang];
                    }
                }
            }
        }
        else{
            if (transcript in keymaps[lang].keydict){
                found = true;
            } 
            else if (transcript + " " in keymaps[lang].keydict){
                found = true;
                transcript += " ";
            }
        }

        return [transcript, lang, found];
    }

}

class Command {
    constructor(name, help, action, type = "full", mr = null){
        this.name = name;
        this.help = help;
        this.action = action;
        this.type = type; //full/partial/?  
        this.mr = mr; //mrrubato reference
    }
}
