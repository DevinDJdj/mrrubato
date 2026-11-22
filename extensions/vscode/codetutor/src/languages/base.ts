import * as vscode from 'vscode';
//import {recentTabs2} from '../extension';
//import { currentfunctions } from '../book.js';
//import * as MyKeys from '../midi/mykeys';


export let currentfunctions: any[] = ["Hello"];
export let recentTabs2: any[];


export class selector {
    array: any[];
    currentindex: number;
    browseindex: number;
    selected: number;
    lastkey: number;

    constructor(array: any[], currentindex: number = 0) {
        this.array = array;
        this.currentindex = currentindex;
        this.browseindex = 0;
        this.selected = 0;
        this.lastkey = 0;
    }

    preselect(selected: number): any {
        console.log(`Preselect called with: ${selected}`);
        if (this.lastkey === selected) {
            console.log(`Last key matched: ${selected}`);
            this.selected += selected;
            if (this.selected + this.currentindex < 0) {
                this.selected = -this.currentindex;
            } else if (this.selected + this.currentindex >= this.array.length) {
                this.selected = this.array.length - 1 - this.currentindex;
            }
            return this.array[this.currentindex + this.selected];
        }

        this.lastkey = selected;

        if (selected + this.selected + this.currentindex < 0) {
            selected = -(this.currentindex + this.selected);
        } else if (selected + this.selected + this.currentindex >= this.array.length) {
            selected = this.array.length - 1 - (this.currentindex + this.selected);
        }

        return this.array[this.currentindex + this.selected + selected] ?? null;
    }

    select(selected?: number | null): any {
        let ret: any;

        if (selected !== undefined && selected !== null) {
            ret = this.preselect(selected);
        } else {
            console.info(`${this.currentindex + this.selected} in ${this.array}`);
            ret = this.array && this.array.length > 0 ? this.array[this.currentindex + this.selected] : null;
        }

        this.currentindex += this.selected;
        this.selected = 0;
        return ret;
    }

    get_visible(): any[] {
        const start = Math.max(0, this.currentindex + this.selected - 11);
        const end = Math.min(this.currentindex + this.selected + 13, this.array.length);
        return [...this.array.slice(start, end)].reverse();
    }

    get_vars(vars: Record<string, any>, entry: string = '**'): void {
        let start = 0;
        if (this.array.length < 12) {
            start = 12 - this.array.length + this.currentindex + 1;
            vars['idx'] = this.currentindex;
            vars[':'] = this.currentindex;
        } else {
            vars['idx'] = this.currentindex+this.selected;
        }

        for (const [i, value] of this.get_visible().entries()) {
            const n = i + start;
            if (typeof value === 'object' && value !== null && entry in value) {
                if (entry === '..') {
                    if ('$$' in value) {
                        const details = value['$$'] as Record<string, any>;
                        const prefix = '..' in details ? details['..'] : (('TIME' in details) ? details['TIME'] : '...');
                        const cmd = '&&' in value ? value['&&'] : '&&';
                        const text = '&&' in details ? details['&&'] : (('TEXT' in details) ? details['TEXT'] : '&&');
                        vars[String(n)] = `${prefix} ${cmd} ${text}`;
                    }
                } else {
                    vars[String(n)] = value[entry as keyof typeof value];
                }
            } else {
                vars[String(n)] = value;
            }
        }
    }
}


export default class LANG {


    config: Record<string, any> = {};
    keybot: number = 69;
    keymid: number = 60;
    keyoffset: number = 0;
    func: string = "";
    funcdict: Record<string, Function> = {};
    midwordtree: Record<string, any> = {}; 
    name: string = "base";
    vars: Record<string, any> = {};
    recentTabs: any;
    tabselector: selector | null = null;
    functionselector: selector | null = null;
    mykeys: any = null;
    //base specific variables for generic keypresses, selection, and navigation
    //ALLCAPS = vscode handler..
    highlight: boolean = false; //whether to highlight text or not
    transcript: string = "";


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
                "GIT FUNCTION": [0,-6,-5],
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
                "TAB": [0,-4,-7], //select tab../select topic..
            },

        };
        if (this.name in this.config['languages']){
            //merge existing config with defaults
            obj = Object.assign({}, obj, this.config['languages'][this.name]);
        }
        this.config['languages'][this.name] = obj;

        this.funcdict["TAB"] = this.tab;
        this.funcdict["TAB_"] = this.tab_;

        this.funcdict["GIT FUNCTION_"] = (cls: LANG, sequence: number[], words: string[]) => {
            this.func = "GIT FUNCTION_";
            console.log("base git function_", sequence, words);
            //send 
            let myfunc = null;
            let vars = {};
            if (sequence.length === 0){
                let selections = this.mykeys.getFunctions().map((func, index) => {return {'**': func.name, ':': func.location.range.start, 'len': func.location.range.end - func.location.range.start}; });
                this.functionselector = new selector(selections, 0);                            
            }
            else if (sequence[sequence.length - 1] === this.keybot) {
                //just skip keybot.. no selection here..
                return 1;
            }
            else{
                let select = this.keymid - sequence[sequence.length - 1];
                myfunc = this.functionselector.preselect(select);
                if (myfunc){
                    vars['function'] = myfunc['**'];
                    vars['line'] = myfunc[':'];
                    vars['funlen'] = myfunc['len'];
                }
            }
            this.functionselector.get_vars(vars);
            let str = this.mykeys.transcriber.write(this.name, this.func, (vars), null, false);
            this.transcript = str;


            return 1; //no action, just a generic keypress
        };

        this.funcdict["GIT FUNCTION"] = (cls: LANG, sequence: number[], words: string[]) => {
            console.log("base git function", sequence, words);
            console.log(this.mykeys.getFunctions()); // Assuming mykeys is imported and available
            let select = this.keymid - sequence[sequence.length - 1];
            let myfunc = this.functionselector.select(select);
            let vars = {};
            if (myfunc){
                vars['function'] = myfunc['**'];
                vars['line'] = myfunc[':'];
                vars['funlen'] = myfunc['len'];
            }
            this.functionselector.get_vars(vars);
            let str = this.mykeys.transcriber.write(this.name, this.func, (vars), null, false);
            this.transcript = str;
            //write to book..
            this.mykeys.appendToBook('--' + myfunc['**'] + "\n");


            return 0; //no action, just a generic keypress
        };

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
        //use this.mykeys.
//        await import('../extension.ts').then(({ recentTabs2 }) => {
//        });
        if (sequence.length === 0){
            this.vars['tabs'] = recentTabs2;
            this.vars['useRecentTabs'] = true;
            this.tabselector = new selector(recentTabs2, 0);

            //how to display selection entries in vscode?  
            return 1;
        }else if (sequence[sequence.length - 1] === this.keybot) {
            //just skip keybot.. no selection here..
            return 1;
        }
        if (sequence.length >0 && sequence[0] === this.keymid){
            //use recentTabs..
            this.vars['useRecentTabs'] = false;
            //get all tabs..
            const visibleEditors: readonly vscode.TextEditor[] = vscode.window.visibleTextEditors;
            const folderUri = vscode.workspace.workspaceFolders[0].uri;
            const tabNames = visibleEditors.map(editor => editor.document.uri.path.replace(folderUri.path + "/", ""));

            let tabs = {'num': visibleEditors.length, 'numrecent': recentTabs2.length, 'tabIndex': 0, 'selectedTab': 0};
            tabs['tabs'] = visibleEditors.map((editor, index) => {return {'#': editor.document.uri, '**': tabNames[index]}; });
            //fname = fname.replace(folderUri.path + "/", ""); //remove the folder path from the file name for display purposes.            
            //get readable name for display.. or for now just add to chat $$0=..
            //how do we sort..
            this.tabselector = new selector(tabs['tabs'], 0);

        }
        if (sequence.length > 0){
            let select = this.keymid - sequence[sequence.length - 1];

            let mytab = null;
            mytab = this.tabselector.preselect(select);
            console.log('useRecentTabs:', this.vars['useRecentTabs']);
            // handle recent tabs selection
            console.log("Selected recent tab index:", mytab);
            console.log("Selected recent tab:", mytab['**']);
            //do we select in vscode here?  Or just show selection in trey..
            //vscode.window.showTextDocument(mytab['#']); //show the selected tab in the editor
//                vscode.window.showTextDocument(this.vars['tabs']['tabs'][tempIndex]['uri']);


            //highlight/indicate selected visually..



        }
    }

    async tab(sequence: number[], words: string[]) {
        let select = this.keymid - sequence[sequence.length - 1];
        let mytab = this.tabselector.select(select);
        console.log('useRecentTabs:', this.vars['tabs']['useRecentTabs']);
        vscode.window.showTextDocument(mytab['#']); //this will trigger it to be at top of recentTabs..
        this.mykeys.selectTopic(mytab['#'].fsPath); //this fileURI should get transformed.  

            
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
                //we have a partial command function..
                //execute it..
                if (cmd + "_" in this.funcdict){
                    let func = this.funcdict[cmd + "_"];
                    return func(this, sequence, words);
                }
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