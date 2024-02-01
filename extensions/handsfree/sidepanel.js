console.log('sidepanel.js');

var speech = true;
window.SpeechRecognition = window.SpeechRecognition
                || window.webkitSpeechRecognition;

const recognition = new SpeechRecognition();
recognition.interimResults = false;
const words = document.querySelector('.words');
words.appendChild(p);


recognition.onstart = function() {
    console.log("We are listening. Try speaking into the microphone.");
};

recognition.onspeechend = function() {
    // when user is done speaking
    recognition.stop();
}
              
// This runs when the speech recognition service returns result
recognition.onresult = function(event) {
    var transcript = event.results[0][0].transcript;
    document.getElementById("p").setAttribute('value', transcript);
    console.log(transcript);
    //this function could be different for each use-case, right now same function
    //we are interacting via voice here, so we call Chat()
    //this is blank for analyze.html.  
    Chat(transcript);
    var confidence = event.results[0][0].confidence;
};

recognition.addEventListener('result', e => {
    const transcript = Array.from(e.results)
        .map(result => result[0])
        .map(result => result.transcript)
        .join('')

    document.getElementById("p").setAttribute('value', transcript);
    console.log(transcript);
    //this function could be different for each use-case, right now same function
    //we are interacting via voice here, so we call Chat()
    //this is blank for analyze.html.  
    Chat(transcript);
    //not sure if we should reset this.  
//    document.getElementById("p").value = ""
    
});
  
if (speech == true) {
    recognition.start();
//    recognition.addEventListener('end', recognition.start);
}
$("#p").on('keyup', function (event) {
  if (event.keyCode === 13) {
     console.log(document.getElementById("p").value);
     document.getElementById("p").value = ""
  }
});

function Chat(transcript){
    console.log(transcript);
}
