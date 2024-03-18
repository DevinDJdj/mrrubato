console.log('sidepanel.js');

var speech = true;
var prevtranscript = '';
var latestSearchTab = null;
var currentSelection = -1;
var mymidicommand = null;

var tempTabs = [];
var tempLinks = [];
var tempSelect = "tabs";

var mr = new Mrrubato();


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
    const now = Date.now();
    abstime = now - start;
    console.log(abstime);
    //match this with the midi messages.  If we have midi messages within the same time frame, utilize those.  
    //meaning will differ based on the command.  
    mymidicommand = getMidiRecent();
    console.log(mymidicommand);
    if (mymidicommand == null){
        Chat(transcript);
    }
    else{
        //waiting for midi command to complete.  
        let windowId = mr.channels[mr.activeChannel];
        let tabid = mr.currentTabs[ windowId ];
        mr.addCommandLog(transcript, null, windowId, tabid, true);
    }
    var confidence = event.results[0][0].confidence;
};


if (speech == true) {
    recognition.start();
    recognition.addEventListener('end', recognition.start);
    midienabled = 1;
    getHistory();
//    chrome.action.setPopup({popup: 'popup.html'});    
    chrome.action.setBadgeText({text: "on"}); // Version 1.1.8 - Initializing...
	chrome.action.setBadgeBackgroundColor({"color": [255, 255, 255, 100]}); 

    chrome.tabs.onUpdated.addListener(function
        (tabId, changeInfo, tab) {
          // read changeInfo data and do something with it (like read the url)
          let mytab = mr.allTabs[tabId];
          let same = tab.url.indexOf(mytab.tab.url);
          if (changeInfo.status === "complete" && (same == -1 || mytab.tab.url == "")) {
            // do something here

//            mr.allTabs[tabId] = undefined;
            console.log(tabId.toString() + ' ' +  changeInfo.url);
            //send message with refreshed DOM and QR code.  
            mr.allTabs[tabId] = { 'tab': tab, 'scriptLoaded': false, 'dom': ''};
            mr.tabnames[tabId] = tab.title;
//            mr.ping(tabId);
            //if this has a script already, then this should be set by the time this times out.  
            //ok maybe this works.  
            setTimeout(() => {
                mr.initTab(tab);
            }, 3000);
          }

          /*
          if (mr.allTabs[tabId] == undefined){
            setTimeout(() => {
                mr.initTab(tab);
            }, 3000);
          }
          */
        }
      );  

      text = "ready";
      mr.ss = new SpeechSynthesisUtterance(text);
      mr.ss.rate = mr.myrate;
      mr.ss.pitch = mr.mypitch;
      window.speechSynthesis.speak(mr.ss);

      Chat("tabs"); //get current tabs.  

      
    //check each second if we have some new message to send.  
    setInterval(checkCommands, 1000);
}

function checkCommands(){
    mr.checkCommands();
}



$("#p").on('keyup', function (event) {
  if (event.keyCode === 13) {
     console.log(document.getElementById("p").value);
     document.getElementById("p").value = ""
  }
});


function getNum(str){
    mynum = parseInt(str);
    if (isNaN(mynum)){
        mynum = text2num(str);
    }
    if (isNaN(mynum)){
        return -1;
    }
    else{
        return mynum;
    }
}

function findTabs(searchText = ''){
    tempTabs = [];
    s = '*' + searchText + '*';

    //just make my own function here to find case-insensitive.  Also fixes the 
    //async call.  We have all the titles already anyway in allTabs.  
    for (const [key, value] of Object.entries(mr.tabnames)) {
        if (value.toLowerCase().includes(searchText.toLowerCase())){
            console.log(key, value);
            tempTabs.push(parseInt(key));
        }
    }
    if (tempTabs.length == 1){
        mr.changeTab(tempTabs[0]);
    }
    else if (tempTabs.length > 1){
        currentSelection = -1;
        text = '';
        for (var i=0; i<tempTabs.length; i++){
            text += i.toString() + ' ' + mr.tabnames[ tempTabs[i] ];
            text += ' ';
        }
        mr.ss = new SpeechSynthesisUtterance(text);
        mr.ss.rate = mr.myrate;
        mr.ss.pitch = mr.mypitch;
        window.speechSynthesis.speak(mr.ss);
    }

/*
    chrome.tabs.query({'title': s}, function(tabs) {        
        console.log(tabs);
        if (tabs.length > 0){
            if (tabs.length == 1){
                mr.changeTab(tabs[0].id);
            }
            else{
                tempTabs = tabs;
                currentSelection = -1;
                text = '';
                for (var i=0; i<tabs.length; i++){
                    text += i.toString() + ' ' + tabs[i].title;
                    text += ' ';
                    console.log(tabs[i].title);
                }
                mr.ss = new SpeechSynthesisUtterance(text);
                mr.ss.rate = mr.myrate;
                mr.ss.pitch = mr.mypitch;
                window.speechSynthesis.speak(mr.ss);
        }
        }
    });
*/
}

function getHistory(searchText = '', maxItems = 25){
    var params = {text:searchText, maxResults:maxItems};
    var allItems = [];
    var itemIdToIndex = {};
    params.startTime = 0;
    params.endTime = Date.now();
    chrome.history.search(params, function(items) {
      var newCount = 0;
      for (var i = 0; i < items.length; i++) {
        var item = items[i];
        if (item.id in itemIdToIndex)
          continue;
        newCount += 1;
        allItems.push(item);
        itemIdToIndex[item.id] = allItems.length - 1;
      }    
    });
    return allItems;

}



  function updateSidePanel(response){
    console.log(response);
    //add to the channels list.  
    //these links dont work for some stupid reason due to the bad design in the chrome-extension framework.  
    //cant find easy workaround yet.  
    //leave for now.  
    var chandiv = document.getElementById('channels');
    chantbl = document.createElement('table');
    chantbl.style.border = '1px solid black';
    chandiv.innerHTML = '';

    for (var i=0; i<mr.channels.length; i++){
        var a = document.createElement('a');
        
        const tr = chantbl.insertRow();
        var linkText = document.createTextNode(mr.tabnames[ mr.currentTabs[ mr.channels[i] ] ]);
        linkText.id = i;
        a.appendChild(linkText);
        a.title = mr.tabnames[ mr.currentTabs[ mr.channels[i] ] ];
        a.href = '#channel' + i;
        a.id = i;
        a.addEventListener('click', function(event) {
            console.log(event);
            console.log(parseInt(event.target.id));
            mr.changeChannel(parseInt(event.target.id));

        });
        const td = tr.insertCell();
        td.style.border = '1px solid black';
        td.appendChild(a);

    }
    chandiv.appendChild(chantbl);
    chandiv.appendChild(document.createElement('br'));


    var tabdiv = document.getElementById('alltabs');
    tabdiv.innerHTML = '';
    tabtbl = document.createElement('table');
    tabtbl.style.border = '1px solid black';
        for (let tabid in mr.allTabs) {

            const tr = tabtbl.insertRow();
            var a = document.createElement('a');
            var linkText = document.createTextNode(mr.tabnames[ tabid ] );
            a.appendChild(linkText);
            a.title = mr.tabnames[ tabid ];
            a.href = '#tab' + tabid;
            a.id = tabid;
            a.addEventListener('click', function(event) {
                console.log(event);
                console.log(parseInt(event.target.id));
                mr.changeTab(parseInt(event.target.id));    
            });
            td = tr.insertCell();
            td.style.border = '1px solid black';
            td.appendChild(a);
            td = tr.insertCell();
            td.style.border = '1px solid black';            
            tab = mr.allTabs[tabid];
            td.appendChild(document.createTextNode(tab.audible));
//            console.log(tab.mutedInfo.muted);
            //tabdiv.appendChild(document.createElement('br'));
            
            //show if MIC is active or not, show if Midi is active or not.  
        
//            tabdiv.innerHTML += '<div id="tab' + tabid + '"><a onclick="changeFocus(' + tabid + ');" href="#">' + tabnames[tabid] + '</a></div>';
//            console.log(key, value);
        } 
        tabdiv.appendChild(tabtbl);
        tabdiv.appendChild(document.createElement('br'));        
  }

function Chat(transcript){
    console.log(transcript);
    //keywords for listing tabs for instance.  
    //update currently listening tabs.  
    if (transcript == "tabs"){
        mr.Chat(transcript, updateSidePanel);
    }
    else if (transcript == "home"){
        //go to the home page.  
        //open my sidepanel
    }
    //switch window/channel.  
    else if (transcript.toLowerCase().startsWith("channel")) {
        console.log(transcript);
        //change channel if needed.  
        //inject script to listen to channelX messages.  
        //maintain a list of tabs -> ChannelID, and only 
//        for (const [key, value] of myMap.entries()) {
//            console.log(key, value);
//        } 
//        mr.Chat(transcript);
        mynum = getNum(transcript.toLowerCase().substring(7));
        if (mynum < mr.channels.length){

            mr.changeChannel(mynum);
        }
        
    }
    else if (transcript.toLowerCase().startsWith("select")){
//        mr.Chat(transcript);
        mr.Chat(transcript);
        /*
        currentSelection = getNum(transcript.toLowerCase().substring(7));
        console.log('selected ' + currentSelection);
        window.speechSynthesis.cancel();

        if (currentSelection > -1 && currentSelection < tempTabs.length){
//            mr.changeTab(tempTabs[currentSelection].id);
            mr.changeTab(tempTabs[currentSelection]);
            tempTabs = [];
        }
        else{
            //selecting in current page from links or other item.  
            chrome.tabs.sendMessage(mr.currentTabs[ mr.channels[mr.activeChannel] ], {text: transcript.toLowerCase()});
        }
        */

    }
    else if (transcript.toLowerCase().startsWith("open")) {
        console.log(transcript);
        mr.Chat(transcript);
//        findTabs(transcript.substring(5));
        //search the tabs
        //list tabs which have this search.  
        //allow selection with midi controller.  
        //if no result inform.  

    }
    else if (transcript.toLowerCase().startsWith("history")) {
        //search history for this term.  
        //list history items for this term.  
        console.log(transcript);
        items = getHistory(transcript.substring(7));
        console.log(items);
        //allow selection with midi
        
    }
    else if (transcript.toLowerCase().startsWith("search")) {
        mr.Chat(transcript.toLowerCase());

    }
    else if (transcript.toLowerCase().startsWith("scroll")){
        console.log('scrolling');
        mr.Chat(transcript.toLowerCase());
    }
    else if (  transcript.toLowerCase().startsWith("help")){
        mr.Chat(transcript.toLowerCase());
    }
    else{
        mr.Chat(transcript.toLowerCase());
//        chrome.tabs.sendMessage(currentTabs[ channels[activeChannel] ], {text: transcript.toLowerCase()});
    }

}

