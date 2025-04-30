//git
var giturl = 'https://api.github.com/repos/DevinDJdj/mrrubato';
var gitbranch = 'master';
var bookfolder = 'book'; //change to notes/book folder within the repository.  

var topicWindowSize = 3;


//db
var dbname = '/misterrubato/'; //RTDB folder for contents
var domain = 'https://misterrubato.com';
var rssurl = '/rss/data/';
var chatdomain = 'https://chat.misterrubato.com';

//youtube
var useyoutube = false;
var channelId = 'UC4dK3RpqBq2JpIkRmQn6HOA'; //@misterrubato doesnt work in URL, probably need to escape the @, but who cares.  

var IPC_NAME = 'pipes';
//define length of keyboard.  use keybot to define where we start looking.  

//keys
var keybot = {"base": 48, "meta": 48};
var KEY_BOT = 48;
var keytop = 72;
var commandcompletion = 20;
var playfeedback = false;
var volumeControl = "0.1" //document.querySelector("input[name='volume']");

var _octave = 12;

//video
var myrate = 1.7;
var mypitch = 1.0;

var vidbuffer = 10;

//speech
var speech = true;


var localprompt = 'You are a software engineer, investigating the source code and notes provided.  \n\
                   Use the documentation provided to answer the @@Question.  \n\
                   Each topic is marked by ** for example **MYTOPIC \n\
                   Keep the response short and less than 300 words.  \n\
                   You are trying to help summarize and explain the key points of the content provided to answer the @@Question.  \n\
                   After listing the key points, try to make one suggestion to improve the current source code.  \n\
                   Be sure to include a short answer to the question using the topics and source code noted by **MYTOPIC \n\
    ';

var myconfig = null;
//for now just local storage is fine I think.  Eventually should move this to DB probably.  

function loadUserConfig(){
    //load user config from local storage.  
    let userconfig = localStorage.getItem('userconfig');
    if (userconfig != null){
        let userconfigjson = JSON.parse(userconfig);
        if (userconfigjson.hasOwnProperty('myrate')){
            myrate = userconfigjson.myrate;
        }
        if (userconfigjson.hasOwnProperty('mypitch')){
            mypitch = userconfigjson.mypitch;
        }
        if (userconfigjson.hasOwnProperty('keybot')){
            keybot = userconfigjson.keybot;
        }
        if ("git" in userconfigjson){
            if ("giturl" in userconfigjson["git"]){
                giturl = userconfigjson["git"]["giturl"];
            }
            if ("gitbranch" in userconfigjson["git"]){
                gitbranch = userconfigjson["git"]["gitbranch"];
            }
            if ("bookfolder" in userconfigjson["git"]){
                bookfolder = userconfigjson["git"]["bookfolder"];
            }
            if ("topicWindowSize" in userconfigjson["git"]){
                topicWindowSize = userconfigjson["git"]["topicWindowSize"];
            }
        }
        if ("db" in userconfigjson){
            if ("dbname" in userconfigjson["db"]){
                dbname = userconfigjson["db"]["dbname"];
            }
            if ("domain" in userconfigjson["db"]){
                domain = userconfigjson["db"]["domain"];
            }
            if ("rssurl" in userconfigjson["db"]){
                rssurl = userconfigjson["db"]["rssurl"];
            }
            if ("chatdomain" in userconfigjson["db"]){
                chatdomain = userconfigjson["db"]["chatdomain"];
            }
        }
        if ("youtube" in userconfigjson){
            if ("useyoutube" in userconfigjson["youtube"]){
                useyoutube = userconfigjson["youtube"]["useyoutube"];
            }
            if ("channelId" in userconfigjson["youtube"]){
                channelId = userconfigjson["youtube"]["channelId"];
            }
        }
        if ("keys" in userconfigjson){
            if ("keybot" in userconfigjson["keys"]){
                keybot = userconfigjson["keys"]["keybot"];
            }
            if ("KEY_BOT" in userconfigjson["keys"]){
                KEY_BOT = userconfigjson["keys"]["KEY_BOT"];
            }
            if ("keytop" in userconfigjson["keys"]){
                keytop = userconfigjson["keys"]["keytop"];
            }
            if ("commandcompletion" in userconfigjson["keys"]){
                commandcompletion = userconfigjson["keys"]["commandcompletion"];
            }

            if ("playfeedback" in userconfigjson["keys"]){
                playfeedback = userconfigjson["keys"]["playfeedback"];
            }
            if ("volumeControl" in userconfigjson["keys"]){
                volumeControl = userconfigjson["keys"]["volumeControl"];
            }
            if ("_octave" in userconfigjson["keys"]){
                _octave = userconfigjson["keys"]["_octave"];
            }


        }
        if ("video" in userconfigjson){
            if ("myrate" in userconfigjson["video"]){
                myrate = userconfigjson["video"]["myrate"];
            }
            if ("mypitch" in userconfigjson["video"]){
                mypitch = userconfigjson["video"]["mypitch"];
            }
            if ("vidbuffer" in userconfigjson["video"]){
                vidbuffer = userconfigjson["video"]["vidbuffer"];
            }
        }
        if ("localprompt" in userconfigjson){
            localprompt = userconfigjson["localprompt"];
        }
        console.log(userconfigjson);
    }

    getConfig();  //update myconfig.  
    return JSON.stringify(myconfig, null, " ");
}

function saveUserConfig(cfg=""){
    let userconfig = JSON.stringify(getConfig());
    if (cfg !=""){
        userconfig = cfg;
    }
    localStorage.setItem('userconfig', userconfig);
    //if error what do we get?  
}

function getConfig(){
    let userconfig = {"myrate": myrate, "mypitch": mypitch, "keybot": keybot, 
        "git": { "giturl": giturl, "gitbranch": gitbranch, "bookfolder": bookfolder, "topicWindowSize": topicWindowSize}, 
        "db": {"dbname": dbname, "domain": domain, "rssurl": rssurl, "chatdomain": chatdomain}, 
        "youtube": {"useyoutube": useyoutube, "channelId": channelId}, 
        "keys": {"keybot": keybot, "KEY_BOT": KEY_BOT, "keytop": keytop, "commandcompletion": commandcompletion, "playfeedback": playfeedback, "volumeControl": volumeControl, "_octave": _octave}, 
        "video": {"myrate": myrate, "mypitch": mypitch, "vidbuffer": vidbuffer}, 
        "localprompt": localprompt
    };
    myconfig = userconfig;
    return userconfig;
}


export{
    getConfig, 
    saveUserConfig, 
    loadUserConfig, 
    myconfig    //use this 
}
