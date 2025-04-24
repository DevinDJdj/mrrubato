
let commandLog = [];
let pendingCommands = [];
let ss = null;
//myrate = 0.7;
//mypitch = 1;


let lastcommand = "";
let lastcommandtime = 0;
let currentvoice = 0;
let voices = null;
let commentpos = 0;

let recentTime = 4000;

//probably should keep this command log.  
//But it is basically being kept in transcript.  
export function deletePendingCommand(){
    //delete the last pending command.  
    if (commandLog.length > 0 && commandLog[commandLog.length-1].pending){
        commandLog.pop();
        transcript = "";
    }
}

export function getPendingCommand(pedal=true){ //dont remove by default
    if (commandLog.length > 0 && commandLog[commandLog.length-1].pending){
        if (Date.now() - commandLog[commandLog.length-1].time > recentTime*2 && !pedal){ //recentTime in midi.js
            //allow for double the time to complete the command.  
            //pop from the pending commands?  Why keep useless history?  
            commandLog.pop();
            transcript = "";
            return null;
        }

        return commandLog[commandLog.length-1];
    }   
    else{
        return null;
    }
}

export function addCommandLog(transcript, command, pending=false, lang="base"){
    //we want to have the time here.  
    let now = Date.now();
    transcript = transcript.trimStart();
    let intranscript = transcript;
    transcript = "";
    //get previous pending commands if they exist.  //only within 8 seconds.  Otherwise they are popped.  
    for (let i=commandLog.length -1; i>-1; i--){
        if (commandLog[i].pending){
            if (commandLog[i].transcript == transcript){
                //dont keep adding the same commands
                return;
            }
            else{
                transcript = commandLog[i].transcript.trim();
                commandLog[i].pending = false;
            }
        }
    }
    transcript += " " + intranscript;
    commandLog.push({time: now, transcript: transcript, command: command, pending: pending, lang: lang});
    //command here is the callback.  Not using at the moment.  
}





//called from clock.js every second.  
//open-ended definitions must end with midi 60, 60.  
//add language, add word etc.  But 60, 60 not stored in keymap.  
//others will be defined in keymap.  
/*
export function checkCommands(lang="meta"){
    let cl = getPendingCommand();
    let midi = getMidiRecent();
    let executed = false;
    //if most recent is too recent wait some more.  
    //otherwise we assume this is a completed command.  
    //also if we have punctuation/end command, we can continue.  
    if (midi != null){
        //clear out any midi or pending commands with 0,0,0
        //why ispaused here?  
        if (midi.length > 2 && midi[midi.length-1].note -keybot["meta"] == 0 && midi[midi.length-2].note -keybot["meta"] == 0 && midi[midi.length-3].note -keybot["meta"] == 0){
            for (let i=0; i<midi.length; i++){
                midi[i].complete = true;
            }
            commandLog.pop();
            cl = null;
            completeMidi(midi, "meta");
            return "";
        }

        completeMidi(midi);
    }
    let transcript = "";
    let pending = false;
    let callback = null;
    if (cl != null){
                //we have a command.  
            //try to find if we have something to do with the midi.  
            //recurse to find the transcript needed.  
            //we will find scroll, then we need those parameters.  
        console.log(cl);
        transcript = cl.transcript;
        let prevtranscript = "";
        pending = cl.pending;
        let done = 1;
        let found = false;  //can we find this command.  If we find are writing a command, dont use in mychat.  
        while (done > 0 && midi !=null && midi.length > 0 && executed==false){
            transcript = transcript.trimStart();
            prevtranscript = transcript;
            //find words in current language.  

            [transcript, lang, found] = findCommand(transcript, midi, prevtranscript, lang);
            if (transcript != prevtranscript){

                done = completeMidi(midi, lang);
                //refresh midi with only incomplete commands.  
                if (transcript.endsWith(" ")){  //use space as indicator of more parameters needed.
                    //still waiting.  
                    cl.transcript = transcript;
                    //we have added to the pending command.  
                    //can continue the command with more midi
                    //no use case at the moment for this.  
                }
                else{
                    //attempt to execute complete command.  
                    executed = Chat(transcript, callback, pending); //add waspendingflag

                    transcript = "";
                }
            }
            else{
                if (transcript != cl.transcript){
                    cl.transcript = transcript;
                    cl.time = Date.now();
                }
                done = 0;
            }
        }
        
        //when does this occur? when we dont have midi.  
        if ((midi ==null || midi.length == 0) && transcript != "" && !found){ //are we waiting for more command?  
            executed = Chat(transcript, callback, pending); //add waspendingflag
//            transcript = "";

        }

        //get rid of executed commands.  
        if (executed){
            commandLog.pop();
            transcript = "";
        }

        //get rid of incomplete commands.  
        if (Date.now() - cl.time > recentTime*2){ //recentTime in midi.js
            //allow for double the time to complete the command.  
            //pop from the pending commands?  Why keep useless history?  
            commandLog.pop();
            transcript = "";
        }

    }
    else{
        if ((midi != null && midi.length > 0)){
            console.log(midi);


            let prevtranscript = "";
            //get command.  
            let done = 1;
            while (done > 0 && midi.length > 0 && executed==false){
                prevtranscript = transcript;
                //get parameters.  
                [transcript, lang, found] = findCommand(transcript, midi, prevtranscript, lang);
                //have to set .complete to true.  
                //we add space to this
                if (transcript != prevtranscript){
                    done = completeMidi(midi, lang);
                    if (transcript.endsWith(" ")){  //use space as indicator of more parameters needed.
                        //still waiting.  in this case perhaps extend the pendingTime.  
                    }
                    else{
                        executed = Chat(transcript, callback, pending); //add waspendingflag
                        transcript = "";
                    }
                }
                else {
                    //we have 4 seconds to add the parameters for this call if .  
                    //still pending.  Just add pending command.  
                    //or ignore.  
                    done = 0;
                }
            }

            if (transcript !=""){
                if (transcript.endsWith(" ")){ //add pending command.  
                    addCommandLog(transcript, null, true);
                    //single command.  Must have at least half a second open here or whatever the timer is open time in order to execute this command.  
                    //add a pending command, and if no more midi comes within half a second, we execute.  
                    //will need to adjust this timer for the user.  
                }
                else{
                    //should never end up here.  
                    executed = Chat(transcript, callback, pending); 
                    transcript = "";
                }
            }

        }
    }
    
    return transcript;

}
*/
/*
function completeMidi(midi, lang=""){
    let ret = 0;
    let reftime = getReferenceTime();
    while (midi.length > 0 && (midi[0].time < reftime-recentTime || midi[0].complete == true)){
        //complete midi commands that are too old.  
        
        midi[0].complete = true;
        //why did we have this here?  
        if (lang != currentlanguage){
            insertNote(midi[0], lang);
            removeNote(midi[0], currentlanguage);
        }
        midi.shift();
        ret++;
    }
    return ret;
}
*/


//dependent on video.js
//need to untangle.  
export function helpme(){
    var temptime = 0;
    if (useyoutube || watch){
        if (!player.getCurrentTime)
            return "00:00";
        var temptime = player.getCurrentTime();
    }
    else{
        temptime = player2.currentTime;
    }
    temptime -= delay;

    var mins = Math.floor(temptime/60);
    if (mins < 0) mins = 0;
	var secs = Math.floor(temptime - mins*60);
    if (secs < 0) secs = 0;
    var finalTime = str_pad_left(mins,'0',2)+':'+str_pad_left(secs,'0',2);
	
	return finalTime;

}

function hasNumber(myString) {
    return /\d/.test(myString);
}

//right now there is no chatting here, we are just using the comments.
export function Chat(transcript, callback=null, pending=false, lang=""){
    //check meta commands first, then keymap[lang].chat...

    let tokens = "";
    let midi = "";
    if (lang==""){
        lang = currentlanguage;
    }
    //should we pass language here?  
    let executed = true;
    //this causes problems with the commands.  Dont think we need this anyway
    /*
    if (lastcommand !=transcript || Date.now() - lastcommandtime > recentTime){
        lastcommand = transcript;
        lastcommandtime = Date.now();
    }
    else{
        //dont repeat for at least 5 seconds.  
        return;
    }
    */

    //trim the start of the transcript.  
    transcript = transcript.trim();
    //find and handle command.  
    if (transcript.toLowerCase().startsWith("help")){

    }
    else if (transcript.toLowerCase().startsWith("highlight")){
        //skip to next event?  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 4){
            let x = parseFloat(tokens[1]);
            let y = parseFloat(tokens[2]);
            let x1 = parseFloat(tokens[3]);
            let y1 = parseFloat(tokens[4]);
            highlightVideo(x, y, x1, y1);

        }
        else if (tokens.length > 2){
            let x = parseFloat(tokens[1]);
            let y = parseFloat(tokens[2]);
            highlightVideo(x, y);
        }
        else{
            executed=false;
        }
    }

    else if (transcript.toLowerCase().startsWith("comment")){
        //make this comment to next event?  
        transcript = transcript.substr(transcript.indexOf(" ") + 1);
        transcript = "--" + transcript; //add -- to the start of the comment.
    }
    else if (transcript.toLowerCase().startsWith("skip")){
        //skip to next event?  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 1 && tokens[1] !=""){
            let skip = parseFloat(tokens[1]);
            skipVideo(skip);
        }
        else{
            executed=false;
        }
    }
    else if (transcript.toLowerCase().startsWith("jump")){
        //skip to next event?  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 1 && tokens[1] !=""){
            let jump = parseFloat(tokens[1]);
            jumpVideo(jump);
        }
        else{
            executed=false;
        }
    }
    else if (transcript.toLowerCase() == "back"){
        //skip to previous event?
    }
    else if (transcript.toLowerCase() == "stop"){
        window.speechSynthesis.cancel();
    }
    else if (transcript.toLowerCase() == "play"){
        //play video
        playVideo();
    }
    else if (transcript.toLowerCase() == "pause"){
        //pause video
        pauseVideo();
    }
    else if (transcript.toLowerCase().startsWith("set octave")){
        //adjust playback speed of video.  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 2 && tokens[2] !=""){
            if (tokens.length > 3 && tokens[3] !=""){
                let octave = parseInt(tokens[2]);
                lang = tokens[3];
                setOctave(octave, lang);

            }
            else{
                let octave = parseInt(tokens[2]);
                setOctave(octave);
            }


        }
        else{
            executed = false;
        }
    }
    else if (transcript.toLowerCase().startsWith("set speed")){
        //adjust playback speed of video.  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 2 && tokens[2] !=""){
            let speed = parseFloat(tokens[2]);
            setVideoSpeed(speed);
        }
        else{
            executed = false;
        }
    }
    else if (transcript.toLowerCase().startsWith("set volume")){
        //adjust playback speed of video.  
        tokens = transcript.split(" ");
        //logic check is in prior function
        if (tokens.length > 2 && tokens[2] !=""){
            let volume = parseFloat(tokens[2]);
            if (volume == 0.5){
                //mute piano sounds
                playfeedback = false;
            }
            else if (volume == 1){
                //unmute piano sounds
                playfeedback = true;
            }
            else{
                //maybe want a different function for this, but for now its ok I guess.  
                setFeedbackVolume(volume);
            }
            setVideoVolume(volume);
        }
        else{
            executed = false;
        }
    }
    //filter clear, filter add, filter remove
    else if (transcript.toLowerCase().startsWith("filter clear")){
        tokens = transcript.split(" ");
        if (tokens.length > 2){
            let func = tokens[2];
            if (func == "word"){
                //clear filter by word                
            }
            else if (func == "language"){
                //clear filter by language

            }
            else if (func == "user"){
                //clear filter by user, probably need to be able to name users.  
            }
        }
        else{
            executed = false;
        }        
    }

    else if (transcript.toLowerCase().startsWith("filter add")){
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            let func = tokens[2];
            let filter = "";
            if (func == "word"){
                //filter by word
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            else if (func == "language"){
                //filter by language
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            else if (func == "user"){
                //filter by user, probably need to be able to name users.  
                filter = tokens.slice(3, tokens.length).join(" ");
            }
        }
        else{
            executed = false;
        }
    }
    else if (transcript.toLowerCase().startsWith("filter remove")){
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            let func = tokens[2];
            let filter = "";
            if (func == "word"){
                //filter by word
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            else if (func == "language"){
                //filter by language
                filter = tokens.slice(3, tokens.length).join(" ");
            }
            else if (func == "user"){
                //filter by user, probably need to be able to name users.  
                filter = tokens.slice(3, tokens.length).join(" ");
            }
        }
        else{
            executed = false;
        }
    }
    else if (transcript.toLowerCase().startsWith("change language")){
        //
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            midi = tokens[tokens.length-1];
            lang = tokens.slice(2, tokens.length-1).join(" ");
            changeLanguage(lang, midi);
        }
        else if (tokens.length == 3){
            //accept midi or language name.  
            midi = tokens[2];
            if (hasNumber(midi)){
                changeLanguage(midi);
            }
            else{
                lang = tokens[2];
                selectLanguage(lang);
            }
        
        }
        else{
            executed = false;
        }
    }
    else if (transcript.toLowerCase().startsWith("add language")){
        //
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            midi = tokens[tokens.length-1];
            lang = tokens.slice(2, tokens.length-1).join(" ");
            if (hasNumber(midi)){ //check if we have actually put in the midi.  
                addLanguage(lang.trim(), midi);
            }
        }
        else{
            executed = false;
        }
    }
    else if (transcript.toLowerCase().startsWith("add word")){
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            midi = tokens[tokens.length-1];
            //for now single word?  I dont think it matters, logic allows for multiple words.  
            //but we do need to time the speech and the midi well if we want to use the 4s timeout.  
            let word = tokens.slice(2, tokens.length-1).join(" ");
            if (hasNumber(midi)){ //check if we have actually put in the midi.
                let newmidi = addWord(word.trim(), midi);
                transcript = transcript.replace(midi, newmidi); //replace midi with new midi
                transcript = currentlanguage + ":" + transcript; //add language to transcript
            }
            else{
                executed = false;
            }
        }
        else{
            executed = false;
        }
    }
    else if (transcript.toLowerCase().startsWith("add tag")){
        tokens = transcript.split(" ");
        if (tokens.length >= 3){
            midi = tokens[tokens.length-1];
            //for now single word?  I dont think it matters, logic allows for multiple words.  
            //but we do need to time the speech and the midi well if we want to use the 4s timeout.  
            let tag = tokens.slice(2, tokens.length-1).join(" ");
            if (hasNumber(midi)){ //check if we have actually put in the midi.
                addTag(tag.trim(), "", midi);
            }
            else{
                tag = tokens.slice(2, tokens.length).join(" ");
                addTag(tag.trim());
            }
        }
        else{
            executed = false;
        }
    }
    else if (transcript.toLowerCase().startsWith("remove tag")){
        tokens = transcript.split(" ");
        if (tokens.length >= 3){
            midi = tokens[tokens.length-1];
            //for now single word?  I dont think it matters, logic allows for multiple words.  
            //but we do need to time the speech and the midi well if we want to use the 4s timeout.  
            let tag = tokens.slice(2, tokens.length-1).join(" ");
            if (hasNumber(midi)){ //check if we have actually put in the midi.
                console.log("error removing tag " + tag.trim() + " " + midi); 
                removeTag(tag.trim(), "", midi);
            }
            else{
                tag = tokens.slice(2, tokens.length).join(" ");
                removeTag(tag.trim());
            }
        }
        else{
            executed = false;
        }
    }
    else{
        executed = false;
    }
    
    //if we have any useful info add it.  
    if (keymaps[lang] != null && keymaps[lang].chat != null && typeof(keymaps[lang].chat) === "function" && executed==false){
        //this way we can have different chat functions for different languages, and organize better.  
        executed = keymaps[lang].chat(transcript);
    }
    
    if (typeof(MyChat) === "function" && executed==false){
        //really should not be using this.  add chat to keymaps[lang]
        MyChat(transcript);
    }
    else{
        if (executed){
            //make sound.  
            audioFeedback(commandcompletion);

            addComment("> " + transcript, helpme()); //not sure if we want the prefix here.  
        }
        else{
            if (pedal){
//                addComment(transcript, helpme());
            }
        }
    }
    return executed;
}


function removeLinks(text){
    text = text.replace(/\s*\([^)]*\)/g, "");
    text = text.replace("<br>", "");
    return text;
}

export function readMe(answer){
    answer = removeLinks(answer);
    let ssu = new SpeechSynthesisUtterance(answer);
    let svoice = $("#voiceSelect")[0].selectedIndex;
    ssu.voice = voices[svoice];
    ssu.rate = myrate;
    ssu.pitch = mypitch;
    window.speechSynthesis.cancel();
    //chat.js
    reading = true;
    ssu.onend = function (event) {
        console.log(event.timeStamp);
        reading = false;
    };

    window.speechSynthesis.speak(ssu);

}

//dependent on transcript functions.  
//need to untangle.  
export function addComment(comment, commenttime){
    //find where to splice and then reset the notes
    //notesarray.splice(i, 0, comment);
    createNotesArray();
    i = 0;
    while (i< notesarray.length && getTime(notesarray[i]) <= getSecsFromTime(commenttime)){
        i++;
    }
//	if (i==0) i=1;
    notesarray.splice(i, 0, comment + " (" + commenttime + ")");
    updateNotes();
    updateState(comment, commenttime, notesarray);

    
}

		



export function loadSpeech(){
    if (speech == true){
        window.SpeechRecognition = window.SpeechRecognition
                        || window.webkitSpeechRecognition;

        const recognition = new SpeechRecognition();
        recognition.interimResults = false;
        const wordp = document.querySelector('.words');
//        wordp.appendChild(p);

        recognition.addEventListener('result', e => {
            const transcript = Array.from(e.results)
                .map(result => result[0])
                .map(result => result.transcript)
                .join('')

            document.getElementById("p").setAttribute('value', transcript);
        //    console.log(transcript + ' (' + (end-start)/1000 + ')');
            //this function could be different for each use-case, right now same function
            //we are interacting via voice here, so we call Chat()
            //this is blank for analyze.html.  

            let mymidicommand = null;
            let ped = false;
            let cl = getPendingCommand(getPedal());
            let lang = "";
            if (cl != null){
                //we have a pending command, so we will use that.  
                lang = cl.lang;
                //for now just add space.  Always end with some midi command.  

            }
            if (typeof(midicontroller) !=='undefined' && midicontroller != null){
                mymidicommand = midicontroller.getMidiRecent();
                ped = midicontroller.pedal;
            }
            else{
                mymidicommand = getMidiRecent();
                ped = getPedal();                //
            }
            if (mymidicommand == null && !ped && cl == null){
                //if not executed immediately, add to pending commands, and wait for midi or further command.  
                
                let [t2, lang, found] = findCommand(transcript, mymidicommand); //this points to speech.js->findCommand
                if (found){
                    addCommandLog(transcript, null, true, lang);
                    //triggerCheckCommands?

                }
                else{
                    //unknown command, free chat.  
                    Chat(transcript);
                    document.getElementById("p").value = "";
                }
        //        Chat(transcript);
            }
            else{
                //waiting for midi command to complete.  
                console.log(mymidicommand);
                console.log("Pending Command:" + cl);
                addCommandLog(transcript, null, true, lang);
            }

        //    Chat(transcript);
            //not sure if we should reset this.  
        //    document.getElementById("p").value = ""
            
        });
        
        recognition.addEventListener("start", () => {
            console.log("Speech recognition service has started");
          });

        recognition.start();
        recognition.addEventListener('end', () => {
            recognition.start();
        });

        $("#p").on('keyup', function (event) {
        if (event.keyCode === 13) {
            console.log(document.getElementById("p").value + ' (' + (end-start)/1000 + ')')
            document.getElementById("p").value = ""
        }
        });
    }
    populateVoiceList();
    speechSynthesis.onvoiceschanged = populateVoiceList;
}

export function getVoice(){
    let svoice = $("#voiceSelect")[0].selectedIndex;
    return voices[svoice];
}

function populateVoiceList() {
    if (typeof window.speechSynthesis === "undefined") {
      return;
    }
  
    voices = window.speechSynthesis.getVoices();
  
    for (let i = 0; i < voices.length; i++) {
      const option = document.createElement("option");
      option.textContent = `${voices[i].name} (${voices[i].lang})`;
  
      if (voices[i].default) {
        option.textContent += " — DEFAULT";
      }
  
      option.setAttribute("data-lang", voices[i].lang);
      option.setAttribute("data-name", voices[i].name);
      document.getElementById("voiceSelect").appendChild(option);
    }
    if (voices.length > 2){
        let userAgentString = navigator.userAgent
        if (userAgentString.indexOf("Chrome") > -1){
            $("#voiceSelect")[0].selectedIndex = 2; //dont like the default voice.  
        }
        else{
            $("#voiceSelect")[0].selectedIndex = 1; //dont like the default voice.  
        }
    }
  }