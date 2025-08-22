//**languages/audiocontrol.js 
//Already have some of this in "meta"
//but should really organize it better.  
/*
\Screenshot (0,3,6) (XXYY)
\zoom (0,3,8) (XXYY) #default x2
\deletescreen (0,3,5) #remove last screenshot

\speak (0,2,6) (XY) #add the last transcript entry to the screen here.  
\delete (0,2,5) #remove last transcript entry

\rewind (12,11) (N)
\jump (12,14) (N)

\start rec (0,12,0)
\stop rec (12,0,12)
\pause rec (1,13,1)
\unpause rec (13,1,13)


\help (1,2,3) #show/hide commands.  

*/


keymaps["audiocontrol"].vars = {};
keymaps["audiocontrol"].vars["coords"] = "grid";
keymaps["audiocontrol"].vars["x1"] = 0;
keymaps["audiocontrol"].vars["y1"] = 0;
keymaps["audiocontrol"].vars["x2"] = 0;
keymaps["audiocontrol"].vars["y2"] = 0;
keymaps["audiocontrol"].vars["midi"] = null;



function ACGenerateDic(){
    ret = {};
    let dic = {"screenshot": {"midi": "0,3,6"},
            "zoom": {"midi": "0,3,8"},
        "deletescreen": {"midi": "0,3,5"},
        "speak": {"midi": "0,2,6"},
        "delete": {"midi": "0,2,5"},
        "jump": {"midi": "12,14"},
        "start": {"midi": "0,12,0"},
        "stop": {"midi": "12,0,12"},
        "pause": {"midi": "1,13,1"},
        "unpause": {"midi": "13,1,13"},
        "help": {"midi": "1,2,3"}
    };
    for (const [key, value] of Object.entries(dic)) {
        let val = value;
        val["color"] = 0;
        val["created"] = "20250714";
        val["updated"] = "20250714";
        val["definition"] = "";
        val["img"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAG4AAAAWCAYAAAAhKqlXAAAAAXNSR0IArs4c6QAAAghJREFUaEPtWjFrwkAU/hIQLehikSr4B5yKi+DoXxDMH+hScHBx01E3KTj4JxJw6NSlOAoujnbpJFRBKhSkCIKWO+tp1MREPTXwsgTfnV/uvu/eu3cvUQAsQNdBBnQAua1eBgDt4D/ldFCYcIvFWrtGo4FisYhgMCieOB6PMRwO+e9oNIpwOCzaJpMJarUa8vm8sCkKg+XAwnYKbiaTQbfbhc/n43iz2QzJZBKtVkvga5oGwzCg6zpyuSXFo9HIdrxucPvpNOLttkmFV78fT6EQt23yYIdrx0MkEuFYbB5sPmwebD7bF+OXhHO4IEi4IzzZjWfI8rjf53vcPXybFv/Xh4rH92X0IY/7p8YpESsmZYdKEs6jHtd/SSP+s7XHffrx9EZ7nGXScwuhkoQjj7PM2imrlHAcOFfSQ8eBC5/jSDiPhkoSjoSjPe6SJS/PeJyqqqJKMJ1OTbXKQCAg2ubzuata5TG47DjQ6XRMVYtUKuW4Vmk13mvgrpKTfTycnFUOBgM0m030ej1ks1kkEgkUCgVOXL1e53bWzuysPRaLOSoyH4tbLpf5s6vVKr+XSiV+r1QqB4vMduO9Bi4TzoqHk4SzKyGt2pxUr1nfzbcDhGuu8e8r0bnhd+ftABF8XoJlLWASDsC+94e3voBJOBJuHWK8uIJlhTRZuORxXva4nY8ayHDzDPwBrQy/agLUfQUAAAAASUVORK5CYII=";
        ret[key] = val;
    }
    return ret;
}

keymaps["audiocontrol"].mydic = ACGenerateDic(); //generate dictionary for this language.

//document.currentScript.src

keymaps["audiocontrol"].funcdict = {};
//this.keydict[ "" ] = {"1": { "4": "error", "6": "ok", "7": "good"} };
//this is loaded from dictionary.  

keymaps["audiocontrol"].funcdict["updateState"] = function(transcript, midi, keydict, key){
}

keymaps["audiocontrol"].funcdict[""] = function(transcript, midi, keydict, key){
    for (i=MAX_COMMANDLENGTH; i>0; i--){
        if (midi != null && midi.length >=i){
            let keyset = keydict[""][i.toString()];
            let keys = "";

            if (typeof(keyset) !=="undefined"){
                for (j=0; j<i; j++){
                    keys += (midi[j].note - keybot["audiocontrol"]).toString();
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
                    if (keymaps["audiocontrol"].currentprefix != ""){
                        transcript = keymaps["audiocontrol"].currentprefix + " " + transcript;
                    }
                    return transcript;
                }
            }
        }
    }
    return transcript;
};


//not sure if we want to do this here or from word definitions.  Maybe easier to just specify here.  
keymaps["audiocontrol"].keydict[""] ["3"] = {
//    "0,3,6": "screenshot", //take screenshot
//    "0,3,8": "zoom", //zoom in
//    "0,3,5": "stop", //remove last screenshot
//    "0,2,6": "speak", //add the last transcript entry to
//    "0,2,5": "delete", //remove last transcript entry    
    "0,12,0": "start", //start recording
    "12,0,12": "stop", //stop recording
    "1,13,1": "pause", //pause recording
    "13,1,13": "unpause", //unpause recording
    "1,2,3": "help" //show/hide commands.  
};

keymaps["audiocontrol"].keydict[""] ["2"] = {
    "12,14": "jump", //jump N seconds
};

keymaps["audiocontrol"].currentprefix = "";


//forward or back
keymaps["audiocontrol"].keydict["jump "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C



function ACcheckConstraints(midi, num, min, max){

    for (let i=0; i<num; i++){
        if (midi[i].note < min || midi[i].note > max){
            return false;
        }
    }
    return true;
}

keymaps["audiocontrol"].funcdict["jump "] = function(transcript, midi, keydict, key){
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
            skip = midi[0].note - keybot["audiocontrol"] - OCTAVE;
            if (skip > -OCTAVE-1 && skip < OCTAVE+1){

                skip = Math.sign(skip)*Math.pow(3, (Math.abs(skip)));
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



keymaps["audiocontrol"].funcdict["_help"] = function(){
    showHelp();
}


keymaps["audiocontrol"].chat = function (transcript){
    let executed = false;
    transcript = transcript.trim();
    //find and handle command.  
    if (transcript.toLowerCase().startsWith("help")){
        keymaps["audiocontrol"].funcdict["_help"]();
        executed = true;

    }
    else if (transcript.toLowerCase() == "start"){
        //start audio recording.  
        //for now use selected audio.  This can also be robot voice.


    }
    else if (transcript.toLowerCase() == "stop"){
        //stop audio recording. 
        window.speechSynthesis.cancel(); //stop any current speech.
        stopllm = true;
        executed = true;
    }
    else if (transcript.toLowerCase() == "pause"){
        //pause audio recording.  
    }
    else if (transcript.toLowerCase() == "unpause"){
        //unpause or start audio recording.  
    }

    return executed;

}
