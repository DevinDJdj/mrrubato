console.log('sidepanel.js');

var speech = true;
var currentTabs = {};
var tabnames = {};
var allTabs = {};
var activeChannel = 0;
var currentTabId = 0;
var channels = [];
var prevtranscript = '';
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

/*
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
*/

if (speech == true) {
    recognition.start();
    recognition.addEventListener('end', recognition.start);
    midienabled = 1;

    Chat("tabs"); //get current tabs.  

    //listen to when the tabs are changed.  
    chrome.tabs.onUpdated.addListener(function
        (tabId, changeInfo, tab) {
          // read changeInfo data and do something with it (like read the url)
          if (changeInfo.url) {
            // do something here
            console.log(tabId.toString() + ' ' +  changeInfo.url);
            //send message with refreshed DOM and QR code.  
            allTabs[tabId] = { 'tab': tab, 'scriptLoaded': false, 'dom': ''};
            chrome.scripting.executeScript({
                target : {tabId : tabId  },
                func : injectedFunction,
            });
            allTabs[tabId].scriptLoaded = true;
            setTimeout(() => {
                getDom(tabId);
            }, 1000);
          }
        }
      );  

}
$("#p").on('keyup', function (event) {
  if (event.keyCode === 13) {
     console.log(document.getElementById("p").value);
     document.getElementById("p").value = ""
  }
});

function getDom(tabid){
    //add requestedTabId to know who this is coming from.  
    //this function mechanism should really allow for that by default.  
    url = allTabs[tabid].tab.url;

    var div = document.getElementById('qrgenerator');
    while(div.firstChild){
        div.removeChild(div.firstChild);
    }

    var qrcode = new QRCode("qrgenerator", {
        text: url,
        width: 128,
        height: 128,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
    var canvas = document.getElementById('qrgenerator').querySelector('canvas');

    var dataURL = canvas.toDataURL();
    console.log(dataURL);

    chrome.tabs.sendMessage(tabid, {text: 'report_back', requestedTabId: tabid, qrdata: dataURL}, doStuffWithDom);

}

function doStuffWithDom(domContent) {
    console.log('I received the following DOM content from ' + domContent['tabid'] + '\n' + domContent['dom']);
    allTabs[domContent['tabid']]['dom'] = domContent['dom'];
}


function injectedFunction() {
    var localcursorx = 100; //local mouse cursor
    var localcursory = 100; //local mouse cursor
    var myrate = 0.7;
    var mypitch = 1.0;
    var ss = null;
    //document.elementFromPoint(localcursorx, localcursory).click();
    chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
        // If the received message has the expected format...
        if (msg.text === 'report_back') {
            // Call the specified callback, passing
            // the web-page's DOM content as argument
            //should pass dom as well as the tabid.  
            //pass the qrcode image here.  
            obj = {'dom': document.all[0].outerHTML, 'tabid': msg.requestedTabId};
            sendResponse(obj);
            qr = document.getElementById('qr');
            console.log(msg.qrdata);
            if (qr == null){
                qr = document.createElement('img');
                qr.id = 'qr';
                qr.src = msg.qrdata;
                //style="position: fixed; bottom: 20px; right: 20px; z-index: 10000;
                qr.style.position = "fixed";
                qr.style.bottom = "40px";
                qr.style.right = "20px";
                qr.style.zIndex = "10000";
                document.body.appendChild(qr);
            }
            else{
                qr.src = msg.qrdata;
            }
            
        
        }
        else if (msg.text === 'links'){
            var array = [];
            var links = document.getElementsByTagName("a");
            for(var i=0, max=links.length; i<max; i++) {
                array.push(links[i].href);
            }            
        }
        else if (msg.text === 'where am i'){
            //send back response with localcursorx, localcursory and other info
            var limit = Math.max( document.body.scrollHeight, document.body.offsetHeight, 
                document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );
            currenty = window.scrollY;
            pctscrolled = currenty / limit;
            var s = Number(pctscrolled).toLocaleString(undefined,{style: 'percent', minimumFractionDigits:2});
            text = s;
            text += ' down the page';
            text += document.title;
            
            console.log(localcursorx + ', ' + localcursory);

            ss = new SpeechSynthesisUtterance(text);
            ss.rate = myrate;
            ss.pitch = mypitch;
            window.speechSynthesis.speak(ss);


        }
        else if (msg.text === 'move down') {
            localcursory += 100;
        }
        else if (msg.text === 'move up') {
            localcursory -= 100;
        }
        else if (msg.text === 'move right') {
            localcursorx += 100;
        }
        else if (msg.text === 'move left') {
            localcursorx -= 100;
        }

        else if (msg.text === 'scroll down') {
            window.scrollBy(0, 100);
        }
        else if (msg.text === 'scroll up') {
            window.scrollBy(0, -100);
        }
        else if (msg.text === 'scroll right') {
            window.scrollBy(100, 0);
        }
        else if (msg.text === 'scroll left') {
            window.scrollBy(-100, 0);
        }
        else if (msg.text == 'click'){
            document.elementFromPoint(localcursorx, localcursory).click();
        }
        else if (msg.text == 'read'){
            //read the page.  
            var el = document.elementFromPoint(localcursorx, localcursory);
            console.log(el);
            console.log(localcursorx + ', ' + localcursory);
            text = el.textContent;

            ss = new SpeechSynthesisUtterance(text);
            ss.rate = myrate;
            ss.pitch = mypitch;
            window.speechSynthesis.speak(ss);
        }
        else if (msg.text == 'stop'){
            //stop reading the page.  
            console.log('stopping speech');
            window.speechSynthesis.cancel();
        }
        else if (msg.text == 'speed up'){
            ss.rate += 0.2;
            myrate += 0.2;
        }
        else if (msg.text == 'slow down'){
            ss.rate -= 0.2;
            myrate -= 0.2;
        }
        else if (msg.text === 'qr'){
        }
        console.log(msg.text);
        
    });

    document.body.style.backgroundColor = "orange";

  }

  function changeTab(id){
        //this is the tab id.  
        windowId = allTabs[id].tab.windowId;
        tabid = id;
        for (var i=0; i<channels.length; i++){  
            if (channels[i] == windowId){
                activeChannel = i;
            }
        }
        updateFocus(windowId, tabid);
  }

  function changeChannel(id){
    if (id < channels.length){
        windowId = channels[id];
        tabid = currentTabs[ windowId ];
        activeChannel = id;
        updateFocus(windowId, tabid);
    }
  }

  function updateFocus(windowId, tabid){
    chrome.windows.update(windowId, {focused: true});
        chrome.tabs.get(tabid, function(tab) {
        if (windowId == tab.windowId){
            chrome.tabs.highlight({'windowId': windowId, 'tabs': tab.index}, function() {});
        }
    });

  }

  function updateSidePanel(){
    //add to the channels list.  
    var chandiv = document.getElementById('channels');
    chandiv.innerHTML = '';
    for (var i=0; i<channels.length; i++){
        var a = document.createElement('a');
        var linkText = document.createTextNode(tabnames[ currentTabs[ channels[i] ] ]);
        a.appendChild(linkText);
        a.title = tabnames[ currentTabs[ channels[i] ] ];
        a.href = '#channel' + i;
        a.id = i;
        a.addEventListener('click', function(event) {
            console.log(event);
            console.log(parseInt(event.target.id));
            changeChannel(parseInt(event.target.id));

        });
        chandiv.appendChild(a);
        chandiv.appendChild(document.createElement('br'));

    }

    var tabdiv = document.getElementById('alltabs');
        for (let tabid in allTabs) {
            var a = document.createElement('a');
            var linkText = document.createTextNode(tabnames[ tabid ] );
            a.appendChild(linkText);
            a.title = tabnames[ tabid ];
            a.href = '#tab' + tabid;
            a.id = tabid;
            a.addEventListener('click', function(event) {
                console.log(event);
                console.log(parseInt(event.target.id));
                changeTab(parseInt(event.target.id));    
            });
            tabdiv.appendChild(a);

            tab = allTabs[tabid];
            console.log(tab.audible);
            console.log(tab.url);
//            console.log(tab.mutedInfo.muted);
            tabdiv.appendChild(document.createElement('br'));
            
            //show if MIC is active or not, show if Midi is active or not.  
        
//            tabdiv.innerHTML += '<div id="tab' + tabid + '"><a onclick="changeFocus(' + tabid + ');" href="#">' + tabnames[tabid] + '</a></div>';
//            console.log(key, value);
        } 

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
                if (allTabs[tabs[i].id] == undefined){
                    //initialize the tab.
                    allTabs[tabs[i].id] = { 'tab': tabs[i], 'scriptLoaded': false, 'dom': ''};
                }
                else{
                    //save latest state of the tab.
                    allTabs[tabs[i].id]['tab'] = tabs[i];
                }
                if (tabs[i].active){
                    currentTabs[tabs[i].windowId] = tabs[i].id;

                    if (channels.indexOf(tabs[i].windowId) == -1){
                        channels.push(tabs[i].windowId);
                    }
                    if (tabs[i].url.includes("chrome-extension")){
                        console.log('skipping ' + tabs[i].url);
                    }
                    else{
                        try{
                            if (!allTabs[tabs[i].id].scriptLoaded){
                                currentTabId = tabs[i].id;
                                chrome.scripting.executeScript({
                                    target : {tabId : tabs[i].id  },
                                    func : injectedFunction,
                                });
                                allTabs[tabs[i].id].scriptLoaded = true;
                            }
                            getDom(tabs[i].id);
                        }
                        catch(err){
                            console.log(err);
                        }
                    }
                }
            }
        });

        updateSidePanel();
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
        console.log(currentTabs[ channels[activeChannel] ] );
        console.log(tabnames[ currentTabs[ channels[activeChannel] ] ]);
        getDom(currentTabs[ channels[activeChannel] ]);
        
    }
    else if (transcript.toLowerCase() == "scroll down"){
        console.log('scrolling');
        chrome.tabs.sendMessage(currentTabs[ channels[activeChannel] ], {text: transcript.toLowerCase()});
    }
    else{
        chrome.tabs.sendMessage(currentTabs[ channels[activeChannel] ], {text: transcript.toLowerCase()});
    }

}

