// constructor function


class Tab{
    constructor(){
        this.id = 0;
        this.url = "";
        this.windowId = 0;
        this.tab = null;
        this.scriptLoaded = false;
        this.dom = null;
    }

}

//two classes one for the extension and one for the embedded script.  


//this is the main class for the extension.
class Mrrubato {
    constructor (){
//        this.midiLog = []; //history of midi commands.  Already have in midiarray
//	var obj = {"note": note, "velocity": velocity, "time": abstime, "duration": 0, osc: osc, pnote: pnote};
//const now = Date.now();
//abstime = now - start;

        this.commandLog = []; //history of voice commands with time.  {time: abstime, transcript: "command", command: c, channel: 0, tab: 0}
        this.pendingCommands = [];
        this.commands = [],
        this.currentTabs = {},
        this.tabnames = {},
        this.allTabs = {}, 
        this.activeChannel = 0, 
        this.currentTabId = 0, 
        this.channels = [], 
        this.channeltab = [],
        this.prevtranscript = '', 
        this.latestSearchTab = null, 
        this.currentSelection = -1, 
        this.baseSearch = 'https://www.google.com/search?q=', 
        this.mymidicommand = null, 
        this.myrate = 0.7, 
        this.mypitch = 1.0, 
        this.ss = null, 
        this.tempTabs = [],
        this.version = 1.0, 
        this.name = "Mrrubato"

        this.keymap = new Keymap(); //midinum - 48
        this.initCommands();
    }

    speak(text){
        window.speechSynthesis.cancel();
        this.ss = new SpeechSynthesisUtterance(text);
        this.ss.rate = this.myrate;
        this.ss.pitch = this.mypitch;
        window.speechSynthesis.speak(this.ss);
    }

    completeMidi(midi){
        let ret = 0;
        while (midi.length > 0 && midi[0].complete){
            midi.shift();
            ret++;
        }
        return ret;
    }

    checkCommands(){
        let cl = this.getPendingCommand();
        let midi = getMidiRecent();
        //if most recent is too recent wait some more.  
        //otherwise we assume this is a completed command.  
        //also if we have punctuation/end command, we can continue.  
        if (midi != null){
            this.completeMidi(midi);
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
                transcript = this.keymap.findCommand(transcript, midi);
                if (transcript == prevtranscript){

                }
                else{
                    this.completeMidi(midi);
                    this.Chat(transcript, callback, pending); //add waspendingflag
                    pending = false;
                }
            }
            else{
                this.Chat(transcript, callback, pending); //add waspendingflag
                pending = false;
            }

            if (pending && Date.now() - cl.time > recentTime){
                //pop from the pending commands?  Why keep useless history?  
                this.commandLog.pop();
            }
    
        }
        else{
            if ((midi != null && midi.length > 0)){
                console.log(midi);

                let prevtranscript = "";
                //get command.  
                transcript = this.keymap.findCommand(transcript, midi);
                let done = this.completeMidi(midi);
                let windowId = this.channels[this.activeChannel];
                let tabid = this.currentTabs[ windowId ];

                if (done > 0 && midi.length > 0){
                    prevtranscript = transcript;
                    //get parameters.  
                    transcript = this.keymap.findCommand(transcript, midi);
                    if (transcript != prevtranscript){
                        done = this.completeMidi(midi);
                        this.Chat(transcript, callback, pending); 
                    }
                    else if (transcript != ""){
                        //we have 4 seconds to add the parameters for this call if .  
                        //still pending.  Just add pending command.  
                        //or ignore.  
                        this.addCommandLog(transcript, null, windowId, tabid, true);
                    }
                }
                else if (transcript !=""){
                    //single command.  Must have at least half a second open here or whatever the timer is open time in order to execute this command.  
                    //add a pending command, and if no more midi comes within half a second, we execute.  
                    //will need to adjust this timer for the user.  
                    this.addCommandLog(transcript, null, windowId, tabid, true);
                }

            }
        }


    }
    addCommandLog(transcript, command, windowId, tabid, pending=false){
        //we want to have the time here.  
        let now = Date.now();
        this.commandLog.push({time: now, transcript: transcript, command: command, window: windowId, tab: tabid, pending: pending});
    }

    getPendingCommand(){
        if (this.commandLog.length > 0 && this.commandLog[this.commandLog.length-1].pending){
            return this.commandLog[this.commandLog.length-1];
        }   
        else{
            return null;
        }
    }

    getCommandLogRecent(since){
        let i=this.commandLog.length-1;
        while (i >-1 && ((this.commandLog[i].time > Date.now()-start-since) || this.commandLog[i].pending)){
            i--;
        }
        if (i == this.commandLog.length-1){
            return null;
        }
        else{
            let retarray = this.commandLog.slice(i+1);
            return retarray;
        }
    }

    initTab(tab){
        console.log(tab.url);
        this.tabnames[tab.id] = tab.title;

        if (this.allTabs[tab.id] == undefined){
            //initialize the tab.
            this.allTabs[tab.id] = { 'tab': tab, 'scriptLoaded': false, 'dom': ''};
        }
        else{
            //save latest state of the tab.
            this.allTabs[tab.id]['tab'] = tab;
        }

        let channelindex = this.channels.indexOf(tab.windowId);
        if (channelindex == -1){
            this.channels.push(tab.windowId);
            this.channeltab.push([]);
            channelindex = this.channels.indexOf(tab.windowId);
        }

        if (this.channeltab[channelindex].indexOf(tab.id) == -1){
            this.channeltab[channelindex].push(tab.id);
        }

        if (tab.active){
            this.currentTabs[tab.windowId] = tab.id;

            if (tab.url.includes("chrome-extension") || tab.url.includes("chrome://")){
                console.log('skipping ' + tab.url);
            }
            else{
            setTimeout(() => {
                try{
                    if (!this.allTabs[tab.id].scriptLoaded){
                        this.currentTabId = tab.id;
//                        this.allTabs[tab.id].scriptLoaded = true;
                        chrome.scripting.executeScript({
                            target : {tabId : tab.id  },
                            func : injectedFunction,
                        });
                    }
                    this.getDom(tab.id);
                }
                catch(err){
                    console.log(err);
                }
            }
            , 5000);
            }
        }

    }

    onError(error){
        console.log('error' + error);
    }
    setActiveWindow(windowInfo){
        console.log('set active window' + windowInfo.id);
        for (var i=0; i< this.channels.length; i++){
            if (this.channels[i] == windowInfo.id){
                this.activeChannel = i;
            }
        }
    }

    doCallback(callback, transcript){
        if (callback != null){
            callback(transcript);
        }
    }

    initCommands(){
        //add in order of importance so help works better.  
        let c = new Command("links", "List all links on the page", function(transcript, callback){
            var array = [];
            var links = document.getElementsByTagName("a");
            for(var i=0, max=links.length; i<max; i++) {
                array.push(links[i].href);
            }            
            console.log(array);
            this.mr.doCallback(callback, transcript);
            
        }, "partial", this);
        this.commands.push(c);

        c = new Command("help", "", function(transcript, callback){

            if (transcript == "help"){
                let text = 'Available commands:\n';
                console.log("Available commands:");
                    this.mr.commands.forEach(function(cmd){
                    console.log(cmd.name + " - " + cmd.help);
                    text += cmd.name + " - " + cmd.help + "\n";
        
                });
                this.mr.ss = new SpeechSynthesisUtterance(text);
                this.mr.ss.rate = this.mr.myrate;
                this.mr.ss.pitch = this.mr.mypitch;
                window.speechSynthesis.speak(this.mr.ss);

            }
            else{
                let text = '';
                transcript = transcript.replace("help", "").trim();
                this.mr.commands.forEach(function(cmd){
                    if (cmd.name == transcript){
                        console.log(cmd.name + " - " + cmd.help);
                        text += cmd.name + " - " + cmd.help + "\n";
                        }
                });
                this.mr.ss = new SpeechSynthesisUtterance(text);
                this.mr.ss.rate = this.mr.myrate;
                this.mr.ss.pitch = this.mr.mypitch;
                window.speechSynthesis.speak(this.mr.ss);

            }
            this.mr.doCallback(callback, transcript);
            
        }, "partial", this);
//        c.mr = this;
        this.commands.push(c);

        c = new Command("move", "move mouse up/down/left/right", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, transcript);
            });
//            window.scrollBy(0, -window.innerHeight);

        }, "partial", this);
        this.commands.push(c);

        c = new Command("scroll", "scroll up/down/left/right", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "partial", this);
        this.commands.push(c);

        c = new Command("page", "page up/down", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "partial", this);
        this.commands.push(c);


        c = new Command("stop", "stop speaking", function(transcript, callback){
            console.log('stopping speech');
            window.speechSynthesis.cancel();
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "full", this);
        this.commands.push(c);

        c = new Command("continue", "continue reading next element", function(transcript, callback){
            console.log('continue next');
            window.speechSynthesis.cancel();
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "full", this);
        this.commands.push(c);

        c = new Command("read", "read from current cursor", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });

        }, "full", this);
        this.commands.push(c);

        c = new Command("click", "click on current element - list links in element and select one", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "full", this);
        this.commands.push(c);

        c = new Command("play", "play embedded video/audio", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "partial", this);
        this.commands.push(c);

        c = new Command("pause", "pause embedded video/audio", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "partial", this);
        this.commands.push(c);

        c = new Command("video", "play embedded videos", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "full", this);
        this.commands.push(c);

        c = new Command("audio", "play embedded audios", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "full", this);
        this.commands.push(c);

        c = new Command("back", "go back on current page", function(transcript, callback){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
            
        }, "full", this);
        this.commands.push(c);

        c = new Command("open", "open a tab", function(transcript, callback){
            console.log(transcript);
            //allow to open a google search for the query term on existing search.  
            //or open new tab for this search.              
            this.mr.findTabs(transcript.substring(5));
            this.mr.doCallback(callback, transcript);

//            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "partial", this);
        this.commands.push(c);

        c = new Command("select", "make selection from list of links", function(transcript, callback){
            console.log(transcript);
            //allow to open a google search for the query term on existing search.  
            //or open new tab for this search.              
            this.mr.currentSelection = getNum(transcript.toLowerCase().substring(7));
            console.log('selected ' + this.mr.currentSelection);
            window.speechSynthesis.cancel();
    
            if (this.mr.currentSelection > -1 && this.mr.currentSelection < this.mr.tempTabs.length){
    //            mr.changeTab(tempTabs[currentSelection].id);
                this.mr.changeTab(this.mr.tempTabs[this.mr.currentSelection]);
                this.mr.tempTabs = [];
            }
            else{
                //selecting in current page from links or other item.  
                chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
//                this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ] = undefined;
            }
    
//            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
            this.mr.doCallback(callback, transcript);
        }, "partial", this);
        this.commands.push(c);

        c = new Command("where am i", "gives status of current cursor and window", function(transcript, callback){
            console.log('where am i');
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });
        }, "full", this);
        this.commands.push(c);

        c = new Command("search", "open new search for ...", function(transcript, callback){
            console.log(transcript);
            //allow to open a google search for the query term on existing search.  
            //or open new tab for this search.  
            let action_url = this.mr.baseSearch + transcript.substring(7);
            chrome.tabs.create({ url: action_url }, function(tab){
                this.mr.initTab(tab);
                this.mr.changeTab(tab.id);
            });
            this.mr.Chat("tabs");
    
            this.mr.doCallback(callback, transcript);
            //chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "partial", this);
        this.commands.push(c);

        c = new Command("find", "find ... in page", function(transcript, callback){
            console.log(transcript);
            //allow to open a google search for the query term on existing search.  
            //or open new tab for this search.  
//            let action_url = this.mr.baseSearch + transcript.substring(5);
//            chrome.tabs.create({ url: action_url });
//            this.mr.Chat("tabs");
    
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()}).then((response) => {
                this.mr.doCallback(callback, response.response);
            });

        }, "partial", this);
        this.commands.push(c);

        c = new Command("tabs", "reload all tabs", function(transcript, callback){

            chrome.tabs.query({}, function(tabs) {        
                for (var i=0; i<tabs.length; i++) {
                    this.mr.initTab(tabs[i]);//, i, tabs.length, callback);
                }

//                chrome.windows.getLastFocused({ populate: true }).then(this.mr.setActiveWindow, this.mr.onError);

                this.mr.doCallback(callback, transcript);
            });
    
        }, "full", this);
        this.commands.push(c);
    }


    getDom(tabid){
        //add requestedTabId to know who this is coming from.  
        //this function mechanism should really allow for that by default.  

        let url = this.allTabs[tabid].tab.url;
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


        this.ping(tabid, dataURL);
    }    

    ping(tabid, dataURL=""){
        if (this.allTabs[tabid] != undefined && this.allTabs[tabid].scriptLoaded==true){
            //already pinged/loaded
        }
        else{
            console.log('pinging' + tabid);
            chrome.tabs.sendMessage(tabid, {text: 'report_back', requestedTabId: tabid, qrdata: dataURL}, mr.pingResponse);
        }
    }

    pingResponse(response){
        mr.allTabs[response['tabid'] ].scriptLoaded = true;        
        
        //use response here for windowId and tabId.  
        //let windowId = this.allTabs[ response['tabid']].tab.windowId;
        console.log(response);
        audioFeedback(60, 100, 500);

    }

    doStuffWithDom(domContent) {
        console.log('I received the following DOM content from ' + domContent);

    //    console.log('I received the following DOM content from ' + domContent['tabid'] + '\n' + domContent['dom']);
//        this.mr.allTabs[domContent['tabid']]['dom'] = domContent['dom'];
    }
    

    findTabs(searchText = ''){
        this.tempTabs = [];

        //just make my own function here to find case-insensitive.  Also fixes the 
        //async call.  We have all the titles already anyway in allTabs.  
        for (const [key, value] of Object.entries(this.tabnames)) {
            if (value.toLowerCase().includes(searchText.toLowerCase())){
                console.log(key, value);
                this.tempTabs.push(parseInt(key));
            }
        }
        if (this.tempTabs.length == 1){
            this.changeTab(this.tempTabs[0]);
        }
        else if (this.tempTabs.length > 1){
            this.currentSelection = -1;
            let text = '';
            for (var i=0; i<this.tempTabs.length; i++){
                text += i.toString() + ' ' + this.tabnames[ this.tempTabs[i] ];
                text += ' ';
            }
            this.speak(text);
        }
            
    }

    changeTab(id){
            //this is the tab id.  
            let thistab = this.allTabs[id];
            if (thistab == undefined){
                console.log('tab not found');
            }
            let windowId = this.allTabs[id].tab.windowId;
            let tabid = id;
            this.currentTabs[ windowId ] = tabid;
            for (var i=0; i<this.channels.length; i++){  
                if (this.channels[i] == windowId){
                    this.activeChannel = i;
                }
            }
            this.updateFocus(windowId, tabid);
            //dont think I need this one.  
            this.getDom(this.currentTabs[ windowId ]);
    }

    changeChannel(id){
        if (id < this.channels.length){
            let windowId = this.channels[id];
            let tabid = this.currentTabs[ windowId ];
            this.activeChannel = id;
            this.updateFocus(windowId, tabid);
            console.log(this.currentTabs[ this.channels[this.activeChannel] ] );
            console.log(this.tabnames[ this.currentTabs[ this.channels[this.activeChannel] ] ]);
            this.getDom(this.currentTabs[ this.channels[this.activeChannel] ]);
    
        }
    }

    updateFocus(windowId, tabid){
        chrome.windows.update(windowId, {focused: true});
            chrome.tabs.get(tabid, function(tab) {
            if (windowId == tab.windowId){
                chrome.tabs.highlight({'windowId': windowId, 'tabs': tab.index}, function() {});
            }
        });

    }

    whereami(res){
        console.log(res);
    }

    Chat(transcript, callback=null, waspending=false){
        transcript = transcript.toLowerCase();
        console.log(transcript);
        //get all full commands - do any match?  
//        console.log(this.commands);
        let windowId = this.channels[this.activeChannel];
        let tabid = this.currentTabs[ windowId ];
        var commandFound = false;
        let c = null;
        for (let i = 0; i < this.commands.length; i++){
            c = this.commands[i];
            if (c.type == "full" && transcript == c.name){
                c.action(transcript, callback);
                commandFound = true;                
                break;
            }
            else if (c.type == "partial" && transcript.startsWith(c.name)){
                c.action(transcript, callback);
                commandFound = true;    
                break;
            }
        }
        if (!commandFound){
            c = null;
        }
        if (waspending){
            //should always return something.  
            let cl = this.getPendingCommand();
            cl.pending = false;
            cl.transcript = transcript;
            cl.c = c;
        }
        else{
            this.addCommandLog(transcript, c, windowId, tabid);
        }        
    }


    getNum(str){
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

    getHistory(searchText = '', maxItems = 25){
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
        
}


function injectedFunction(){
    var localcursorx = 400; //local mouse cursor
    var localcursory = 400; //local mouse cursor
    let scrollLeft = document.documentElement.scrollLeft;
    let scrollTop = document.documentElement.scrollTop;
    localcursorx += scrollLeft;
    localcursory += scrollTop;
    var myrate = 0.7;
    var mypitch = 1.0;
    var ss = null;
    var currentElement = null;
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

    var numkeys = 24;
    var maxx = numkeys-1;
    var maxy = numkeys*aspectratio-1;
    var tempLinks = [];
    var currentSelection = -1;
    var allVideos = [];
    var allAudios = [];
    var currentVideo = null;
    var currentAudio = null;
    var selectionMode = "links";
//document.elementFromPoint(localcursorx, localcursory).click();

//word2int
    var Small = {
        'zero': 0,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10,
        'eleven': 11,
        'twelve': 12,
        'thirteen': 13,
        'fourteen': 14,
        'fifteen': 15,
        'sixteen': 16,
        'seventeen': 17,
        'eighteen': 18,
        'nineteen': 19,
        'twenty': 20,
        'thirty': 30,
        'forty': 40,
        'fifty': 50,
        'sixty': 60,
        'seventy': 70,
        'eighty': 80,
        'ninety': 90
    };

    var Magnitude = {
        'thousand':     1000,
        'million':      1000000,
    };

    var a, n, g;

    function text2num(s) {
        a = s.toString().split(/[\s-]+/);
        n = 0;
        g = 0;
        a.forEach(feach);
        return n + g;
    }

    function feach(w) {
        var x = Small[w];
        if (x != null) {
            g = g + x;
        }
        else if (w == "hundred") {
            g = g * 100;
        }
        else {
            x = Magnitude[w];
            if (x != null) {
                n = n + g * x
                g = 0;
            }
            else { 
                console.log("Unknown number: "+w); 
            }
        }
    }

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
    
    function speak(text){
        window.speechSynthesis.cancel();
        ss = new SpeechSynthesisUtterance(text);
        ss.rate = myrate;
        ss.pitch = mypitch;
        window.speechSynthesis.speak(ss);
    }

    function getOffset( el ) {
        var _x = 0;
        var _y = 0;
        while( el && !isNaN( el.offsetLeft ) && !isNaN( el.offsetTop ) ) {
            _x += el.offsetLeft - el.scrollLeft;
            _y += el.offsetTop - el.scrollTop;
            el = el.offsetParent;
        }
        return { y: _y, x: _x };
    }
        
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


    function getBestParent(element){
        var w = element.clientWidth;
        var h = element.clientHeight;
        var pw = w;
        var ph = h;
        if (w < 1){ w = 1;}
        if (h < 1){ h=1;}
        var text = element.innerText;
        var parent = element;
        var ptext = text;
        var nextparent = element.parentNode;
        //200000 = 1000 * 400 (Dont want the full page)
        var looplimit = 10;
        while (pw*ph < 400000 && ptext.length < 500 && looplimit-- > 0){
            parent = element.parentNode;
            nextparent = parent.parentNode;
            ptext = parent.innerText;
            
            pw = nextparent.clientWidth;
            ph = nextparent.clientHeight;
            element = parent;
        }
        
        return parent;
    }

    function XYtomap(x, y){
        let scrolly = window.scrollY; 
        let scrollx = window.scrollX;
        var xpixel = Math.floor((x+scrollx)*numkeys/docwidth);
        var ypixel = Math.floor((y+scrolly)*numkeys*aspectratio/docheight);
        return [xpixel, ypixel];
    }

    function mapToXY(x, y){
        let xpixel = x*docwidth/numkeys;
        let ypixel = y*docwidth/numkeys;
        ypixel += window.scrollY;
        xpixel += window.scrollX;
        if (xpixel > docwidth){
            xpixel = docwidth;
        }
        if (ypixel > docheight){
            ypixel = docheight;
        }
        if (xpixel < 0){
            xpixel = 0;
        }
        if (ypixel < 0){
            ypixel = 0;
        }
        return [xpixel, ypixel];
    }


    function findHeatmapElement(searchText = ''){

        const [xpixel, ypixel] = XYtomap(localcursorx, localcursory);

        if (searchText != ''){
            let searchResults = [];
            maxx = numkeys-1;
            maxy = Math.floor(numkeys*aspectratio-1);
            for (var i=0; i<maxy; i++){
                for (var j=0; j<maxx; j++){
                    for (var k=0; k < heatmap[i][j].length; k++){

                        if (typeof heatmap[i][j][k].innerText !== 'undefined' && heatmap[i][j][k].innerText.toLowerCase().includes(searchText)){
                            let parent = getBestParent(heatmap[i][j][k]);
                            if (searchResults.indexOf(parent) == -1){
                                searchResults.push(parent);
                            }
                            k = heatmap[i][j].length;
                            //no need to push more than one.  
                        }                        
                    }
                }
            }

            //sort for length, sometimes the 0, 0 element contains the whole page for instance.  
            searchResults.sort((a, b) => a.innerText.length - b.innerText.length);
            return searchResults;

        }
        else{
            if (heatmap[ypixel][xpixel].length > 0){
                return getBestParent(heatmap[ypixel][xpixel][0]);
            }
        }
    }

    function findNearestElement(){ //with text        
        let scrolly = window.scrollY; 
        let scrollx = window.scrollX;
        var el = document.elementFromPoint(localcursorx, localcursory);
        var text = '';
        var radius = 0;
        while (text == '' && radius < 300){
            if (localcursorx -radius > 0){
                el = document.elementFromPoint(localcursorx-radius, localcursory);
                if (typeof el !=='undefined' && el !==null && el.innerText !==null && el.innerText != ''){
                    localcursorx -=radius;
                    break;
                }
            } 
            else if (localcursorx + radius < window.innerWidth){
                el = document.elementFromPoint(localcursorx+radius, localcursory);
                if (typeof el !=='undefined' && el !==null && el.innerText !==null && el.innerText != ''){
                    localcursorx += radius;
                    break;
                }
            }
            else if (localcursory - radius > 0){
                el = document.elementFromPoint(localcursorx, localcursory-radius);
                if (typeof el !=='undefined' && el !==null && el.innerText !==null && el.innerText != ''){
                    localcursory -= radius;
                    break;
                }
            }
            else if (localcursory + radius < window.innerHeight){
                el = document.elementFromPoint(localcursorx, localcursory+radius);
                if (typeof el !=='undefined' && el !==null && el.innerText !==null && el.innerText != ''){
                    localcursory += radius;
                    break;
                }
            }
            radius += 50;
        }
        return getBestParent(el);
    }

    function initHeatmap(){


        docheight = Math.max( document.body.scrollHeight, document.body.offsetHeight, 
            document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight  );
        docwidth = Math.max(document.body.scrollWidth, document.body.offsetWidth,
            document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );
        //had to look up the word for this.  
        aspectratio = docheight / docwidth;
    
        numkeys = 24;
        maxx = numkeys-1;
        maxy = Math.floor(numkeys*aspectratio-1);
        if (heatmap.length >= maxy ){
            return;
            //no need to repopulate.  
        }

        heatmap = [];
        // Call the specified callback, passing
        // the web-page's DOM content as argument
        //should pass dom as well as the tabid.  
        //pass the qrcode image here.  

        var all = document.getElementsByTagName("*");
        //does this have a text field?  If so, we can use it.  
        //get all interactive elements.  Can we tell if they have a function associated?  
        //This would be good info to have.  Then we know which are actually interactive, instead of just display elements.  
        var links = document.body.getElementsByTagName("a");

        //a bit of waste here, but its fine, just include all pixels size of width/24.  --
        //I was thinking about rounding for some reason for a moment, but dont think that is necessary.  
        //scroll and page control will be bottom octave perhaps.  top octave for interacting with the page.
        //essentially the top octave can be controlled by either mouse or keyboard.  
        heatmap = Array(Math.floor(numkeys*aspectratio)).fill().map(() => Array(numkeys).fill([]));
        //so we have a 24 x 24 empty array.  
        //we will put the elements here.  
        //document.documentElement; //is this what we want?  

        for (var i=0, max=all.length; i < max; i++) {
            // Do something with the element here
            let currenty = 0;//window.scrollY;
            let currentx = 0;//window.scrollX;
            var pos = getOffset(all[i]);

            //var pos = getPositionXY(all[i]);
            var xpixel = Math.floor((pos.x+currentx)*numkeys/docwidth);
            var ypixel = Math.floor((pos.y+currenty)*numkeys*aspectratio/docheight);
            if (xpixel < 0)
                xpixel = 0;
            if (ypixel < 0)
                ypixel = 0;
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
            /*
            var width = all[i].clientWidth;
            var height = all[i].clientHeight;
            var innerHTML = all[i].innerHTML;
            var innerText = all[i].innerText;
            var id = all[i].id;
            */
            //is this enough?  
            //heatmap[ypixel][xpixel].push({'x': xpixel, 'y': ypixel, 'width': width, 'height': height, 'innerHTML': innerHTML, 'innerText': innerText, 'id': id});
            try{
                heatmap[ypixel][xpixel].push(all[i]);
                if (all[i].tagName == 'video'){
                    allVideos.push(all[i]);
                    currentVideo = all[i];
                }
                if (all[i].tagName == 'audio'){
                    allAudios.push(all[i]);
                    currentAudio = all[i];
                }
            }

            catch(err){
                console.log(err);
            }
            //then just use getelementbyid to get the element for any operations.  

        }
        console.log('heatmap populated');

        //why is this not working properly?  
//            obj = {'dom': document.all[0].outerHTML, 'tabid': msg.requestedTabId};
//            sendResponse(obj);

    }

    chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
        // If the received message has the expected format...
        if (msg.text === 'report_back') {
            initHeatmap();
            qr = document.getElementById('qr');
            console.log(msg.qrdata);
            if (qr == null){
                if (msg.qrdata != ""){
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
            }
            else{
                qr.src = msg.qrdata;
            }
            obj = {'text': 'report_back', 'tabid': msg.requestedTabId};
            sendResponse(obj);
            
        
        }
        else if (msg.text === 'back'){
            window.history.back();
        }
        //get audio, get video
        else if (msg.text === 'audio'){
            var audios = document.getElementsByTagName("audio");
            allAudios = audios;
            if (audios.length < 1){
                speak('no audio elements found');
            }
            else if (audios.length == 1){
                audios[0].play();
                currentAudio = audios[0];
            }
            else{                    
                tempLinks = audios;
                currentSelection = -1;
                selectionMode = "audios";
                text = tempLinks.length.toString() + ' audio elements found';
                for (var i=0; i<tempLinks.length; i++){
                    let src = tempLinks[i].src;
                    if (typeof src === 'undefined' || src == ''){
                        src = tempLinks[i].getElementsByTagName("source")[0].src;
                    }
                    text += i.toString() + ' ' + src;
                    text += ' ';
                }
                speak(text);
            }
        }


        else if (msg.text === 'video'){
            var videos = document.getElementsByTagName("video");
            allVideos = videos;
            if (videos.length < 1){
                speak('no video elements found');
            }
            else if (videos.length == 1){
                videos[0].play();
                currentVideo = videos[0];
            }
            else{                    
                tempLinks = videos;
                currentSelection = -1;
                selectionMode = "videos";
                text = tempLinks.length.toString() + ' videos found.  ';
                for (var i=0; i<tempLinks.length; i++){
                    let src = tempLinks[i].src;
                    if (typeof src === 'undefined' || src == ''){
                        src = tempLinks[i].getElementsByTagName("source")[0].src;
                    }
                    text += i.toString() + ' ' + src;
                    text += ' ';
                }
                speak(text);
            }
        }

        else if (msg.text.startsWith('play')){
            //pause video and audio.  
            let mytype = msg.text.toLowerCase().substring(5);
            if (mytype == 'audio'){
                
            }
            else{
                mytype = 'video';
            }
            if (currentVideo != null && mytype == 'video'){
                currentVideo.play();
            }
            else if (currentAudio != null && mytype == 'audio'){
                currentAudio.play();
            }
        }
        else if (msg.text.startsWith('pause')){
            //pause video and audio.  
            let mytype = msg.text.toLowerCase().substring(6);
            if (mytype == 'audio'){
                
            }
            else{
                mytype = 'video';
            }

            if (currentVideo != null && mytype == 'video'){
                currentVideo.pause();
            }
            else if (currentAudio != null && mytype == 'audio'){
                currentAudio.pause();
            }
        }
        else if (msg.text === 'click'){
            if (currentElement != null){
                var links = currentElement.getElementsByTagName("a");
                if (links.length < 1){
                    links[0].click();
                }
                else{                    
                    tempLinks = links;
                    currentSelection = -1;
                    selectionMode = "links";
                    text = tempLinks.length.toString() + ' links found.  ';
                    for (var i=0; i<tempLinks.length; i++){
                        text += i.toString() + ' ' + tempLinks[i].innerText;
                        text += ' ';
                    }
                    speak(text);
                }
            }
        }
        else if (msg.text.startsWith('select')){
            let mynum = getNum(msg.text.toLowerCase().substring(7));
            console.log('selected ' + currentSelection);
            window.speechSynthesis.cancel();
            if (selectionMode == "links"){
                if (mynum > -1 && mynum < tempLinks.length){
                    tempLinks[mynum].click();
                }
            }    
            if (selectionMode == "find"){
                if (mynum > -1 && mynum < tempLinks.length){
                    var pos = getOffset(tempLinks[mynum]);
                    localcursorx = pos.x;
                    localcursory = pos.y;
                    window.scrollTo(0, localcursory);
                    //should we do this other places as well?  
                    //lets scroll here to avoid confusion.  
                    let text = tempLinks[mynum].innerText;
                    //find and speak.  
                    speak(text);
                            
                }
            }    
            else if (selectionMode == "videos"){
                if (mynum > -1 && mynum < tempLinks.length){
                    tempLinks[mynum].play();
                    currentVideo = tempLinks[mynum];
                }
            }
            else if (selectionMode == "audios"){
                if (mynum > -1 && mynum < tempLinks.length){
                    tempLinks[mynum].play();
                    currentAudio = tempLinks[mynum];
                }
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
            xpixel = Math.floor(localcursorx*numkeys/docwidth);
            ypixel = Math.floor((localcursory+currenty)*numkeys*aspectratio/docheight);
            text += xpixel.toString() + ' x ' + ypixel.toString() + ' y ';
            text += document.title;
            
            console.log(localcursorx + ', ' + localcursory);
            obj = {'text': text};
            //sendResponse(obj);


            speak(text);

        }
        else if (msg.text === 'page up') {
            window.scrollBy(0, -window.innerHeight);
        }
        else if (msg.text === 'page down') {
            window.scrollBy(0, window.innerHeight);
            setTimeout(initHeatmap, 2000);
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
        else if (msg.text.startsWith('move'))
        {
            //move to a specific location.  
            //this should be a x y location.  
            params = msg.text.toLowerCase().substring(5).split(' ');
            //this is the heatmap value.  
            //multiply by 2 on the send side.  
            x = getNum(params[0]);
            y = getNum(params[1]);
            //for now just use the y value to scroll to this location.  
            //for now we are just using what is on screen but eventually we can just use all heatmap elements probably.  
            currenty = window.scrollY;
            [localcursorx, localcursory] = mapToXY(x, y);
//            localcursory = Math.floor((y+currenty)*numkeys*aspectratio/docheight);
//            localcursorx = Math.floor(x*numkeys/docwidth);
            
//            ypixel = Math.floor((y+currenty)*numkeys*aspectratio/docheight);

            //dont actually scroll here.  Just for testing.  
            //use scroll ... to scroll.  
            //window.scrollTo(0, localcursory);
        }

        else if (msg.text === 'scroll down') {
            window.scrollBy(0, 100);
            setTimeout(initHeatmap, 2000);
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
        else if (msg.text.startsWith("scroll")){
            params = msg.text.toLowerCase().substring(7).split(' ');
            y = getNum(params[0]);
            x = 0;
            //we never scroll horizontal.  I guess we can to just show it.  
            //But there is no recalculation of heatmap pixels for it.  
            if (params.length > 1){
                x = getNum(params[1]);
            }
//            currenty = window.scrollY;
            [x, y] = mapToXY(x, y);
            window.scrollTo(x, y);
            setTimeout(initHeatmap, 2000);

        }

        else if (msg.text.startsWith('find')){
            var searchText = msg.text.substring(5);
            searchText = searchText.toLowerCase();
            let els = findHeatmapElement(searchText);
            let text = '';
            if (els.length > 0){
                let tempMap = [];

                for (var i=0; i<els.length; i++){
                    f = els[i].innerText.indexOf(searchText);
                    s = els[i].innerText.indexOf(" ", f-30);
                    if (s < f-50 || s > f){
                        s = f-50;
                    }
                    if (s < 0){
                        s = 0;
                    }
                    e = els[i].innerText.indexOf(" ", f+30);
                    if (e > f+50 || e < 0){
                        e = f+50;
                    }
                    if (e > els[i].innerText.length){
                        e = els[i].innerText.length;
                    }
                    if (tempMap.indexOf(els[i].innerText.substring(s, e)) == -1){
                        tempMap.push(els[i].innerText.substring(s, e));
                        //dont repeat yourself.  There is some repetition because of the parent/child search.  
                        tempLinks.push(els[i]);
                    }
                }
                text = tempMap.length.toString() + ' instances found.  ';
                for (var j=0; j<tempMap.length; j++){
                    text += j.toString() + ' ' + tempMap[j];
                    text += '. ';
                }
                selectionMode = "find";
            }
            else{
                text = searchText + ' not found';
            }
            speak(text);
        }
        else if (msg.text == 'read'){
            //read the page.  
            console.log(localcursorx + ', ' + localcursory);
//            el = findNearestElement();
            el = findHeatmapElement();
            text = "";
            if (typeof el !=='undefined' && el !==null){
                text = el.innerText;

                console.log('Nearest: ' + localcursorx + ', ' + localcursory);
                currentElement = el;

            }
            if (text == ''){
                text = 'no text found';
            }
            speak(text);
        }
        else if (msg.text == 'continue'){
            //read the page.  
            console.log(localcursorx + ', ' + localcursory);
            text = '';
            if (currentElement != null){
                el = currentElement.nextElementSibling;
                text = 'next sibling ';
            }
            if (el !=null){
                text += el.innerText;
                console.log('Nearest: ' + localcursorx + ', ' + localcursory);
                currentElement = el;

            }
            else {
                text = 'no more elements';
            }
            speak(text);
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

