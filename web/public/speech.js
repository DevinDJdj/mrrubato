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

function addComment(comment, commenttime){
    //find where to splice and then reset the notes
    //notesarray.splice(i, 0, comment);
    createNotesArray();
    i = 0;
    while (i< notesarray.length && getTime(notesarray[i]) < getSecsFromTime(commenttime)){
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

