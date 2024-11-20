
keymaps["tennis"].funcdict = {};

keymaps["tennis"].funcdict["updateState"] = function(transcript, midi, keydict, key){

}

keymaps["tennis"].funcdict[""] = function(transcript, midi, keydict, key){
    for (i=MAX_COMMANDLENGTH; i>0; i--){
        if (midi != null && midi.length >=i){
            let keyset = keydict[""][i.toString()];
            let keys = "";
            for (j=0; j<i; j++){
                keys += (midi[j].note - keybot["tennis"]).toString();
//                        keys += midi[j].note.toString();
                if (j<i-1){
                    keys += ",";
                }
            }
            if (typeof(keyset) !=="undefined" && typeof(keyset[keys]) !=="undefined" && keyset[keys] != null){
                //run this function.  
                transcript += keyset[keys];
                for (j=0; j<i; j++){
                    midi[j].complete = true;
                }
                return transcript;
            }
        }
    }
    return transcript;
};

keymaps["tennis"].keydict[ "" ] = { 
    "4": {
        "24,21,23,24": "skip "
    }
};

keymaps["tennis"].keydict["skip "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C

keymaps["tennis"].funcdict["skip "] = function(transcript, midi, keydict, key){
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
            skip = midi[0].note - keybot["tennis"] - OCTAVE;
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
