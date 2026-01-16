import * as vscode from 'vscode';
import * as Book from './book';
import ollama from 'ollama';
import { profile } from 'console';


interface TerminalWorker {
    name: string; //name of the terminal worker.
    type: string; //type of terminal worker.  CMD, PowerShell, Bash, etc.
    version: string; //version of the terminal worker.
    currentCommand: string; //current command being executed.
    history: string[]; //history of commands executed.
    terminal: vscode.Terminal | undefined; //the terminal instance.
}

export var terminalworkers: {[key: string] : TerminalWorker | undefined} = {};


export var worktopics: string[] = []; //list of topics being worked on.

var selectedworker: TerminalWorker | undefined = undefined;

export function run(command: string, dir: string="") {
    //dir not used yet.  
    let idx = command.indexOf(" "); //assume we have a space after command type.  
    let cmdtype = command.substring(0, idx);
    command = command.substring(idx + 1);
    let version = "";
    if (cmdtype.length > 2){
        version = cmdtype.substring(2); //get version if any.
        if (version[0] === '-'){
            //minus X version
            //not used for now.
            version = version.substring(1); //remove leading dash.
        }
    }
    let worker = selectedworker;
    if (cmdtype.length < 1 && worker === undefined){
        console.log("Invalid terminal command: " + command);
        return;
    }
    else if (cmdtype.length < 1){
        //use selected terminal.
    }
    else{
        if (cmdtype.length === 1){
            //no type specified, use default terminal.
            worker = getTerminalWorker(cmdtype, "", version, dir);
        }
        else if (cmdtype[1] === '$'){
            //focus terminal and run command.
            worker = getTerminalWorker(cmdtype, cmdtype[1], version, dir);
        }
        else if (cmdtype[1] === '>'){
            //focus terminal and run command.
            //run elevated?  
            worker = getTerminalWorker(cmdtype, cmdtype[1], version, dir);
        }
    }

    if (worker === undefined || worker.terminal === undefined){
        console.log("Could not create or find terminal for command: " + command);
        return;
    }
    worker.terminal.show(); //not sure we want to show it here?
    selectedworker = worker; //set as selected worker
    worker.currentCommand = command;
    worker.history.push(command);
    worker.terminal.sendText(command);
//    vscode.commands.executeCommand('workbench.action.terminal.sendSequence', { text: command + "\n" });

}

function getTerminal(key: string, type: string="", version: string="", dir=""): vscode.Terminal | undefined {
    // Iterate through all open terminals
    for (const terminal of vscode.window.terminals) {
        if (terminal.name === key) {
            return terminal; // Return the matching terminal
        }
    }

    //no terminal found with that name.
    //create one with this type.  
    let myprofile = {
        "name": key,
        "shellPath": "C:\\WINDOWS\\System32\\cmd.exe",
        "shellArgs": []
    };


    if (type === '$'){
        myprofile = {
            "name": key,
            "shellPath": "C:\\Windows\\System32\\wsl.exe",

            "shellArgs": ["-d", "Ubuntu-20.04"]
        };
        //for now assume ubuntu. this API not working well, so just do manually..
        /*
        if (allprofiles !== undefined){
            let profilekeys = Object.keys(allprofiles);
            console.log("Available profiles: " + profilekeys.join(", "));
            //find any ubuntu profile.
            for (let pk of profilekeys){
                if (pk.toLowerCase().includes('ubuntu')){
                    myprofile = pk;//allprofiles[pk];
                    myprofilefull = allprofiles[pk];
                    break;
                }
            }
            //find version if specified.
            for (let pk of profilekeys){
                if (pk.toLowerCase().includes('ubuntu') && pk.toLowerCase().includes(version.toLowerCase())){
                    myprofile = pk;//allprofiles[pk];
                    myprofilefull = allprofiles[pk];
                    break;
                }
            }
        }
            */
    }

    console.log("Creating terminal with profile: " + myprofile.name + " Type: " + type + " Version: " + version);

//    return vscode.window.createTerminal(myprofile);
/*
    vscode.commands.executeCommand('workbench.action.terminal.newWithProfile', {
        name: key, 
        profile: myprofile
    });
    */
    return vscode.window.createTerminal(myprofile);


}


export function addClosedTerminalListener() {
    const disposable = vscode.window.onDidCloseTerminal((closedTerminal: vscode.Terminal) => {
        vscode.window.showInformationMessage(`Terminal closed: ${closedTerminal.name}`);
        console.log(`Terminal named "${closedTerminal.name}" closed.`);
        terminalworkers[closedTerminal.name] = undefined; //remove from list.
        // You can also access the exit status of the terminal
        if (closedTerminal.exitStatus !== undefined) {
            console.log(`Exit code: ${closedTerminal.exitStatus.code}, reason: ${closedTerminal.exitStatus.reason}`);
        }
    });
}

export function getTerminalWorker(key: string, type: string="", version: string = "", dir="") : TerminalWorker {
    //for now only use one of each type/version of terminal.  


    if(terminalworkers[key] === undefined){
        //create a new worker.  
        console.log("Creating new terminal worker: " + key + " Type: " + type + " Version: " + version);
        let newworker: TerminalWorker = {
            name: key,
            type: type,
            version: version,
            currentCommand: "",
            history: [], 
            terminal: getTerminal(key, type, version, dir) //check if terminal already exists.
        };

        terminalworkers[key] = newworker;
        //start terminal for worker.    

    }
    if (terminalworkers[key]!.terminal === undefined){
        terminalworkers[key]!.terminal = getTerminal(key, type, version, dir);
    }
    return terminalworkers[key];

}


