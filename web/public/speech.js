
commandLog = [];
pendingCommands = [];
ss = null;
myrate = 0.7;
mypitch = 1;
keymap = new Keymap();

function addCommandLog(transcript, command, pending=false){
    //we want to have the time here.  
    let now = Date.now();
    commandLog.push({time: now, transcript: transcript, command: command, pending: pending});
}

function getPendingCommand(){
    if (commandLog.length > 0 && commandLog[commandLog.length-1].pending){
        return commandLog[commandLog.length-1];
    }   
    else{
        return null;
    }
}

//called from clock.js every second.  
//open-ended definitions must end with midi 60, 60.  
//add language, add word etc.  But 60, 60 not stored in keymap.  
//others will be defined in keymap.  
function checkCommands(){
    let cl = getPendingCommand();
    let midi = getMidiRecent();
    //if most recent is too recent wait some more.  
    //otherwise we assume this is a completed command.  
    //also if we have punctuation/end command, we can continue.  
    if (midi != null){
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
        while (done > 0 && midi !=null && midi.length > 0){
            prevtranscript = transcript;
            //find words in current language.  
            
            transcript = keymap.findCommand(transcript, midi);
            if (transcript != prevtranscript){

                done = completeMidi(midi);
                if (transcript.endsWith(" ")){  //use space as indicator of more parameters needed.
                    //still waiting.  
                    cl.transcript = transcript;
                    //we have added to the pending command.  
                    //can continue the command with more midi
                    //no use case at the moment for this.  
                }
                else{
                    Chat(transcript, callback, pending); //add waspendingflag
                    transcript = "";
                }
            }
            else{
                if (transcript != cl.transcript){
                    cl.transcript = transcript;
                }
                done = 0;
            }
        }
        
        if ((midi ==null || midi.length == 0) && transcript != ""){
            Chat(transcript, callback, pending); //add waspendingflag
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
            while (done > 0 && midi.length > 0){
                prevtranscript = transcript;
                //get parameters.  
                transcript = keymap.findCommand(transcript, midi);
                //have to set .complete to true.  
                if (transcript != prevtranscript){
                    done = completeMidi(midi);
                    if (transcript.endsWith(" ")){  //use space as indicator of more parameters needed.
                        //still waiting.  in this case perhaps extend the pendingTime.  
                    }
                    else{
                        Chat(transcript, callback, pending); //add waspendingflag
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
                    Chat(transcript, callback, pending); 
                    transcript = "";
                }
            }

        }
    }

    midi = getMidiRecent();
    mtemp = "";
    if (midi != null){
        for (let i=0; i<midi.length; i++){
            mtemp += midi[i].note + ",";
        }
    }
    return transcript + " " + mtemp;

}


function completeMidi(midi){
    let ret = 0;
    while (midi.length > 0 && midi[0].complete){
        midi.shift();
        ret++;
    }
    return ret;
}



function str_pad_left(string,pad,length) {
    return (new Array(length+1).join(pad)+string).slice(-length);
}

function helpme(){
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

//right now there is no chatting here, we are just using the comments.
function Chat(transcript, callback=null, pending=false){
    if (transcript.toLowerCase().startsWith("help")){

    }
    else if (transcript.toLowerCase() == "stop"){
        window.speechSynthesis.cancel();
    }
    else if (transcript.toLowerCase().startsWith("add language")){
        //
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            midi = tokens[tokens.length-1];
            lang = tokens.slice(2, tokens.length-1).join(" ");
            addLanguage(lang, midi);
        }
    }
    else if (transcript.toLowerCase().startsWith("add word")){
        tokens = transcript.split(" ");
        if (tokens.length > 3){
            midi = tokens[tokens.length-1];
            //for now single word?  I dont think it matters, logic allows for multiple words.  
            //but we do need to time the speech and the midi well if we want to use the 4s timeout.  
            word = tokens.slice(2, tokens.length-1).join(" ");
            addWord(word, midi);
        }
    }
    
    else{
        //...
        addComment(transcript, helpme());
    }
}


function addComment(comment, commenttime){
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
    
}

		

var speech = true;
window.SpeechRecognition = window.SpeechRecognition
                || window.webkitSpeechRecognition;

const recognition = new SpeechRecognition();
recognition.interimResults = false;
const words = document.querySelector('.words');
words.appendChild(p);

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


    mymidicommand = getMidiRecent();
    if (mymidicommand == null){
        Chat(transcript);
    }
    else{
        //waiting for midi command to complete.  
        console.log(mymidicommand);
        addCommandLog(transcript, null, true);
    }
//    Chat(transcript);
    //not sure if we should reset this.  
//    document.getElementById("p").value = ""
    
});
  
if (speech == true) {
    recognition.start();
    recognition.addEventListener('end', recognition.start);
}
$("#p").on('keyup', function (event) {
  if (event.keyCode === 13) {
     console.log(document.getElementById("p").value + ' (' + (end-start)/1000 + ')')
     document.getElementById("p").value = ""
  }
});

