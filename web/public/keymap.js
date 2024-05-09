class Keymap{
    constructor(){
        this.keys = [];
        this.keymap = []; //midinum - 48
        this.keydict = {};
        this.funcdict = {};
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

        //param dictionary.  1 and 2 are for parameters for functions.  Functions can take more than this, but how to demarcate end of parameters?  
        //if there is no demarcation, all midi are passed, and the function decides what to pop.  
        //This seems haphazard, but more convenient for the user.  

        //3 and 4 are for core functions themselves.  
        //5 and more are for user defined variables and functions which then can take 1-2 parameters.  
        //

        this.keydict[ "" ] = { 
            "3": { 
                "0,11,0" : "start record", 
                "12,11,12": "stop record", //after this we should either have a name or keyset in the upper octave.  
                //this is essentially creating a commandset with all command log and midi log in time.  
                //definition should be 11 or 13 keys.  
                //for now just associate this with a word.  We can use the word to find the commandset.
                //this will be more familiar for people.  This will trigger save commandset, no this should be manual.  
                //it is 12,10,12 so should be easy to trigger in sequence.  
                "0,10,0": "open", //open a tab or a previously saved commandset.  
                "12,10,12": "save", //save a commandset.  This will be a new commandset or overwrite an existing one if it exists.
                //or maybe prompt if exists.  
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
            "4": {
                "0,7,7,0": "where am i", 
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
        this.funcdict[""] = function(transcript, midi, keydict, key){            
            let c3 = keydict[""]["3"];
            let c4 = keydict[""]["4"];
            if (midi !=null && midi.length > 2){
                //search c3
                //midi[0].complete = true;
                //return transcript
            }
            if (midi !=null && midi.length > 3){
                //search c4
            }

        };

        this.keydict["help"] = {
            "1": {"1": "1"} 
        }; //0 means any number, search for commands with this midi function after 1.  
        //this should also search up keywords which we have generated and correspond to this set of keys.  
        
        //this is essentially the parameters which will be passed.  This needs to be recursive in some way.  Not sure how yet.  
        //but we need to be able to play this at whatever speed we can.  
        //return the transcript and the number of midi keys which were used.  
        this.keydict["move"] = {
            "1": 0, 
            "2": 12 //expected minimum offset from 1
        }; //bottom octave = Y coord, top octave = X coord
        this.funcdict["move"] = function(transcript, midi, keydict, key){
            //input transcript and return final transcript.  
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let x = -1;
            let y = -1;
            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "2"){
                    //this is the only length but other commands will have variable lengths.  
                    //allow for out of order.  
                    if (midi[0].note > midi[1].note){
                        x = midi[0].note - 60;
                        y = midi[1].note - 48;
                    }
                    else{
                        y = midi[0].note - 48;
                        x = midi[1].note - 60;
                    }


                    if (y > -1 && y < 12 && x > -1 && x < 12){
                        y = 11 - y; //reverse
                        transcript = "move " + x.toString() + " " + y.toString();
                        midi[0].complete = true;
                        midi[1].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "move error - incorrect parameters"
                    }
                }
            }
            //or just pop from midi as we use?  Is this good enough?  
            //if we have an error in any function it will cause problems downstream.  
            //I guess this is ok.  
            return transcript;
        };
        this.keydict["scroll"] = {"1": {"min": -12, "max": -1}, "2": {"min": 1, "max": 12}}; //number of increments.  from middle C
        //need a min/max for parameters.  
        this.funcdict["scroll"] = function(transcript, midi, keydict, key){
            //input transcript and return final transcript.  
            let commandlength = null;
            let commanddict = null;
            for (const [k, v] of Object.entries(keydict[key])) {
                if (parseInt(k) <= midi.length){
                    commandlength = k;
                    commanddict = v;
                };
            }
            //maybe not for all commands, but here, we set to blank in case we have incorrect params.  
            transcript = "";
            let x = 0;
            let y = 0;
            if (commandlength !== null){
                //we have a command map at least.  
                if (commandlength == "1"){
                    y = midi[0].note - 60;
                    if (y > -13 && y < 13){
                        y = -y; //reverse
                        transcript = "scroll " + y.toString();
                        midi[0].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "scroll error - incorrect parameters"
                    }
                }

                if (commandlength == "2"){
                    //this is the only length but other commands will have variable lengths.  
                    //allow for out of order.  
                    //scroll up or down 
                    if (midi[0].note > midi[1].note){
                        x = midi[0].note - 66;
                        y = midi[1].note - 54;
                    }
                    else{
                        y = midi[0].note - 54;
                        x = midi[1].note - 66;
                    }


                    if (y > -7 && y < 7 && x > -7 && x < 7){
                        y = -y; //reverse
                        transcript = "scroll " + y.toString() + " " + x.toString();
                        midi[0].complete = true;
                        midi[1].complete = true;
                        //I think this will work ok.  
                        //this allows us to move on to next command.  
                    }
                    else{
                        //not sure how I want to handle errors yet.  
                        return "scroll error - incorrect parameters"
                    }
                }
            }
            return transcript;
        };
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
        if (midi != null){
            for (const [key, value] of Object.entries(this.funcdict)) {
                if (transcript !=""){
                    if (key !="" && transcript.startsWith(key)){
                        let f = value;
                        transcript = f(transcript, midi, this.keydict, key);
                        return transcript;
                    }
                }
                else{
                    let f = value;
                    transcript = f(transcript, midi, this.keydict, key);
                    return transcript;
                }
            }
        }

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
