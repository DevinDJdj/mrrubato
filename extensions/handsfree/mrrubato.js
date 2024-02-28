// constructor function

class Keymap{
    constructor(){
        this.keys = [];
        this.keymap = []; //midinum - 48
        this.keydict = {};
        this.loadKeys();
    }
    loadKeys(){
        //spoken work + key = action
        //keydict["keyword"]["numkeys"]["key,key,key"] = "action"
        //find word command, if doesnt exist, we can search this blank dict, and if it keys match, we can see if the 
        //word represents a number.  If it does, we can use that number in the command.
        //i.e. "0,5,12" + "fifteen" = "tab 15"
        //lookup word command if it doesnt exist, use this map.  
        //anything ending in 0 is standalone command.  and doesnt require a word.  
        //ending in 12 requires continuation or additional word/parameter
        //otherwise it requires a word.  
        //separate these categories.   
        //blank
        this.keydict[ "" ] = { "3": { "0,11,0" : "start record", 
            "12,11,12": "stop record", //after this we should either have a name or keyset in the upper octave.  
            //this is essentially creating a commandset with all command log and midi log in time.  
            //definition should be 11 or 13 keys.  
            "12,5,12": "channel", //channel selector will be 13 and up to 23
            "12,7,12": "tab", //tab selector will be 13 and up to 23, 2 keys for up to 100 tabs each channel.  Need to store index of the tab in window
            //this will use channeltab variable to select from current channel.  
            "12,9,12": "bookmark", //bookmark selector will be 13 and up to 23, 5 keys or more.  
            //this will be usable in subsequent "tab commands" to open this named tab, this will also save the tab
            "0,7,0": "click",
            "0,6,0": "right click", 
            "0,5,0": "read", 
            "0,4,0": "scroll down",
            "0,3,0": "page down",
            "0,2,0": "stop"
            }, 
            "4": {"0,7,7,0": "where am i", 
            "0,5,5,0": "tabs",
            "0,4,4,0": "scroll up",
            "0,3,3,0": "page up",
            "0,2,2,0": "continue",
            "0,4,7,0": "activate mic", "0,7,4,0": "deactivate mic", 
            "0,3,7,0": "activate piano", "0,7,3,0": "deactivate piano",
            } };
            //basic functionality all keys should come before the word is complete.  Not sure if the user can handle this consistently 
            //but maybe best to make this a rule, to avoid problems.  Basically if said at the same time, it should work.  
            //keycommand + parameter word = action.  
            //wordcommand + parameter keyset = action.  
            //keycommand + parameter keyset = action.  In this case the keyset should essentially be the upper octave.  
            //general terms are even numbers.  Identifiers are odd.  
        this.keydict["help"] = {"1": {"1": "1"} }; //0 means any number, search for commands with this midi function after 1.  
        //this should also search up keywords which we have generated and correspond to this set of keys.  
        this.keydict["move"] = {"2": {}}; //bottom octave = Y coord, top octave = X coord
        this.keydict["scroll"] = {"1": {}}; //number of increments.  from middle C
        this.keydict["page"] = {"1": {}}; //number of pages to scroll.  from middle C
        this.keydict["search"] = {"8": {}}; 
        this.keydict["channel"] = {"5": {}}; //keywords are sets of 5 or 7 and more
        this.keydict["tabs"] = {};
        this.keydict["tab"] = {"7": {}}; //use the channel with another two keys
        this.keydict["bookmark"] = {"9": {}}; //probably just use the tab which we have defined with another two keys.  
        //then we can go to a bookmark without needing to go to the tab first.  
        this.keydict["commandset"] = {"11": {}, "13": {}}; //probably just use the tab which we have defined with another two keys.  
        //when running a commandset, how do we speed up?  
    }
    findCommand(transcript, midi){
        //return transcript
        //if transcript startswith any of these commands or equals anything in the keydict, prioritize this
        //if we can translate the midi return transcript, otherwise return ""
        return transcript;
    }

}

class Command {
    constructor(name, help, action, type = "full", mr = null){
        this.name = name;
        this.help = help;
        this.action = action;
        this.type = type; //full/partial/?  
        this.mr = mr; //mrrubato reference
    }
}

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

    checkCommands(){
        let cl = this.getPendingCommand();
        let midi = getMidiRecent();
        let transcript = "";
        let waiting = false;
        if (cl != null){
            transcript = cl.transcript;
            waiting = cl.waiting;
        }

        if (midi != null || cl !=null){
            console.log(cl);
            console.log(midi);
                //we have a command.  
            //try to find if we have something to do with the midi.  
            transcript = this.keymap.findCommand(transcript, midi);
            if (transcript != ""){
                this.Chat(transcript, null, waiting); //add waspendingflag
            }
            else{
                //still waiting for midi to complete?  
                //we should probably allow for more than 4 seconds.  Add on time here somehow.  
            }
        }
    }
    
    addCommandLog(transcript, command, windowId, tabid, waiting=false){
        let now = Date.now();
        this.commandLog.push({time: now-start, transcript: transcript, command: command, window: windowId, tab: tabid, waiting: waiting});
    }

    getPendingCommand(){
        if (this.commandLog[this.commandLog.length-1].waiting){
            return this.commandLog[this.commandLog.length-1];
        }   
        else{
            return null;
        }
    }

    getCommandLogRecent(since){
        let i=this.commandLog.length-1;
        while (i >-1 && ((this.commandLog[i].time > Date.now()-start-since) || this.commandLog[i].waiting)){
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
                        this.allTabs[tab.id].scriptLoaded = true;
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
    
    initCommands(){
        //add in order of importance so help works better.  
        let c = new Command("links", "List all links on the page", function(transcript){
            var array = [];
            var links = document.getElementsByTagName("a");
            for(var i=0, max=links.length; i<max; i++) {
                array.push(links[i].href);
            }            
            console.log(array);
        });
        this.commands.push(c);

        c = new Command("help", "", function(transcript){

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
        }, "partial", this);
//        c.mr = this;
        this.commands.push(c);

        c = new Command("move", "move mouse up/down/left/right", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
//            window.scrollBy(0, -window.innerHeight);
        }, "partial", this);
        this.commands.push(c);

        c = new Command("scroll", "scroll up/down/left/right", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
//            window.scrollBy(0, -window.innerHeight);
        }, "partial", this);
        this.commands.push(c);

        c = new Command("page", "page up/down", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
//            window.scrollBy(0, -window.innerHeight);
        }, "partial", this);
        this.commands.push(c);


        c = new Command("stop", "stop speaking", function(transcript){
            console.log('stopping speech');
            window.speechSynthesis.cancel();
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
        this.commands.push(c);

        c = new Command("continue", "continue reading next element", function(transcript){
            console.log('continue next');
            window.speechSynthesis.cancel();
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
        this.commands.push(c);

        c = new Command("read", "read from current cursor", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
        this.commands.push(c);

        c = new Command("click", "click on current element - list links in element and select one", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
        this.commands.push(c);

        c = new Command("play", "play embedded video/audio", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "partial", this);
        this.commands.push(c);

        c = new Command("pause", "pause embedded video/audio", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "partial", this);
        this.commands.push(c);

        c = new Command("video", "play embedded videos", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
        this.commands.push(c);

        c = new Command("audio", "play embedded audios", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
        this.commands.push(c);

        c = new Command("back", "go back on current page", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
        this.commands.push(c);

        c = new Command("open", "open a tab", function(transcript){
            console.log(transcript);
            //allow to open a google search for the query term on existing search.  
            //or open new tab for this search.              
            this.mr.findTabs(transcript.substring(5));

//            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "partial", this);
        this.commands.push(c);

        c = new Command("select", "make selection from list of links", function(transcript){
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
        }, "partial", this);
        this.commands.push(c);

        c = new Command("where am i", "gives status of current cursor and window", function(transcript){
            console.log('where am i');
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
        this.commands.push(c);

        c = new Command("search", "open new search for ...", function(transcript){
            console.log(transcript);
            //allow to open a google search for the query term on existing search.  
            //or open new tab for this search.  
            let action_url = this.mr.baseSearch + transcript.substring(7);
            chrome.tabs.create({ url: action_url });
            this.mr.Chat("tabs");
    
            //chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "partial", this);
        this.commands.push(c);

        c = new Command("tabs", "reload all tabs", function(transcript, callback){
            chrome.tabs.query({}, function(tabs) {        
                for (var i=0; i<tabs.length; i++) {
                    this.mr.initTab(tabs[i]);//, i, tabs.length, callback);
                }
                callback();
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
    
        chrome.tabs.sendMessage(tabid, {text: 'report_back', requestedTabId: tabid, qrdata: dataURL});
    
    }

    ping(tabid){
        chrome.tabs.sendMessage(tabid, {text: 'report_back', requestedTabId: tabid}, mr.pingResponse);
    }

    pingResponse(response){
        mr.allTabs[response['tabid'] ].scriptLoaded = true;        
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
            let windowId = this.allTabs[id].tab.windowId;
            let tabid = id;
            this.currentTabs[ windowId ] = tabid;
            for (var i=0; i<this.channels.length; i++){  
                if (this.channels[i] == windowId){
                    this.activeChannel = i;
                }
            }
            this.updateFocus(windowId, tabid);
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

    function findHeatmapElement(){
        let scrolly = window.scrollY; 
        let scrollx = window.scrollX;
        var xpixel = Math.floor((localcursorx+scrollx)*numkeys/docwidth);
        var ypixel = Math.floor((localcursory+scrolly)*numkeys*aspectratio/docheight);

        if (heatmap[ypixel][xpixel].length > 0){
            return getBestParent(heatmap[ypixel][xpixel][0]);
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
            initHeatmap();
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

