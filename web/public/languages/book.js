keymaps["book"].vars = {};
keymaps["book"].vars["lineorpct"] = "line";
keymaps["book"].vars["midi"] = null;


keymaps["book"].funcdict = {};


keymaps["book"].funcdict["updateState"] = function(transcript, midi, keydict, key){
    //check transcript for commands.  
}

keymaps["book"].funcdict[""] = function(transcript, midi, keydict, key){
    for (i=MAX_COMMANDLENGTH; i>0; i--){
        if (midi != null && midi.length >=i){
            let keyset = keydict[""][i.toString()];
            let keys = "";
            for (j=0; j<i; j++){
                keys += (midi[j].note - keybot["doodle"]).toString();
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

keymaps["book"].keydict[ "" ] = {
    "2": {
        "3,6": "jump ", //draw from current x,y to x,y
        "8,10": "zoom ", //draw from current x,y to x,y
        "14,16": "set type ", //change to polar or grid coords
        "17,19": "line", 
        "19,21": "pct"
    },
    "4": {
        "24,21,23,24": "skip "
    }
};

keymaps["book"].funcdict["_jump"] = function(midi){
    //UI function start with _?  
    //vars should be set prior to this in "line".  
    //data validation should occur in "line " function.
    //perform UI action on 
    var editor = myCodeMirror;
    editor.scrollTo(gitcurrentscrollinfo.left, gitcurrentscrollinfo.top+midi);
    

}


keymaps["book"].keydict["jump "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C

keymaps["book"].funcdict["jump "] = function(transcript, midi, keydict, key){
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
            skip = midi[0].note - keybot["book"] - OCTAVE;
            if (skip > -OCTAVE-1 && skip < OCTAVE+1){

                skip = Math.sign(skip)*Math.pow(2, (Math.abs(skip)));
                transcript = "jump " + skip.toFixed(2);
                midi[0].complete = true;
                //I think this will work ok.  
                //this allows us to move on to next command.  
            }
            else{
                //not sure how I want to handle errors yet.  
                return "ERROR jump - incorrect parameters"
            }
        }

    }
    return transcript; //add language xxxx 2,3,4
};


keymaps["book"].keydict["zoom "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C

keymaps["book"].funcdict["zoom "] = function(transcript, midi, keydict, key){
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
            skip = midi[0].note - keybot["book"] - OCTAVE;
            if (skip > -OCTAVE-1 && skip < OCTAVE+1){

                skip = Math.sign(skip)*Math.pow(2, (Math.abs(skip)));
                transcript = "zoom " + skip.toFixed(2);
                midi[0].complete = true;
                //I think this will work ok.  
                //this allows us to move on to next command.  
            }
            else{
                //not sure how I want to handle errors yet.  
                return "ERROR zoom - incorrect parameters"
            }
        }

    }
    return transcript; //add language xxxx 2,3,4
};


keymaps["book"].chat = function (transcript){
    let executed = false;
    transcript = transcript.trim();
    //find and handle command.  
    if (transcript.toLowerCase().startsWith("jump")){
        tokens = transcript.split(" ");
        if (tokens.length > 1){
            midi = tokens[tokens.length-1];
            if (hasNumber(midi)){ //check if we have actually put in the midi.
                //this should be a good function.  
                console.log("book jump line " + midi);
                //check for same or change here.  
                keymaps["book"].funcdict["_jump"](midi);
                executed = true;
            }
        }
        else{
            executed = false;
        }

    }
    return executed;

}

