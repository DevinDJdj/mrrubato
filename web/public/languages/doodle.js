keymaps["doodle"].vars = {};
keymaps["doodle"].vars["coords"] = "polar";
keymaps["doodle"].vars["x"] = 0;
keymaps["doodle"].vars["y"] = 0;
keymaps["doodle"].vars["x_"] = 0;
keymaps["doodle"].vars["y_"] = 0;
keymaps["doodle"].vars["midi"] = null;


keymaps["doodle"].funcdict = {};


keymaps["doodle"].funcdict["updateState"] = function(transcript, midi, keydict, key){
    //check transcript for commands.  
}

keymaps["doodle"].funcdict[""] = function(transcript, midi, keydict, key){
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

keymaps["doodle"].keydict[ "" ] = {
    "2": {
        "3,6": "line ", //draw from current x,y to x,y
        "8,10": "box ", //draw from current x,y to x,y
        "14,16": "set coordinates ", //change to polar or grid coords
        "17,19": "polar", 
        "19,21": "grid"
    },
    "4": {
        "24,21,23,24": "skip "
    }
};

keymaps["doodle"].keydict["skip "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C

keymaps["doodle"].funcdict["skip "] = function(transcript, midi, keydict, key){
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
            skip = midi[0].note - keybot["doodle"] - OCTAVE;
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


//how should this naming work?  
keymaps["doodle"].funcdict["_line"] = function(){
    //UI function start with _?  
    //vars should be set prior to this in "line".  
    //data validation should occur in "line " function.
    var midi = keymaps["doodle"].vars["midi"];

    let x_ = keymaps["doodle"].vars["x_"];
    let y_ = keymaps["doodle"].vars["y_"];
    let x = keymaps["doodle"].vars["x"];
    let y = keymaps["doodle"].vars["y"];

    let polygon = {"type": "line", "points": [ [0,0], [x-x_,y-y_] ]}
    addOverlay(x_, y_, polygon);

    keymaps["doodle"].vars["x_"] = x;
    keymaps["doodle"].vars["y_"] = y;

}


keymaps["doodle"].chat = function (transcript){
    let executed = false;
    transcript = transcript.trim();
    //find and handle command.  
    if (transcript.toLowerCase().startsWith("line")){
        tokens = transcript.split(" ");
        if (tokens.length > 1){
            midi = tokens[tokens.length-1];
            if (hasNumber(midi)){ //check if we have actually put in the midi.
                //this should be a good function.  
                console.log("doodle chat line " + midi);
                //check for same or change here.  
                keymaps["doodle"].funcdict["_line"]();
                executed = true;
            }
        }
        else{
            executed = false;
        }

    }
    return executed;

}


keymaps["doodle"].keydict["line "] = {
    "2": 12, //expected minimum offset from 1
}; //bottom octave = Y coord, top octave = X coord

keymaps["doodle"].funcdict["line "] = function(transcript, midi, keydict, key){
    //perhaps need to use midi velocity parameters here to create style etc.  
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
    let x = -1;
    let y = -1;
    if (commandlength !== null){
        //we have a command map at least.  
        if (commandlength == "2"){
            //this is the only length but other commands will have variable lengths.  
            //allow for out of order.  
            if (midi[0].note > midi[1].note){
                x = midi[0].note - keybot["doodle"] - OCTAVE;
                y = midi[1].note - keybot["doodle"];
            }
            else{
                y = midi[0].note - keybot["doodle"];
                x = midi[1].note - keybot["doodle"] - OCTAVE;
            }


            if (y > -1 && y < OCTAVE && x > -1 && x < OCTAVE){
                y = OCTAVE - 1 - y; //reverse
                keymaps["doodle"].vars["x"] = x;
                keymaps["doodle"].vars["y"] = y;
                keymaps["doodle"].vars["midi"]  = midi;

                transcript = "line " + x.toString() + "," + y.toString();
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
        else if (commandlength == "4"){
            //this is the only length but other commands will have variable lengths.  
            //allow for out of order.  
            if (midi[0].note > midi[1].note){
                x = midi[0].note - keybot["doodle"] - OCTAVE;
                y = midi[1].note - keybot["doodle"];
            }
            else{
                y = midi[0].note - keybot["doodle"];
                x = midi[1].note - keybot["doodle"] - OCTAVE;
            }

            if (midi[2].note > midi[3].note){
                x = midi[2].note - keybot["doodle"] - OCTAVE;
                y = midi[3].note - keybot["doodle"];
            }
            else{
                y = midi[2].note - keybot["doodle"];
                x = midi[3].note - keybot["doodle"] - OCTAVE;
            }


            if (y > -1 && y < OCTAVE && x > -1 && x < OCTAVE){
                y = OCTAVE - 1 - y; //reverse
                transcript = "move " + x.toString() + " " + y.toString();
                midi[0].complete = true;
                midi[1].complete = true;
                midi[2].complete = true;
                midi[3].complete = true;
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

