console.log('sidepanel.js');

var speech = true;
var currentTabs = {};
var tabnames = {};
var channels = [];
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
//    recognition.stop();
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
    recognition.addEventListener('end', recognition.start);

    Chat("tabs"); //get current tabs.  
}
$("#p").on('keyup', function (event) {
  if (event.keyCode === 13) {
     console.log(document.getElementById("p").value);
     document.getElementById("p").value = ""
  }
});

function getDom(tabid){
    chrome.tabs.sendMessage(tabid, {text: 'report_back'}, doStuffWithDom);

}

function doStuffWithDom(domContent) {
    console.log('I received the following DOM content:\n' + domContent);
}


function injectedFunction() {
    chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
        // If the received message has the expected format...
        if (msg.text === 'report_back') {
            // Call the specified callback, passing
            // the web-page's DOM content as argument
            sendResponse(document.all[0].outerHTML);
        }
        if (msg.text === 'scroll down') {
            // Call the specified callback, passing
            // the web-page's DOM content as argument
            window.scrollBy(0, 100);
        }
    });

    document.body.style.backgroundColor = "orange";
  }

function Chat(transcript){
    console.log(transcript);
    //keywords for listing tabs for instance.  
    //update currently listening tabs.  
    if (transcript == "tabs"){
        chrome.tabs.query({}, function(tabs) {        
            for (var i=0; i<tabs.length; i++) {
                console.log(tabs[i].url);
                tabnames[tabs[i].id] = tabs[i].title;
                if (tabs[i].active){
                    currentTabs[tabs[i].windowId] = tabs[i].id;
                    channels.push(tabs[i].windowId);
                    if (tabs[i].url.includes("chrome-extension")){
                        console.log('skipping ' + tabs[i].url);
                    }
                    else{
                        try{
                            chrome.scripting.executeScript({
                                target : {tabId : tabs[i].id  },
                                func : injectedFunction,
                            });
                            getDom(tabs[i].id);
                        }
                        catch(err){
                            console.log(err);
                        }
                    }
                }
            }
        });
    }
    //switch window/channel.  
    if (transcript.toLowerCase().startsWith("channel")) {
        console.log(transcript);
        //inject script to listen to channelX messages.  
        //maintain a list of tabs -> ChannelID, and only 
//        for (const [key, value] of myMap.entries()) {
//            console.log(key, value);
//        } 
        console.log(currentTabs[ channels[0] ] );
        console.log(tabnames[ currentTabs[ channels[0] ] ]);
        getDom(currentTabs[ channels[0] ]);
        
    }
    if (transcript.toLowerCase() == "scroll down"){
        console.log('scrolling');
        chrome.tabs.sendMessage(currentTabs[ channels[0] ], {text: 'scroll down'});
    }

}

