// constructor function
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

        c = new Command("read", "read from current cursor", function(transcript){
            chrome.tabs.sendMessage(this.mr.currentTabs[ this.mr.channels[this.mr.activeChannel] ], {text: transcript.toLowerCase()});
        }, "full", this);
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
                    if (tabs[i].active){
                        this.mr.currentTabs[tabs[i].windowId] = tabs[i].id;
    
                        if (this.mr.channels.indexOf(tabs[i].windowId) == -1){
                            this.mr.channels.push(tabs[i].windowId);
                        }
                        if (tabs[i].url.includes("chrome-extension")){
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
    
        chrome.tabs.sendMessage(tabid, {text: 'report_back', requestedTabId: tabid, qrdata: dataURL}, this.doStuffWithDom);
    
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

    function findNearestElement(){ //with text        
        let scrolly = window.scrollY; 
        let scrollx = window.scrollX;
        var el = document.elementFromPoint(scrollx + localcursorx, scrolly+localcursory);
        var text = '';
        var radius = 0;
        while (text == ''){
            if (scrollx+localcursorx -radius > 0){
                el = document.elementFromPoint(scrollx + localcursorx-radius, scrolly+localcursory);
                if (typeof el !=='undefined' && el !==null && el.innerText !==null && el.innerText != ''){
                    localcursorx -=radius;
                    break;
                }
            } 
            else if (scrollx+localcursorx + radius < window.innerWidth){
                el = document.elementFromPoint(scrollx+localcursorx+radius, scrolly+localcursory);
                if (typeof el !=='undefined' && el !==null && el.innerText !==null && el.innerText != ''){
                    localcursorx += radius;
                    break;
                }
            }
            else if (scrolly+localcursory - radius > 0){
                el = document.elementFromPoint(scrollx+localcursorx, scrolly+localcursory-radius);
                if (typeof el !=='undefined' && el !==null && el.innerText !==null && el.innerText != ''){
                    localcursory -= radius;
                    break;
                }
            }
            else if (scrolly+localcursory + radius < window.innerHeight){
                el = document.elementFromPoint(scrollx+localcursorx, scrolly+localcursory+radius);
                if (typeof el !=='undefined' && el !==null && el.innerText !==null && el.innerText != ''){
                    localcursory += radius;
                    break;
                }
            }
            radius += 50;
        }
        return el;
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
            text += localcursorx.toString() + ' x ' + localcursory.toString() + ' y ';
            text += document.title;
            
            console.log(localcursorx + ', ' + localcursory);
            obj = {'text': text};
            //sendResponse(obj);


            window.speechSynthesis.cancel();
            ss = new SpeechSynthesisUtterance(text);
            ss.rate = myrate;
            ss.pitch = mypitch;
            window.speechSynthesis.speak(ss);


        }
        else if (msg.text === 'page up') {
            window.scrollBy(0, -window.innerHeight);
        }
        else if (msg.text === 'page down') {
            window.scrollBy(0, window.innerHeight);
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
            console.log(localcursorx + ', ' + localcursory);
            el = findNearestElement();
            text = el.innerText;
            console.log('Nearest: ' + localcursorx + ', ' + localcursory);
            currentElement = el;

            window.speechSynthesis.cancel();
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

