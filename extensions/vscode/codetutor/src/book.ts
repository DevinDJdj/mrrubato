import * as vscode from 'vscode';
import { posix } from 'path';

/*
    * Book.ts - This file is part of the GitBook extension for VSCode.
    * It manages the GitBook structure, repositories, and content retrieval.
    * this will be the book used for autocompletion logic and genbook will be used 
    * when creating entries.  
    * This way we keep separate the guidance of this thought and the generated thought.  
    * Not sure if this will chain properly, but at least one-step thought will work I think.  
*/

//**/web/public/git.js pulled originally from here.  
//only need some of this.  

var gitbook = [];
var gitcommits = [];
var selectedgitindex = 0; //which repo are we using?  

var gitstruct = {"bydate": {}, "bytopic": {}, "alltopics": "", "allcontent": {}}; //context holds sequential string.  
var gittoken = null;
var gitcurrentpath = "";
var gitcurrentfolder = "";
var gitcurrentcontents = "";
var gitcurrentbook = "";
var gitcurrentcontentstype = "javascript";
var gitcurrentscrollinfo = null;

const GIT_BOOK = 0; //always get book.  Load from DB eventually.  
const GIT_CODE = 1;
const GIT_DETAILS = 2;
const GIT_RELATIONS = 4;
const GIT_DB = 8;

var gitnature = GIT_CODE | GIT_DETAILS; //do we retrieve history and commits?  

var currenttopic = "NONE";
var selectedtopic = "NONE";
var currenttopicline = 0;
var currentrefline = 0;
var currentref = "NONE";

var selectionhistory = [];
var myCodeMirror = null;
var tempcodewindow = null;
var usetempcodewindow = false;
var definitions = {"REF": "#", "REF2": "##", "TOPIC": "**", "STARTCOMMENT": "<!--", "ENDCOMMENT": "-->", "CMD": ">", "QUESTION": "@@", "NOTE": "--", "SUBTASK": "-"};


//store data as tabs open and close and based on location in the tab.  
//from this info generate the context when querying the model.  
//right now only front-side loading.  Possibly add RAG processing later?  
//need to include some random data in the context to make sure 
//the logic is not circular.  


export function open(context: vscode.ExtensionContext) {
    return getBook();

}


export function read(request: vscode.ChatRequest, context: vscode.ChatContext) {
    //adjust request to include book context needed.  
    return getBook();

}

export function getBook(){
    loadBook();
}

export async function closeFileIfOpen(file:vscode.Uri) : Promise<void> {
    const tabs: vscode.Tab[] = vscode.window.tabGroups.all.map(tg => tg.tabs).flat();
    const index = tabs.findIndex(tab => tab.input instanceof vscode.TabInputText && tab.input.uri.path === file.path);
    if (index !== -1) {
        await vscode.window.tabGroups.close(tabs[index]);
    }
}

async function readFilesInFolder(folder: vscode.Uri): Promise<{ total: number, count: number }> {
    let total = 0;
    let count = 0;
    for (const [name, type] of await vscode.workspace.fs.readDirectory(folder)) {
        //what order does this come in?  Is it alphabetical?
        if (type === vscode.FileType.File) {
            const fileUri = folder.with({ path: posix.join(folder.path, name) });
            vscode.workspace.openTextDocument(fileUri).then((document) => {
                let text = document.getText();
                console.log(`${fileUri.path} ... read`);
                // parse this.  
                loadPage(text);
//                console.log(text);
                // Optionally insert the text into the active editor
        //		insertTextIntoActiveEditor(text);
                closeFileIfOpen(fileUri).then(() => {
                    console.log(`${fileUri.path} ... closed`);
                });
            });
            let filePath = posix.dirname(fileUri.path);
            const stat = await vscode.workspace.fs.stat(folder.with({ path: filePath }));
            total += stat.size;
            count += 1;
        }
    }
    return { total, count };
}


function loadPage(text: string){
    //get the completions from the text.  


}
function loadBook(){
    if (!vscode.workspace.workspaceFolders) {
        return vscode.window.showInformationMessage('No folder or workspace opened');
    }
    //read all files in /book folder and parse them.  
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    // this should be a book path.  Use as you would work on the project.  
    const bookUri = folderUri.with({ path: posix.join(folderUri.path, 'book') });
    const fileUri = folderUri.with({ path: posix.join(folderUri.path, 'book/definitions.txt') });

    readFilesInFolder(bookUri).then((result) => {
        console.log(`Total size: ${result.total} bytes, File count: ${result.count}`);
    });

    
}

