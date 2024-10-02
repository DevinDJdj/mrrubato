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
    if (mymidicommand == null && !pedal){
        //if not executed immediately, add to pending commands, and wait for midi or further command.  
        if (Chat(transcript) == false){
            addCommandLog(transcript, null, true);
        }
//        Chat(transcript);
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
