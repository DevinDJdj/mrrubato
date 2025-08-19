//**languages/videocontrol.js 
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


keymaps["videocontrol"].vars = {};
keymaps["videocontrol"].vars["coords"] = "grid";
keymaps["videocontrol"].vars["x1"] = 0;
keymaps["videocontrol"].vars["y1"] = 0;
keymaps["videocontrol"].vars["x2"] = 0;
keymaps["videocontrol"].vars["y2"] = 0;
keymaps["videocontrol"].vars["midi"] = null;



function VCGenerateDic(){
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

keymaps["videocontrol"].mydic = VCGenerateDic(); //generate dictionary for this language.

//document.currentScript.src

keymaps["videocontrol"].funcdict = {};
//this.keydict[ "" ] = {"1": { "4": "error", "6": "ok", "7": "good"} };
//this is loaded from dictionary.  

keymaps["videocontrol"].funcdict["updateState"] = function(transcript, midi, keydict, key){
}

keymaps["videocontrol"].funcdict[""] = function(transcript, midi, keydict, key){
    for (i=MAX_COMMANDLENGTH; i>0; i--){
        if (midi != null && midi.length >=i){
            let keyset = keydict[""][i.toString()];
            let keys = "";

            if (typeof(keyset) !=="undefined"){
                for (j=0; j<i; j++){
                    keys += (midi[j].note - keybot["videocontrol"]).toString();
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
                    if (keymaps["videocontrol"].currentprefix != ""){
                        transcript = keymaps["videocontrol"].currentprefix + " " + transcript;
                    }
                    return transcript;
                }
            }
        }
    }
    return transcript;
};


//not sure if we want to do this here or from word definitions.  Maybe easier to just specify here.  
keymaps["videocontrol"].keydict[""] ["3"] = {
    "0,3,6": "screenshot", //take screenshot quick location only 
    "0,3,7": "zoomshot", //take screenshot zoomed in
    "0,3,8": "zoom", //zoom in or out    
    "0,3,5": "deletescreen", //remove last screenshot
    "0,3,4": "deletescreen", //remove last screenshot
    "0,2,6": "speak", //add the last transcript entry to
    "0,2,5": "delete", //remove last transcript entry    
    "0,12,0": "start", //start recording
    "12,0,12": "stop", //stop recording
    "1,13,1": "pause", //pause recording
    "13,1,13": "unpause", //unpause recording
    "1,2,3": "help" //show/hide commands.  
};

keymaps["videocontrol"].keydict[""] ["2"] = {
    "12,14": "jump", //jump N seconds
};

keymaps["videocontrol"].currentprefix = "";


//forward or back
keymaps["videocontrol"].keydict["jump "] = {"1": {"min": -12, "max": 12}}; //number of increments.  from middle C


keymaps["videocontrol"].keydict["screenshot "] = {"4": {"min": 0, "max": 24}}; //number of increments.  from middle C

function VCcheckConstraints(midi, num, min, max){

    for (let i=0; i<num; i++){
        if (midi[i].note < min || midi[i].note > max){
            return false;
        }
    }
    return true;
}

function VCgetBBOX(midi, keybot){
    let x1,x2 = 0;
    let y1,y2 = 0;
    if (midi[0].note > midi[1].note){
        x1 = midi[0].note - keybot;
        x2 = midi[1].note - keybot;
    }
    else{
        x2 = midi[0].note - keybot;
        x1 = midi[1].note - keybot;
    }
    if (midi[2].note > midi[3].note){
        y1 = midi[2].note - keybot;
        y2 = midi[3].note - keybot;
    }
    else{
        y2 = midi[2].note - keybot;
        y1 = midi[3].note - keybot;
    }
    return [x1, x2, y1, y2];
}

keymaps["videocontrol"].funcdict["screenshot "] = function(transcript, midi, keydict, key){

    //take screenshot
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
    let kb = keybot["videocontrol"];
    if (commandlength !== null){
        //we have a command map at least.  
        if (commandlength == "4"){
            if (VCcheckConstraints(midi, 4, commanddict["min"], commanddict["max"])){
                [x1,x2,y1,y2] = VCgetBBOX(midi, kb);
            }
            else{
                return "ERROR screenshot - incorrect parameters";
            }
            transcript = "screenshot " + x1.toFixed(2) + "," + x2.toFixed(2) + "," + y1.toFixed(2) + "," + y2.toFixed(2);
        }

    }
    return transcript; //add language xxxx 2,3,4
}        

keymaps["videocontrol"].funcdict["jump "] = function(transcript, midi, keydict, key){
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
            skip = midi[0].note - keybot["videocontrol"] - OCTAVE;
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


keymaps["videocontrol"].funcdict["_screenshot"] = function(){

}


keymaps["videocontrol"].funcdict["_help"] = function(){
    showHelp();
}


keymaps["videocontrol"].chat = function (transcript){
    let executed = false;
    transcript = transcript.trim();
    //find and handle command.  
    if (transcript.toLowerCase().startsWith("help")){
        keymaps["videocontrol"].funcdict["_help"]();
        executed = true;

    }
    else if (transcript.toLowerCase().startsWith("screenshot")){
        tokens = transcript.split(" ");
        if (tokens.length == 2){
            let coords = tokens[1].split(",");
            if (coords.length == 4){
                //parse coordinates
                keymaps["videocontrol"].vars["x1"] = parseInt(coords[0]);
                keymaps["videocontrol"].vars["x2"] = parseInt(coords[1]);
                keymaps["videocontrol"].vars["y1"] = parseInt(coords[2]);
                keymaps["videocontrol"].vars["y2"] = parseInt(coords[3]);
                //use these coords later if needed.  

                //take screenshot
                executed = true;
                //call screenshot function here
            }
        }
    }
    return executed;

}
