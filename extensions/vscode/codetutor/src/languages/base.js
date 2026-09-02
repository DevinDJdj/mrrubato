
export default class LANG {

    config = {};
    keybot = 69;
    keyoffset = 0;
    funcdict = {};
    midwordtree = {}; 

    name = "base";
    vars = {};
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
                "GENERATE": [0, -1],
                "HIGHLIGHT": [0,1],
                
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
                "TAB": [0,-3,-7], //select tab../select topic..
            },

        };
        if (this.name in this.config['languages']){
            //merge existing config with defaults
            obj = Object.assign({}, obj, this.config['languages'][this.name]);
        }
        this.config['languages'][this.name] = obj;

        this.funcdict["TAB"] = this.tab;
        this.funcdict["TAB_"] = this.tab_;
        this.funcdict["GENERATE"] = this.generate;
        this.funcdict["HIGHLIGHT"] = () => { 
            console.log("base highlight", this.highlight);
            this.highlight = !this.highlight; 
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

    }

    generate(sequence, words){
        console.log("base generate", sequence, words);
        vscode.commands.executeCommand('mrrubato.mytutor.generate'); //no params, just generate from current cursor location..
        return 0; //no action, just a generic keypress
    }

    home(sequence, words){        
        console.log("base home", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'wrappedLineStart',
            by: 'wrappedLine',
            select: this.highlight,
            value: 1
        });

        return 0; //no action, just a generic keypress        
    }

    tab_(sequence, words) {

        if (sequence.length === 0){
            // 1. Get all active tab groups in the window
            const tabGroups = vscode.window.tabGroups.all;
            // 2. Map and flatten the tabs from all groups
            const allTabs = tabGroups.flatMap(group => group.tabs);
            // 3. Extract the information you need (e.g., labels)
            const tabLabels = allTabs.map(tab => tab.label);
            this.vars['tabLabels'] = tabLabels;
            //this could have changed, probably need to search previously selected?  
            if ('tabIndex' in this.vars){
                tabIndex = this.vars['tabIndex'];
            }
            else{
                tabIndex = 0; //default to the first tab if no tabIndex is set
                this.vars['tabIndex'] = tabIndex;
            }

            //how to display selection entries in vscode?  
            return 1;
        }
        if (sequence.length > 0){
            let selectedTab = sequence[sequence.length - 1] - this.keybot;
            this.vars['selectedTab'] = selectedTab;

            //highlight/indicate selected visually..

        }
    }
    tab(sequence, words) {

    }    

    end(sequence, words){
        console.log("base end", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'wrappedLineEnd',
            by: 'wrappedLine',
            select: this.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    pgup(sequence, words){
        console.log("base pgup", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'up',
            by: 'page',
            select: this.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    pgdn(sequence, words){
        console.log("base pgdn", sequence, words);
        try {
            vscode.commands.executeCommand('cursorMove', {
                to: 'down',
                by: 'page',
                select: this.highlight,
                value: 1
            });
        } catch (error) {
            console.error("Error executing cursorMove for pgdn:", error);
        }
        return 0; //no action, just a generic keypress
    }

    up(sequence, words){
        console.log("base up", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'up',
            by: 'line',
            select: this.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    down(sequence, words){
        console.log("base down", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'down',
            by: 'line',
            select: this.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    left(sequence, words){
        console.log("base left", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'left',
            by: 'character',
            select: this.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    right(sequence, words){
        console.log("base right", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'right',
            by: 'character',
            select: this.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }



    act(cmd, sequence, words){
        console.log("base act", cmd, sequence, words);
        if (cmd in this.funcdict){
            let func = this.funcdict[cmd];
            if (sequence.length ===1 && sequence[0] === this.keybot+this.keyoffset){
                return func([], words); //no parameters
            }
            else if (sequence.length > 1 && JSON.stringify(sequence.slice(-2)) === JSON.stringify([this.keybot+this.keyoffset, this.keybot+this.keyoffset])){
                return func(sequence.slice(0, -2), words);
            }
            else{
                if (cmd + "_" in this.funcdict){
                    return this.funcdict[cmd + "_"](sequence, words);
                }
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