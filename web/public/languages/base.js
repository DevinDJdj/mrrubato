
keymaps["base"].funcdict = {};
this.keydict[ "" ] = {"1": { "4": "error", "6": "ok", "7": "good"} };


keymaps["base"].funcdict["updateState"] = function(transcript, midi, keydict, key){
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
                    return transcript;
                }
            }
        }
    }
    return transcript;
};

this.keydict[ "" ] = { 
    "4": {
        "24,21,23,24": "skip "
    }
};

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
