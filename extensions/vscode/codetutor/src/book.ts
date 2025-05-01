import * as vscode from 'vscode';
import { posix, basename } from 'path';


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
var defmap = [{"#": "REF",">": "CMD", "-": "SUBTASK"}, 
    {"##": "REF2", "**": "TOPIC", "@@": "QUESTION", "--": "NOTE", "==": "ANSWER", "$$": "ENV", "!!": "ERROR"}, 
    {"-->": "ENDCOMMENT"}, 
    {"<!--": "STARTCOMMENT"}];



interface BookTopic {
    file: string;
    line: number;
    topic: string;
    data: string;
    date: number; //date in YYYYMMDD format.
    sortorder: number;
}

export var topicarray: {[key: string] : Array<BookTopic> | undefined} = {};
var refarray = [];

let mynow = new Date(); //get the current date in YYYYMMDD format.    

//store data as tabs open and close and based on location in the tab.  
//from this info generate the context when querying the model.  
//right now only front-side loading.  Possibly add RAG processing later?  
//need to include some random data in the context to make sure 
//the logic is not circular.  


export function open(context: vscode.ExtensionContext) {
    return getBook();

}

function getDateFromString(dateString: string): Date {
    if (dateString.length !== 8) {
        return new Date();  // Return current date if the string is not in the expected format
    }
    const year = parseInt(dateString.substring(0, 4), 10);
    const month = parseInt(dateString.substring(4, 6), 10) - 1; // Months are 0-indexed
    const day = parseInt(dateString.substring(6, 8), 10);
    return new Date(year, month, day);
}

function getDaysBetweenDates(startDate : Date, endDate: Date) : number{
    const startTime = startDate.getTime();
    const endTime = endDate.getTime();
    const timeDiff = endTime - startTime;
    const daysDiff = Math.round(timeDiff / (1000 * 60 * 60 * 24));
    return daysDiff;
}

function getRecency(bt : Array<BookTopic>, mydate: Date = new Date()) : number {
    let cumdate = 0;
    for (let i = 0; i < bt.length; i++) {
        //need better calculation of recency.

        //get closest to mydate.  
        cumdate += getDaysBetweenDates(getDateFromString(bt[i].date.toString()), mydate);

        bt[i].sortorder = 0;
    }
    if (bt.length > 0){
        return cumdate / bt.length; //average recency of the topics.
    }
    else{
        return 0;
    }
}



export function read(request: vscode.ChatRequest, context: vscode.ChatContext) {
    //adjust request to include book context needed.  
//    return getBook();
    //only want pertinent context.  
    //latest selections etc.  
    //create sort order for toicarray.  
    //then retrieve topic information.  


    Object.keys(topicarray).forEach((key) => {
        if (topicarray[key] !== undefined) {
            //sort the topics by date.  
            if (topicarray[key].length > 0) {
                topicarray[key][0].sortorder = getRecency(topicarray[key]); //set the sort order to recency.
            }
        }
    });

}

function formatDate(date: Date = new Date()): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}${month}${day}`;
};

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
                loadPage(text, fileUri.path);
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


function getFileName(filePath: string): string {
    //get the date of the file.  
    //get the filename without the extension and path.  
    let myName = posix.basename(filePath);
    return myName; //remove the extension.
}

function getFileDate(filePath: string): number {
    filePath = filePath.split(".")[0]; //remove the extension.
    if (!Number.isNaN(filePath)){
        return Number(filePath); //get the date of the file.  

    }
    return 0;
}

function initTopic(topic: string, data: string){
    if (!(topic in topicarray) || topicarray[topic] === undefined) {
        topicarray[topic] = [];
    }
}

function loadPage(text: string, filePath: string) {
    //get the completions from the text.  
    //each topic or comment should be parsed and added to 
    //completions...
    let filename = getFileName(filePath);

    currenttopic = filename.split(".")[0]; //default topic is the file name.

    if (!(currenttopic in topicarray) || topicarray[currenttopic] === undefined) {
        topicarray[currenttopic] = [];
    }
    let mydate = getFileDate(filename.split(".")[0]); //get the date of the file.    
    let mypage = {"file": filePath, "line": 0, "topic": currenttopic, "sortorder": 0, "date": mydate, "data": ""};
    //adjust sortorder based on order of occurrence for now. 
    let mytopic = {"file": filePath, "line": 0, "topic": currenttopic, "sortorder": 0, "date": mydate, "data": ""};
    let strs = text.split("\n");
    let tkey = "FILESTART";
    for (let i=0; i<strs.length; i++) {
        let str = strs[i].trim();

        mypage.data += str + "\n"; //add to current page data.

        keyfind: for (let j=defmap.length-1; j>=0; j--) {
            for (const [key, val] of Object.entries(defmap[j])) {
                if (str.startsWith(key)) {
                    let type = val;
                    if (type === "TOPIC") {

                        initTopic(tkey, str); //if doesnt exist, add.  

                        topicarray[tkey]?.push(mytopic); //add the previous topic to the array.
                        tkey = str.slice(j+1);
                        let myorder = 0;
                        myorder = topicarray[tkey]?.length || 0; //get the current order of the topic.


                        mytopic = {"file": filePath, "line": i, "topic": tkey, "sortorder": myorder, "date": mydate, "data": ""};
                        //adjust sortorder based on order of occurrence for now. 

                        currenttopic = tkey;
                        

                        break keyfind;
                    }
                }
            }


        }

    }

    topicarray[currenttopic]?.push(mytopic);
    topicarray[mydate.toString()]?.push(mypage);       
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

    topicarray = {};   //reset topic array.
    readFilesInFolder(bookUri).then((result) => {
        console.log(`Total size: ${result.total} bytes, File count: ${result.count}`);
        console.log(topicarray);
        //add this to our CompletionItemProvider.   

    });


    
}

