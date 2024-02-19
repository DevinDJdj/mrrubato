console.log('sidepanel.js');

var speech = true;
var currentTabs = {};
var tabnames = {};
var allTabs = {};
var activeChannel = 0;
var currentTabId = 0;
var channels = [];
var prevtranscript = '';
var latestSearchTab = null;
var currentSelection = -1;
var baseSearch = 'https://www.google.com/search?q=';
var mymidicommand = null;

var myrate = 0.7;
var mypitch = 1.0;
var ss = null;
var tempTabs = [];

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
    getHistory();
    Chat("tabs"); //get current tabs.  
    chrome.action.setPopup({popup: 'popup.html'});    
    chrome.action.setBadgeText({text: "on"}); // Version 1.1.8 - Initializing...
	chrome.action.setBadgeBackgroundColor({"color": [255, 255, 255, 100]}); 

    //listen to when the tabs are changed.  
    /*
    chrome.tabs.onActivated.addListener(function
        (activeInfo) {
          // read changeInfo data and do something with it (like read the url)
          if (activeInfo.tabId) {
            tabId = activeInfo.tabId;
            // do something here
            console.log(activeInfo.tabId.toString() + ' ' +  activeInfo.windowId + ' activated');
            //send message with refreshed DOM and QR code.  
            allTabs[tabId] = { 'tab': tab, 'scriptLoaded': false, 'dom': ''};
            chrome.scripting.executeScript({
                target : {tabId : tabId  },
                func : injectedFunction,
            });
            allTabs[tabId].scriptLoaded = true;
            setTimeout(() => {
                getDom(tabId);
            }, 2000);
          }
        }
      );  
    */    
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
            }, 2000);
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
    var allItems = [];
    s = '*' + searchText + '*';
    //just make my own function here to find case-insensitive.  Also fixes the 
    //async call.  We have all the titles already anyway in allTabs.  
    chrome.tabs.query({'title': s}, function(tabs) {        
        console.log(tabs);
        if (tabs.length > 0){
            if (tabs.length == 1){
                changeTab(tabs[0].id);
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
                ss = new SpeechSynthesisUtterance(text);
                ss.rate = myrate;
                ss.pitch = mypitch;
                window.speechSynthesis.speak(ss);
        }
        }
    });
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

function getDom(tabid){
    //add requestedTabId to know who this is coming from.  
    //this function mechanism should really allow for that by default.  
    url = allTabs[tabid].tab.url;
    //this qrcode only represents around 1000 chars
    url = url.padEnd(220); //gets around some bug https://stackoverflow.com/questions/30796584/qrcode-js-error-code-length-overflow-17161056

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
    console.log('I received the following DOM content from ' + domContent['tabid']);
//    console.log('I received the following DOM content from ' + domContent['tabid'] + '\n' + domContent['dom']);
    allTabs[domContent['tabid']]['dom'] = domContent['dom'];
}


function injectedFunction() {
    var localcursorx = 100; //local mouse cursor
    var localcursory = 100; //local mouse cursor
    var myrate = 0.7;
    var mypitch = 1.0;
    var ss = null;
    //document.elementFromPoint(localcursorx, localcursory).click();
    function getPositionXY(element) {
        let rect = element.getBoundingClientRect();
        if (rect.x < 0)
            rect.x = 0;
        if (rect.y < 0)
            rect.y = 0;
        return {
            x: rect.x,
            y: rect.y, 
            width: rect.width,
            height: rect.height
        };
    } 

    chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
        // If the received message has the expected format...
        if (msg.text === 'report_back') {
            // Call the specified callback, passing
            // the web-page's DOM content as argument
            //should pass dom as well as the tabid.  
            //pass the qrcode image here.  

            var all = document.getElementsByTagName("*");
            //does this have a text field?  If so, we can use it.  
            //get all interactive elements.  Can we tell if they have a function associated?  
            //This would be good info to have.  Then we know which are actually interactive, instead of just display elements.  
            var links = document.body.getElementsByTagName("a");

            var heatmap = []; //double array of y, x internal value represents another array of the elements obj which are at this position.  
            //we want y, x because we are scrolling, so x is always visible or the smaller dimension.  
//            var rowmap = []; 
            //we dont want a map of pixels, this is wasteful.  We want a map structure which is quantized (recent trend word lol).  
            //we also want to represent the key positions.  perhaps a single octave 12 is not enough.  Lets try 24.  
            //I like separation of keys for this, but for now we can use 24.  
            var docheight = Math.max( document.body.scrollHeight, document.body.offsetHeight, 
                document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight  );
            var docwidth = Math.max(document.body.scrollWidth, document.body.offsetWidth,
                document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );
            //had to look up the word for this.  
            var aspectratio = docheight / docwidth;
                //a bit of waste here, but its fine, just include all pixels size of width/24.  --
            //I was thinking about rounding for some reason for a moment, but dont think that is necessary.  
            //scroll and page control will be bottom octave perhaps.  top octave for interacting with the page.
            //essentially the top octave can be controlled by either mouse or keyboard.  
            var numkeys = 24;
            var maxx = numkeys-1;
            var maxy = numkeys*aspectratio-1;
            heatmap = Array(Math.floor(numkeys*aspectratio)).fill().map(() => Array(numkeys).fill([]));
            //so we have a 24 x 24 empty array.  
            //we will put the elements here.  
            //document.documentElement; //is this what we want?  

            for (var i=0, max=all.length; i < max; i++) {
                // Do something with the element here
                var pos = getPositionXY(all[i]);
                var xpixel = Math.floor(pos.x*numkeys/docwidth);
                var ypixel = Math.floor(pos.y*numkeys*aspectratio/docheight);
                if (xpixel > maxx)
                    xpixel = maxx;
                if (ypixel > maxy)
                    ypixel = maxy;
                //do we want to include the element in all pixels that it resides in?  
                //I think we do, but this may be wasteful.  
                //or do we create a tree struct of some sort?  
                //for now lets just search left and up if we dont have anything in the current pixel.  
                //if we have something in the current pixel, will it include a pointer to other elements?  
                //element.nextElementSibling, element.previousElementSibling, 
                //element.children, element.parentNode
                //allow zoom in and zoom out functionality when using the layout command.  
                //so once we get one element we are fine.  I suspect we will have an element in every pixel in most pages.  
                var width = all[i].clientWidth;
                var height = all[i].clientHeight;
                var innerHTML = all[i].innerHTML;
                var id = all[i].id;

                //is this enough?  
                heatmap[ypixel][xpixel].push({'x': xpixel, 'y': ypixel, 'width': width, 'height': height, 'innerHTML': innerHTML, 'id': id});
                //then just use getelementbyid to get the element for any operations.  

            }
            console.log('heatmap populated');

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
        currentTabs[ windowId ] = tabid;
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
    else if (transcript == "home"){
        //go to the home page.  
        //open my sidepanel
    }
    else if (transcript == "stop"){
        console.log('stopping speech');
        window.speechSynthesis.cancel();
        chrome.tabs.sendMessage(currentTabs[ channels[activeChannel] ], {text: transcript.toLowerCase()});
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
        getNum(transcript.toLowerCase().substring(7));
        if (mynum < channels.length){

            changeChannel(mynum);
        }
        console.log(currentTabs[ channels[activeChannel] ] );
        console.log(tabnames[ currentTabs[ channels[activeChannel] ] ]);
        getDom(currentTabs[ channels[activeChannel] ]);
        
    }
    else if (transcript.toLowerCase().startsWith("select")){
        currentSelection = getNum(transcript.toLowerCase().substring(7));
        console.log('selected ' + currentSelection);
        window.speechSynthesis.cancel();
        if (currentSelection > -1 && currentSelection < tempTabs.length){
            changeTab(tempTabs[currentSelection].id);
        }
        chrome.tabs.sendMessage(currentTabs[ channels[activeChannel] ], {text: transcript.toLowerCase()});

    }
    else if (transcript.toLowerCase().startsWith("open")) {
        console.log(transcript);
        findTabs(transcript.substring(5));
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
        console.log(transcript);
        //allow to open a google search for the query term on existing search.  
        //or open new tab for this search.  
        action_url = baseSearch + transcript.substring(7);
        chrome.tabs.create({ url: action_url });

        chrome.tabs.sendMessage(currentTabs[ channels[activeChannel] ], {text: transcript.toLowerCase()});

    }
    else if (transcript.toLowerCase() == "scroll down"){
        console.log('scrolling');
        chrome.tabs.sendMessage(currentTabs[ channels[activeChannel] ], {text: transcript.toLowerCase()});
    }
    else if (  transcript.toLowerCase().startsWith("help")){
        mr.Chat(transcript)
    }
    else{
        chrome.tabs.sendMessage(currentTabs[ channels[activeChannel] ], {text: transcript.toLowerCase()});
    }

}

