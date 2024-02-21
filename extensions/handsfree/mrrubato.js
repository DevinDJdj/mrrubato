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
        this.keydict[ "" ] = { "3": { "0,12,0" : "start record", "0,10,0": "stop record",
            "0,7,12": "channel", //channel selector will be 13 and up to 23
            "0,5,12": "tab", //tab selector will be 13 and up to 23, 2 keys for up to 100 tabs each channel.  Need to store index of the tab in window
            //this will use channeltab variable to select from current channel.  
            "0,9,12": "bookmark", //bookmark selector will be 13 and up to 23, 3 keys or more.  
            //this will be usable in subsequent "tab commands" to open this named tab, this will also save the tab
            "0,7,0": "click",
            "0,6,0": "right click", 
            "0,5,0": "read", 
            "0,4,0": "scroll down",
            "0,4,12": "scroll up",
            "0,3,0": "page down",
            "0,3,12": "page up",
            "0,2,0": "continue",
            "0,2,12": "stop"
            }, 
            "4": {"0,0,12,12": "where am i", 
            "0,4,7,12": "activate mic", "12,7,4,0": "deactivate mic", 
            "0,3,7,12": "activate piano", "12,7,3,0": "deactivate piano",
            } };
        this.keydict["help"] = {};
        this.keydict["move"] = {};
        this.keydict["scroll"] = {};
        this.keydict["page"] = {};
        this.keydict["stop"] = {};
        this.keydict["read"] = {};
        this.keydict["where am i"] = {};
        this.keydict["search"] = {};
        this.keydict["tabs"] = {};
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

        c = new Command("back", "go back on current page", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
        this.commands.push(c);

        c = new Command("select", "make selection from list of links", function(transcript){
            console.log(transcript);
            //allow to open a google search for the query term on existing search.  
            //or open new tab for this search.              
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
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
                    console.log(tabs[i].url);
                    this.mr.tabnames[tabs[i].id] = tabs[i].title;
                    if (this.mr.allTabs[tabs[i].id] == undefined){
                        //initialize the tab.
                        this.mr.allTabs[tabs[i].id] = { 'tab': tabs[i], 'scriptLoaded': false, 'dom': ''};
                    }
                    else{
                        //save latest state of the tab.
                        this.mr.allTabs[tabs[i].id]['tab'] = tabs[i];
                    }

                    let channelindex = this.mr.channels.indexOf(tabs[i].windowId);
                    if (channelindex == -1){
                        this.mr.channels.push(tabs[i].windowId);
                        this.mr.channeltab.push([]);
                        channelindex = this.mr.channels.indexOf(tabs[i].windowId);
                    }

                    if (this.mr.channeltab[channelindex].indexOf(tabs[i].id) == -1){
                        this.mr.channeltab[channelindex].push(tabs[i].id);
                    }

                    if (tabs[i].active){
                        this.mr.currentTabs[tabs[i].windowId] = tabs[i].id;
    
                        if (tabs[i].url.includes("chrome-extension") || tabs[i].url.includes("chrome://")){
                            console.log('skipping ' + tabs[i].url);
                        }
                        else{
                            try{
                                if (!this.mr.allTabs[tabs[i].id].scriptLoaded){
                                    this.mr.currentTabId = tabs[i].id;
                                    chrome.scripting.executeScript({
                                        target : {tabId : tabs[i].id  },
                                        func : injectedFunction,
                                    });
                                    this.mr.allTabs[tabs[i].id].scriptLoaded = true;
                                }
                                this.mr.getDom(tabs[i].id);
                            }
                            catch(err){
                                console.log(err);
                            }
                        }
                    }
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
    
        chrome.tabs.sendMessage(tabid, {text: 'report_back', requestedTabId: tabid, qrdata: dataURL});//, this.doStuffWithDom);
    
    }

    doStuffWithDom(domContent) {
        console.log('I received the following DOM content from ' + domContent['tabid']);
    //    console.log('I received the following DOM content from ' + domContent['tabid'] + '\n' + domContent['dom']);
        this.mr.allTabs[domContent['tabid']]['dom'] = domContent['dom'];
    }
    

    findTabs(searchText = ''){
        
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

    Chat(transcript, callback=null){
        transcript = transcript.toLowerCase();
        console.log(transcript);
        //get all full commands - do any match?  
        console.log(this.commands);
        for (let i = 0; i < this.commands.length; i++){
            let c = this.commands[i];
            if (c.type == "full" && transcript == c.name){
                c.action(transcript, callback);
                break;
            }
            else if (c.type == "partial" && transcript.startsWith(c.name)){
                c.action(transcript, callback);
                break;
            }
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
        maxy = numkeys*aspectratio-1;

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
            heatmap[ypixel][xpixel].push(all[i]);
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
            
        
        }
        else if (msg.text === 'back'){
            window.history.back();
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
                    text = '';
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
            if (typeof el !=='undefined' && el !==null){
                text = el.innerText;

                console.log('Nearest: ' + localcursorx + ', ' + localcursory);
                currentElement = el;

            }
            else{
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

