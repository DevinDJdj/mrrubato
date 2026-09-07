import * as vscode from 'vscode';
//import {recentTabs2} from '../extension';

export let recentTabs2: any[];

export default class LANG {

    
    config: Record<string, any> = {};
    keybot: number = 69;
    keymid: number = 60;
    keyoffset: number = 0;
    funcdict: Record<string, Function> = {};
    midwordtree: Record<string, any> = {}; 
    name: string = "base";
    vars: Record<string, any> = {};
    
    recentTabs: any;
    //base specific variables for generic keypresses, selection, and navigation
    //ALLCAPS = vscode handler..
    highlight: boolean = false; //whether to highlight text or not


    constructor(){
        console.log("base language constructor");
    }

    init(config: Record<string, any>): void {
        //optional init function
        console.log("base language init");
        this.config = config || {};
        this.load();
        //recentTabs2 is imported from the extension

    }

    load(): void {
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
                "READALOUD": [0,-6,-1],
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

        this.funcdict["PAUSE"] = (cls: LANG, sequence: number[], words: string[]) => {
            console.log("base pause", sequence, words);
            return 0; //no action, just a generic keypress
        };
        this.funcdict["GENERATE"] = this.generate;
        this.funcdict["HIGHLIGHT"] = (cls: LANG, sequence: number[], words: string[]) => { 
            console.log("base highlight", cls.highlight);
            cls.highlight = !cls.highlight; 
            return 0; //no action, just a generic keypress
        };
        this.funcdict["READALOUD"] = (cls: LANG, sequence: number[], words: string[]) => {
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


    async tab_(sequence: number[], words: string[]) {
//        await import('../extension.ts').then(({ recentTabs2 }) => {
//        });
        /*
        if (sequence.length === 0){
            const visibleEditors: readonly vscode.TextEditor[] = vscode.window.visibleTextEditors;
            const folderUri = vscode.workspace.workspaceFolders[0].uri;
            const tabNames = visibleEditors.map(editor => editor.document.uri.path.replace(folderUri.path + "/", ""));

            let tabs = {'num': visibleEditors.length, 'numrecent': recentTabs2.length, 'tabIndex': 0, 'selectedTab': 0};
            tabs['tabs'] = visibleEditors.map((editor, index) => {return {uri: editor.document.uri, name: tabNames[index]}; });
            //fname = fname.replace(folderUri.path + "/", ""); //remove the folder path from the file name for display purposes.            
            //get readable name for display.. or for now just add to chat $$0=..

            this.vars['tabs'] = tabs;
            this.vars['useRecentTabs'] = false;


            //how to display selection entries in vscode?  
            return 1;
        }
        if (sequence.length >0 && sequence[0] === this.keymid){
            //use recentTabs..
            this.vars['useRecentTabs'] = true;
        }
        if (sequence.length > 0){
            let selectedTab = sequence[sequence.length - 1] - this.keymid;
            this.vars['tabs']['selectedTab'] += selectedTab;
            if (this.vars['useRecentTabs']){
                // handle recent tabs selection
                if (selectedTab >= 0 && selectedTab < recentTabs2.length){
                    let tempIndex = selectedTab;
                    console.log("Selected recent tab index:", tempIndex);
                    console.log("Selected recent tab:", recentTabs2[tempIndex]['name']);
                }
                else{
                    console.log("Selected recent tab index out of range:", selectedTab);
                }
            }
            if (this.vars['tabs']['tabIndex'] + this.vars['tabs']['selectedTab'] >= 0 && this.vars['tabs']['tabIndex'] + this.vars['tabs']['selectedTab'] < this.vars['tabs']['tabs'].length){
                let tempIndex = this.vars['tabs']['tabIndex'] + this.vars['tabs']['selectedTab'];
                //show this tab, refresh display..
                console.log("Selected tab index:", tempIndex);
                console.log("Selected tab:", this.vars['tabs']['tabs'][tempIndex]['name']);
//                vscode.window.showTextDocument(this.vars['tabs']['tabs'][tempIndex]['uri']);
//                this.vars['tabs']['tabIndex'] += this.vars['selectedTab'];
            }


            //highlight/indicate selected visually..



        }
            */
    }

    async tab(sequence: number[], words: string[]) {
        /*
        if (this.vars['tabs']['useRecentTabs']){
            let tempIndex = Math.abs(this.vars['tabs']['selectedTab']); //allow bidirectional for now.. only able to select up to 12..
            if (tempIndex >= 0 && tempIndex < recentTabs2.length){
                this.vars['tabs']['selectedTab'] = 0;
                console.log("Selected recent tab index:", tempIndex);
                console.log("Selected recent tab:", recentTabs2[tempIndex]['name']);
                vscode.window.showTextDocument(recentTabs2[tempIndex]['uri']); //this will trigger it to be at top of recentTabs..
            }
        }
        else{
            let tempIndex = this.vars['tabs']['tabIndex'] + this.vars['tabs']['selectedTab'];
            if (tempIndex >= 0 && tempIndex < this.vars['tabs']['tabs'].length){
                this.vars['tabs']['tabIndex'] += this.vars['tabs']['selectedTab'];
                this.vars['tabs']['selectedTab'] = 0;
                console.log("Selected tab index:", tempIndex);
                console.log("Selected tab:", this.vars['tabs']['tabs'][tempIndex]['name']);
                vscode.window.showTextDocument(this.vars['tabs']['tabs'][tempIndex]['uri']);
            }
        }
            */
    }    

    genbook(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base genbook", sequence, words);
        //bring to front genbook for current time detected..
        // +- selection
        var shift = 0;
        if (sequence.length > 0) {
            shift = sequence[sequence.length - 1] - this.keybot;
        }

        return 0; //no action, just a generic keypress
    }

    book(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base book", sequence, words);
        //bring to front book for current time detected.  
        var shift = 0;
        // +/- selection
        if (sequence.length > 0) {
            shift = sequence[sequence.length - 1] - this.keybot;
        }
        return 0; //no action, just a generic keypress
    }

    pause(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base pause", sequence, words);
        vscode.commands.executeCommand('workbench.action.chat.open', "@mr /stop");
        return 0; //no action, just a generic keypress
    }
    generate(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base generate", sequence, words);
        vscode.commands.executeCommand('mrrubato.mytutor.generate'); //no params, just generate from current cursor location..
        return 0; //no action, just a generic keypress
    }

    home(cls: LANG, sequence: number[], words: string[]): number {        
        console.log("base home", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'wrappedLineStart',
            by: 'wrappedLine',
            select: cls.highlight,
            value: 1
        });

        return 0; //no action, just a generic keypress        
    }

    end(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base end", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'wrappedLineEnd',
            by: 'wrappedLine',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    pgup(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base pgup", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'up',
            by: 'page',
            select: cls.highlight,
            value: 25
        });
        return 0; //no action, just a generic keypress
    }

    pgdn(cls: LANG, sequence: number[], words: string[]): number {
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

    up(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base up", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'up',
            by: 'line',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    down(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base down", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'down',
            by: 'line',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    left(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base left", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'left',
            by: 'character',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }

    right(cls: LANG, sequence: number[], words: string[]): number {
        console.log("base right", sequence, words);
        vscode.commands.executeCommand('cursorMove', {
            to: 'right',
            by: 'character',
            select: cls.highlight,
            value: 1
        });
        return 0; //no action, just a generic keypress
    }



    act(cmd: string, sequence: number[], words: string[]): number {
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

    word(sequence: number[], words: string[] = []): string {
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