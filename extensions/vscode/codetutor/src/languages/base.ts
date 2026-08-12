import * as vscode from 'vscode';

export default class LANG {

    
    config = {};
    keybot = 69;
    keyoffset = 0;
    funcdict = {};
    midwordtree = {}; 
    name = "base";
    

    //base specific variables for generic keypresses, selection, and navigation
    //ALLCAPS = vscode handler..
    highlight = false; //whether to highlight text or not


    constructor(){
        console.log("base language constructor");
    }

    init(config){
        //optional init function
        console.log("base language init");
        this.config = config || {};
        this.load();
    }

    load(){
        let obj = {
            "2":{
                "PAUSE": [0,-1],
                "GENERATE": [0, 1],
                "HIGHLIGHT": [0,2],
                
            },
            "3":{
                "HOME": [0,-5,-6], 
                "END": [0,-5,-4],
                "PGUP": [0,-5,-1],
                "PGDN": [0,-5,-2],
                "UP": [0,-4,-1],
                "DOWN": [0,-4,-2],
                "LEFT": [0,-4,-5],
                "RIGHT": [0,-4,-3],
                "GENBOOK": [0,-3,-2],
                "BOOK": [0,-3,-4],
                "READALOUD": [0,-6,-1]

            },

        };
        if (this.name in this.config['languages']){
            //merge existing config with defaults
            obj = Object.assign({}, obj, this.config['languages'][this.name]);
        }
        this.config['languages'][this.name] = obj;

        this.funcdict["PAUSE"] = (cls, sequence, words) => {
            console.log("base pause", sequence, words);
            return 0; //no action, just a generic keypress
        }
        this.funcdict["GENERATE"] = this.generate;
        this.funcdict["HIGHLIGHT"] = (cls, sequence, words) => { 
            console.log("base highlight", cls.highlight);
            cls.highlight = !cls.highlight; 
            return 0; //no action, just a generic keypress
        };
        this.funcdict["READALOUD"] = (cls, sequence, words) => {
            console.log("base readaloud", sequence, words);
            const mySettings = vscode.workspace.getConfiguration('mrrubato');	
            let toreadaloud = !mySettings.get('readaloud', false);
            if (toreadaloud){
                vscode.commands.executeCommand('workbench.action.chat.nextCodeBlock');
                vscode.commands.executeCommand('workbench.action.chat.readChatResponseAloud');
            }
            else{
                vscode.commands.executeCommand('workbench.action.chat.open', "@mr /stop");            
            }
            mySettings.update(
                    'readaloud', 
                    toreadaloud, 
                    vscode.ConfigurationTarget.Global // Saves to User settings
                );
            return 0; //no action, just a generic keypress
        };
        this.funcdict["HOME"] = this.home;
        this.funcdict["END"] = this.end;
        this.funcdict["PGUP"] = this.pgup;
        this.funcdict["PGDN"] = this.pgdn;
        this.funcdict["UP"] = this.up;
        this.funcdict["DOWN"] = this.down;
        this.funcdict["LEFT"] = this.left;
        this.funcdict["RIGHT"] = this.right;
        this.funcdict["GENBOOK"] = this.genbook;
        this.funcdict["BOOK"] = this.book;

    }

    genbook(cls, sequence, words){
        console.log("base genbook", sequence, words);
        //bring to front genbook for current time detected..
        // +- selection
        var shift = 0;
        if (sequence.length > 0) {
            shift = sequence[sequence.length - 1] - this.keybot;
        }

        return 0; //no action, just a generic keypress
    }

    book(cls, sequence, words){
        console.log("base book", sequence, words);
        //bring to front book for current time detected.  
        var shift = 0;
        // +/- selection
        if (sequence.length > 0) {
            shift = sequence[sequence.length - 1] - this.keybot;
        }
        return 0; //no action, just a generic keypress
    }

    pause(cls, sequence, words){
        console.log("base pause", sequence, words);
        vscode.commands.executeCommand('workbench.action.chat.open', "@mr /stop");
        return 0; //no action, just a generic keypress
    }
    generate(cls, sequence, words){
        console.log("base generate", sequence, words);
        vscode.commands.executeCommand('mrrubato.mytutor.generate'); //no params, just generate from current cursor location..
        return 0; //no action, just a generic keypress
    }

    home(cls, sequence, words){        
        console.log("base home", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'wrappedLineStart',
            by: 'wrappedLine',
            select: cls.highlight,
            value: 1
        });

        return 0; //no action, just a generic keypress        
    }

    end(cls, sequence, words){
        console.log("base end", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'wrappedLineEnd',
            by: 'wrappedLine',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    pgup(cls, sequence, words){
        console.log("base pgup", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'up',
            by: 'page',
            select: cls.highlight,
            value: 25
        });
        return 0; //no action, just a generic keypress
    }

    pgdn(cls, sequence, words){
        console.log("base pgdn", sequence, words);
        console.log(cls.highlight);
//        console.log(this.highlight);
        try {
            vscode.commands.executeCommand('cursorMove', {
                to: 'down',
                by: 'page',
                select: cls.highlight,
                value: 25
            });
        } catch (error) {
            console.error("Error executing scrollPageDown for pgdn:", error);
        }
        return 0; //no action, just a generic keypress
    }

    up(cls, sequence, words){
        console.log("base up", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'up',
            by: 'line',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    down(cls, sequence, words){
        console.log("base down", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'down',
            by: 'line',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    left(cls, sequence, words){
        console.log("base left", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'left',
            by: 'character',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    right(cls, sequence, words){
        console.log("base right", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'right',
            by: 'character',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }



    act(cmd, sequence, words){
        console.log("base act", cmd, sequence, words);
        if (cmd in this.funcdict){
            let func = this.funcdict[cmd];
            if (sequence.length ===1 && sequence[0] === this.keybot+this.keyoffset){
                return func(this, [], words); //no parameters
            }
            else if (sequence.length > 1 && JSON.stringify(sequence.slice(-2)) === JSON.stringify([this.keybot+this.keyoffset, this.keybot+this.keyoffset])){
                return func(this, sequence.slice(0, -2), words);
            }
            else{
                return 1; //more keys needed
            }

        }
        else{
            console.log("base unknown command", cmd);
            return -1; //unknown command
        }
    }

    word(sequence, words=[]){
        let cmd = "";
        let sl = sequence.length;
        let strsl = sl.toString();
        let asequence = sequence.map(x => x-this.keybot-this.keyoffset); //0-adjusted sequence 
        if (strsl in this.config['languages'][this.name]){
            for (const [key, value] of Object.entries(this.config['languages'][this.name][strsl])) {
                if (JSON.stringify(value) === JSON.stringify(asequence)){
                    cmd = key;
                    break;
                }
            }
        }
        return cmd;

    }
}