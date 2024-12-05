
var giturl = 'https://api.github.com/repos/DevinDJdj/mrrubato/commits?sha=master';
var dbname = '/misterrubato/';
var domain = 'https://misterrubato.com';
var chatdomain = 'https://chat.misterrubato.com';
var useyoutube = false;
var channelId = 'UC4dK3RpqBq2JpIkRmQn6HOA'; //@misterrubato doesnt work in URL, probably need to escape the @, but who cares.  

//define length of keyboard.  use keybot to define where we start looking.  
var keybot = {"base": 48, "meta": 48};
var KEY_BOT = 48;
var keytop = 72;
var commandcompletion = 20;
var playfeedback = false;
const volumeControl = "0.1" //document.querySelector("input[name='volume']");

var myrate = 1.7;
var mypitch = 1.0;

var vidbuffer = 10;

var speech = true;

//for now just local storage is fine I think.  Eventually should move this to DB probably.  

function loadUserConfig(){
    //load user config from local storage.  
    let userconfig = localStorage.getItem('userconfig');
    if (userconfig != null){
        userconfig = JSON.parse(userconfig);
        if (userconfig.hasOwnProperty('myrate')){
            myrate = userconfig.myrate;
        }
        if (userconfig.hasOwnProperty('mypitch')){
            mypitch = userconfig.mypitch;
        }
        if (userconfig.hasOwnProperty('keybot')){
            keybot = userconfig.keybot;
        }
    }
}

function saveUserConfig(){
    let userconfig = {"myrate": myrate, "mypitch": mypitch, "keybot": keybot};
    localStorage.setItem('userconfig', JSON.stringify(userconfig));
}

