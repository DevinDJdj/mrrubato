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

        c = new Command("page up", "page up", function(transcript){
            window.scrollBy(0, -window.innerHeight);
        });
        this.commands.push(c);

        c = new Command("page down", "page down", function(transcript){
            window.scrollBy(0, window.innerHeight);
        });
        this.commands.push(c);

        c = new Command("stop", "stop speaking", function(transcript){
            console.log('stopping speech');
            window.speechSynthesis.cancel();
            chrome.tabs.sendMessage(this.currentTabs[ this.channels[this.activeChannel] ], {text: transcript.toLowerCase()});
        });
        this.commands.push(c);

    }

    Chat(transcript){
        transcript = transcript.toLowerCase();
        console.log(transcript);
        //get all full commands - do any match?  
        console.log(this.commands);
        for (let i = 0; i < this.commands.length; i++){
            let c = this.commands[i];
            if (c.type == "full" && transcript == c.name){
                c.action(transcript);
                break;
            }
            else if (c.type == "partial" && transcript.startsWith(c.name)){
                c.action(transcript);
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