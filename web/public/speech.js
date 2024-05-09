
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
        let prevtranscript = transcript;
        pending = cl.pending;
        if (midi != null && midi.length > 0){
            transcript = keymap.findCommand(transcript, midi);
            if (transcript == prevtranscript){

            }
            else{
                completeMidi(midi);
                Chat(transcript, callback, pending); //add waspendingflag
                pending = false;
            }
        }
        else{
            Chat(transcript, callback, pending); //add waspendingflag
            pending = false;
        }

        if (pending && Date.now() - cl.time > recentTime){ //recentTime in midi.js
            //pop from the pending commands?  Why keep useless history?  
            commandLog.pop();
        }

    }
    else{
        if ((midi != null && midi.length > 0)){
            console.log(midi);

            let prevtranscript = "";
            //get command.  
            transcript = keymap.findCommand(transcript, midi);
            let done = completeMidi(midi);

            if (done > 0 && midi.length > 0){
                prevtranscript = transcript;
                //get parameters.  
                transcript = keymap.findCommand(transcript, midi);
                if (transcript != prevtranscript){
                    done = completeMidi(midi);
                    Chat(transcript, callback, pending); 
                }
                else if (transcript != ""){
                    //we have 4 seconds to add the parameters for this call if .  
                    //still pending.  Just add pending command.  
                    //or ignore.  
                    addCommandLog(transcript, null, true);
                }
            }
            else if (transcript !=""){
                //single command.  Must have at least half a second open here or whatever the timer is open time in order to execute this command.  
                //add a pending command, and if no more midi comes within half a second, we execute.  
                //will need to adjust this timer for the user.  
                addCommandLog(transcript, null, true);
            }

        }
    }


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
    else if (transcript.toLowerCase().startsWith("create language")){
        
    }
    else if (transcript.toLowerCase().startsWith("create word")){
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
    console.log(transcript + ' (' + (end-start)/1000 + ')');
    //this function could be different for each use-case, right now same function
    //we are interacting via voice here, so we call Chat()
    //this is blank for analyze.html.  
    Chat(transcript);
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

