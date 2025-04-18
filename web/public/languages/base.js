
keymaps["base"].funcdict = {};
//this.keydict[ "" ] = {"1": { "4": "error", "6": "ok", "7": "good"} };
//this is loaded from dictionary.  

keymaps["base"].funcdict["updateState"] = function(transcript, midi, keydict, key){
}

keymaps["base"].funcdict[""] = function(transcript, midi, keydict, key){
    for (i=MAX_COMMANDLENGTH; i>0; i--){
        if (midi != null && midi.length >=i){
            let keyset = keydict[""][i.toString()];
            let keys = "";

            if (typeof(keyset) !=="undefined"){
                for (j=0; j<i; j++){
                    keys += (midi[j].note - keybot["base"]).toString();
    //                        keys += midi[j].note.toString();
                    if (j<i-1){
                        keys += ",";
                    }
                }
                if (typeof(keyset[keys]) !=="undefined" && keyset[keys] != null){
                    //run this function.  
                    transcript += keyset[keys];
                    for (j=0; j<i; j++){
                        midi[j].complete = true;
                    }

                    //add prefix here if needed.  
                    if (keymaps["base"].currentprefix != ""){
                        transcript = keymaps["base"].currentprefix + " " + transcript;
                    }
                    return transcript;
                }
            }
        }
    }
    return transcript;
};


//not sure if we want to do this here or from word definitions.  Maybe easier to just specify here.  
keymaps["base"].keydict[""] ["3"] = {
    "12,13,13": "content",
    "12,14,14": "transcription"
};

keymaps["base"].currentprefix = "";

keymaps["base"].funcdict["content"] = function(transcript, midi, keydict, key){
    keymaps["base"].currentprefix = "content";
};

keymaps["base"].funcdict["transcription"] = function(transcript, midi, keydict, key){  
  keymaps["base"].currentprefix = "transcription";
}


keymaps["base"].keydict[ "" ] ["4"] = {"24,21,23,24": "skip " };

keymaps["base"].keydict["skip "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C

keymaps["base"].funcdict["skip "] = function(transcript, midi, keydict, key){
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
            skip = midi[0].note - keybot["base"] - OCTAVE;
            if (skip > -OCTAVE-1 && skip < OCTAVE+1){

                skip = Math.sign(skip)*Math.pow(3, (Math.abs(skip)));
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
