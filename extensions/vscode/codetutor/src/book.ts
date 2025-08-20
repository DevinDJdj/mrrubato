import * as vscode from 'vscode';
import { posix, basename } from 'path';
import * as tokenizer from './tokenizer'; // Import the Token interface
import * as  Worker from './worker'; // Import the Worker class

import { LocalIndex } from 'vectra';
import ollama from 'ollama';
import * as fs from 'fs';
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

export const GIT_BOOK = 0; //always get book.  Load from DB eventually.  
export const GIT_CODE = 1;
export const GIT_DETAILS = 2;
export const GIT_RELATIONS = 4;
export const GIT_DB = 8;

export const BOOK_OPEN_FILE = 1;
export const BOOK_OPEN_WEB = 2;
export const BOOK_OPEN_GIT = 4;

var opennature = BOOK_OPEN_FILE; //how do we open the book page?  File, web, git.

var gitnature = GIT_CODE | GIT_DETAILS; //do we retrieve history and commits?  

export var currenttopic = "NONE";
export var selectedtopic = "NONE";
var currenttopicline = 0;
var currentrefline = 0;
var currentref = "NONE";

export var selectionhistory = [];
export var environmenthistory = [];


var myCodeMirror = null;
var tempcodewindow = null;
var usetempcodewindow = false;
var definitions = {"REF": "#", "REF2": "##", "TOPIC": "**", "STARTCOMMENT": "<!--", "ENDCOMMENT": "-->", "CMD": ">", "QUESTION": "@@", "NOTE": "--", "SUBTASK": "-"};
//have to include >, -> to get to -->
//have to include -, --, !-- to get to <!--


function fnEnv(lines : Array<Array<tokenizer.Token>>, currentindex: number)  {
    //this will be used to create a token for the environment variable.  
    //look at the tokens and take proper action.  
    if (currentindex === 0){
        //parse the command.  
        //if currentindex+1 is -
        //if currentindex+1 is +
        //if currentindex+1 is ID
        //if currentindex+1 is **
    }
    //return completion or error message if misformatted.  
    return "ENV ";
}
function fnTopic(lines : Array<Array<tokenizer.Token>>, currentindex: number)  {
    return "TOPIC ";
}

function fnWork(lines : Array<Array<tokenizer.Token>>, currentindex: number)  {
    //this will be used to create a token for the environment variable.  
    //look at the tokens and take proper action.  
    if (currentindex === 0){
        //parse the command.  
        //if currentindex+1 is -
        //if currentindex+1 is +
        //if currentindex+1 is ID
        //if currentindex+1 is **
    }
    //return completion or error message if misformatted.  
    return "WORK ";
}

export var defmap = [{"#": "REF",">": "CMD", "-": "SUBTASK", "@": "USER"}, 
    {"##": "REF2", "**": "TOPIC", "@@": "QUESTION", "->": "DGRAPH", "--": "NOTE", "==": "ANSWER", "$$": "ENV", "!!": "ERROR", "%%": "WORKER"}, 
    {"-->": "ENDCOMMENT", "!--": "ERRORNOTE" }, 
    {"<!--": "STARTCOMMENT"}];

export var fnmap = {"$$": fnEnv, "%%": fnWork, "**": fnTopic};
//do we want slash?  
export var defstring = "~!@#$%^&*<>/:;-+=";


export interface BookTopic {
    file: string;
    line: number;
    topic: string;
    data: string;
    date: number; //date in YYYYMMDD format.
    sortorder: number;
}


export var vectrafixes: {[key: string] : boolean } = {};

export var alltopics: string[] = [];
export var alltopicsa: string[] = [];

export var envarray: {[key: string] : string} = {}; //environment variables.

export var topicarray: {[key: string] : Array<BookTopic> | undefined} = {};

var bookvectorFolder = "vecbook"; //this will be used to store the book vector folder.
//no sharding for now, but perhaps shard per time period.  
export var topicvectorarray: {[key: string] : LocalIndex | undefined} = {};

export var temptopics: string[] = [];
export var temptopicarray: {[key: string] : Array<BookTopic> | undefined} = {};

export var commandarray: {[key: string] : Array<BookTopic> | undefined} = {};

export var arrays: {[key: string] : {[key: string] : Array<BookTopic> | undefined}} = {};
//this will look like arrays[">"]["TOPIC"] = ...

var refarray = [];

let mynow = new Date(); //get the current date in YYYYMMDD format.    

let NEXT_TERM_ID = 1;

export let MAX_SELECTION_HISTORY = 10; //max number of topics to keep in history.

var bookgraph = {}; //store topic relationships.  

let topicchanged = false;
//store data as tabs open and close and based on location in the tab.  
//from this info generate the context when querying the model.  
//right now only front-side loading.  Possibly add RAG processing later?  
//need to include some random data in the context to make sure 
//the logic is not circular.  

function getDigraph(topic, templist, depth=12){
    let str = "";
    if (!(topic in bookgraph)){
      bookgraph[topic] = {};
      bookgraph[topic][topic] = 1;
    }
    else{
      bookgraph[topic][topic] += 1; //self is just a counter.  Not for weight calculation.  
      if (topic === "web/public/page.html"){
        let j=0;
      }
    }
    for (let i=0; i<templist.length; i++){
      if (!(templist[i] in bookgraph[topic])){
        bookgraph[topic][templist[i]] = depth-i;
      }
      else{
        if (templist[i] !== topic){
          bookgraph[topic][templist[i]] += depth-i;
        }
      }
    }
  }
  
  function buildTopicGraph(start, end, depth=6){
    //create digraph structure.  
    //calculate weights and structure.  
    //array[topic][topic] = weight
    //bookgraph, gitgraph
    //load by date
    //bookgraph
    console.log(start);
    console.log(end);
    var dstart = parseInt(start);
    var dend = parseInt(end);
    let bookstr = "";
    bookgraph = {};
    let counter = 0;
    let templist = [];
    //not most efficient, but for now this will work.
    for (const [key, value] of Object.entries(topicarray)) {
        for (let j=0; j<value.length; j++){
            if (value[j].date >= dstart && value[j].date <= dend){
                templist.push(value[j].topic);
                if (templist.length > depth){
                    //create first and shift.  
                    let topic = templist.shift();
                    getDigraph(topic, templist);
                }
            }
        }
    }
  
    while (templist.length > 0){
      let topic = templist.shift();
      getDigraph(topic, templist);
    }
  
  
  }
  



export function logCommand(command: string) {
    //log the command in genbook.  
    try {
        const mySettings = vscode.workspace.getConfiguration('mrrubato');	
        let genbookFolder = mySettings.genbookfolder;
    
        let logPath = genbookFolder + "/" + formatDate(mynow) + ".txt"; //get the date in YYYYMMDD format.
        updatePage(logPath, command, -1, -1);
    }
    catch (error) {
        console.error(`Error reading file: ${error}`);
    }

}

export function getTokens(str: string): Array<Array<tokenizer.Token>> {
    return tokenizer.tokenize(str);

//    return [];
}
export function executeTokens(tokens: Array<Array<tokenizer.Token>>, topic: string = "NONE"): string {
    return tokenizer.execute(tokens, topic);
}

export function getCommandType(str: string) : [string, string] {
    if (str.length < 2){
        return ["", ""];
    }
    else{
        return [str.charAt(0), str.charAt(1)]; //get the first two characters of the string for now.
    }

}

export function open(context: vscode.ExtensionContext) {
    return getBook(context);


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

export function findTopicsCompletion(str: string = "") : string[]{
    let myarray = [];
    let sortText = "0000";
    if (str === ""){
        for (const [key, value] of Object.entries(topicarray)) {
            if (value !== undefined && value.length > 0) {
                let ci = new vscode.CompletionItem(key, vscode.CompletionItemKind.Text);
                ci.detail = `**${key}`;
                let doc = "";
                sortText = "0000";
                for (let item of value) {
                    doc += `Line: ${item.line}, Sort: ${value[0].sortorder}  \n`;
                    doc += `Link: [${item.file}](${item.file}#L${item.line})  \n`;
                    let data = item.data.substring(0, 255);
                    //add formatting here for timestamp and OCR if available.  
                    doc += `Data: ${data}  \n`;
                    //set sortText to top if it is in selection history.  
                    const found = selectionhistory.findIndex((t) => t === item.topic);
                    if (found > -1){
                        sortText = (MAX_SELECTION_HISTORY-found).toString(16).padStart(4, '0').toUpperCase();
                    }
                    
                }
                ci.documentation = new vscode.MarkdownString(`${doc}`);
                if (sortText === "0000"){
                    sortText = value[0].sortorder.toString(16).padStart(4, '0').toUpperCase();
                }
                ci.sortText = sortText;
                myarray.push(ci);
            }                    
        }
        return myarray;
    }
    else{
        let firstchar = str.substring(2,3);
        let retarray = [];
        let linePrefixFull = str.substring(2);
        for (let i=0; i<alltopicsa.length; i++) {
            if (alltopicsa[i] === firstchar){
                //this is the first one.  
                for (let j=i; j<alltopics.length; j++) {
                    let key2 = alltopics[j];
                    if (key2.startsWith(linePrefixFull) && retarray.find((topic) => topic === key2) === undefined) {
                        retarray.push(key2);

                    }
                    else{
                        break; //stop looking.  We are sorted.
                    }
                }
            }

        }
        getTempTopicsFromPath(linePrefixFull);
        //add what we have found in the temp topic array.  
        for (let i=0; i<temptopics.length; i++) {

            //this needs relative path to work.  
            let key = temptopics[i];
            if (key.startsWith(linePrefixFull)) {
                retarray.push(key);
            }
        }
        adjustSort(retarray);

        for (let i=0; i<retarray.length; i++) {
            let key = retarray[i];
            if ((topicarray[key] !== undefined && topicarray[key].length > 0))  {
                let ci = new vscode.CompletionItem(key.substring(linePrefixFull.length), vscode.CompletionItemKind.Text);
                ci.detail = `**${key}`;
                let doc = "";
                for (let item of topicarray[key]) {
                    doc += `Line: ${item.line}, Sort: ${item.sortorder}  \n`;
                    doc += `Link: [${item.file}](${item.file}#L${item.line})  \n`;
                    let data = item.data.substring(0, 255);
                    doc += `Data: ${data}  \n`;

                }
                ci.documentation = new vscode.MarkdownString(`${doc}`);
                ci.sortText = topicarray[key][0].sortorder.toString(16).padStart(4, '0').toUpperCase();
                myarray.push(ci);
            }                    
            else{
                //temp topic.  
                let ci = new vscode.CompletionItem(key.substring(linePrefixFull.length), vscode.CompletionItemKind.Text);
                ci.detail = `**${key}`;
                //get file path.  
                let filename = getUri(key);
                let doc = "";
                doc += `File: ${key}, Line: 0, Sort: 0\n`;
                //dont specify line number.  Open where we were.  
                doc += `Link: [${key}](${filename.path})\n`; 

                ci.documentation = new vscode.MarkdownString(`${doc}`);
                //set to end of list.  
                let tempsort = 65535;
                ci.sortText = tempsort.toString(16).padStart(4, '0').toUpperCase();
                myarray.push(ci);

            }
        }

        return myarray;
    }

}
export function findInputTopics(inputString : string) : string[]{
    // Create a regex pattern to match double asterisks and capture the text after them
    //need to add newline at start.  
    const matches = inputString.matchAll(/\*\*/g);
    let ret = [];
    for (const match of matches) {
        if (match.index !== undefined && match.index > 0) {
            let end = inputString.indexOf(' ', match.index);
            if (end === -1) {
                end = inputString.length; // If no space found, take the rest of the string
            }
            ret.push(inputString.substring(match.index+2, end));
        
        }
    }
    
    return ret;
}
  
export async function getTempTopicsFromPath(path: string) : Promise<Array<string>> {
    //get the file name from the path.  
    //this will be used to get the file name from the path.  

    try{
        let topics = await readFileNamesInFolder(path);
        //create new entries in the topicarray.
        //these should be relative paths now.  
        for (let i=0; i<topics.length; i++) {
            let mytopic = topics[i];
            const found = temptopics.find((topic) => topic === mytopic);
            if (!found) {
                temptopics.push(mytopic); //add the topic to the array.
            }
        }
        return topics;
    }
    catch (error) {
        console.error(`Error reading file: ${error}`);
        return [];
    }
}
export function adjustSort(array: Array<string>) {
    //go through topicarray
    //and adjust the sort order based on the date.
    //and other things.  

}

//do we want to reset all here?  
//for now the book isnt large enough to worry about this type of performance.  But...
function sortArray(array: {[key: string] : Array<BookTopic> | undefined}, typekey='')  {
    if (typekey===''){
        alltopics = []; //reset all topics.
        alltopicsa = []; //reset all topics.
    }

    Object.keys(array).forEach((key) => {
        if (array[key] !== undefined) {
            //sort the topics by date.  
            if (array[key].length > 0) {
                array[key][0].sortorder = getRecency(array[key]); //set the sort order to recency.
            }
        }
        alltopics.push(key);
        alltopicsa.push(key.substring(0,1)); //add the first character of the topic to the array.
    });

}

export function printENV(){
    for (let i=0; i<environmenthistory.length; i++) {
        console.log("$$" + environmenthistory[i] + " = " + envarray[environmenthistory[i]]);
    }

}

export function removeFromEnvironment(str: string) {
    //remove the topic from the environment.  
    const found = environmenthistory.findIndex((t) => t === str);
    if (found > -1){
        environmenthistory.splice(found, 1); //remove the topic from the selection history.
    }
    delete envarray[str]; //remove the value from the environment array.
}

export function addToEnvironment(str: string, value: string) {
    //add the topic to the environment.  
    const found = environmenthistory.findIndex((t) => t === str);
    if (found < 0){
        environmenthistory.push(str); //add the topic to the selection history.
    }
    else{
        environmenthistory.splice(found, 1); //remove the topic from the selection history.
        environmenthistory.push(str); //add the topic to the end of the selection history.
    }
    envarray[str] = value; //update the value in the environment array.
    if (environmenthistory.length > MAX_SELECTION_HISTORY*2) {
        environmenthistory.shift(); //remove the first element from the array.
    }        
}

export function removeFromHistory(topic: string){
    const found = selectionhistory.findIndex((t) => t === topic);
    if (found > -1){
        selectionhistory.splice(found, 1); //remove the topic from the selection history.
    }

}

export function addToHistory(topic: string){
    //add the topic to the history.  
    const found = selectionhistory.findIndex((t) => t === topic);
    if (found < 0){
        selectionhistory.push(topic); //add the topic to the selection history.
    }
    else{
        selectionhistory.splice(found, 1); //remove the topic from the selection history.
        selectionhistory.push(topic); //add the topic to the end of the selection history.
    }
    if (selectedtopic !== topic) {
        selectedtopic = topic; //set the selected topic to the current topic.
        topicchanged = true; //set the topic changed flag to true.
    }
    if (selectionhistory.length > MAX_SELECTION_HISTORY) {
        selectionhistory.shift(); //remove the first element from the array.
    }    
}

function getWebviewContent(topic: string): string {
    //get all book content with links to files in the digraph.  
    //use the digraph we have already built here.  

    return "Web Book for " + topic;    
}

function webBook(topic: string){
    //this will be used to get the web book for the topic.  
    //this will be used to get the web book for the topic.  
    //for now just return the topic.  
    //later we will get the web book from the server.  
      // Create and show panel
      /*
      const panel = vscode.window.createWebviewPanel(
        topic,
        topic,  // Title of the panel
        vscode.ViewColumn.One,
        {}
      );

      // And set its HTML content
      panel.webview.html = getWebviewContent(topic);
      */

      //for now just open externally.  
      const mySettings = vscode.workspace.getConfiguration('mrrubato');	

      //analyze the topic web external link.  
      vscode.env.openExternal(vscode.Uri.parse(mySettings.webbookurl + topic)); //open the web book in the browser.

}

export function select(topic: string, open: number = opennature) : boolean {
    //select the topic from the topicarray.  
    //this will be used to get the topic from the array.  
    let fname = topic.trim();
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    // this should be a book path.  Use as you would work on the project.  
    const fileUri = folderUri.with({ path: posix.join(folderUri.path, fname) });
//	const fileUri = folderUri.with({ path: posix.join(folderUri.path, 'definitions.txt') });

    const found = alltopics.find((t) => t === topic);

    vscode.workspace.openTextDocument(fileUri).then(doc => {
        if (open & BOOK_OPEN_FILE) {
            vscode.window.showTextDocument(doc);
        }
        //keep selectionhistory, dont load twice.  
        if (!found){
            addToHistory(topic); //add the topic to the history.
        }
    });
    if (open & BOOK_OPEN_WEB) {
        webBook(topic); //open the web view for the topic.
    }

    //only add if we have data.  
    if (found) {
        addToHistory(topic); //add the topic to the history.
        return true;
    }
    return false;

}
export function pickTopic(selectedtopics : string[], defaultprompts: string[] = [], numtopics: number = 10) : [string, string] {
    //pick a topic from the topicarray based on the sort order.
    //still need to improve when we have no selected topics.  
    let minsort = 1000000; //set to a large number.
    let retkey = "NONE";

    if (selectionhistory.length > 0) {
        for (let i = selectionhistory.length - 1; i > -1; i--) {
            if (topicarray[selectionhistory[i]] !== undefined && topicarray[selectionhistory[i]].length > 0) {
                //sort the topics by date.  
                selectedtopics.unshift(selectionhistory[i]); //add the topic to the selected topics.
                if (retkey === "NONE"){
                    retkey = selectionhistory[i]; //set the key to the topic.
                }


            }
        }


    }
    if (retkey === "NONE"){
        //usually should have a selection history
        //for the session.  
        Object.keys(topicarray).forEach((key) => {
            if (topicarray[key] !== undefined) {
                //sort the topics by date.  
                if (topicarray[key].length > 0) {
                    if (topicarray[key][0].sortorder < minsort && 0.5 < (Math.random()*minsort)) { //pick a random topic with the lowest sort order.
                        retkey = topicarray[key][0].topic; //set the key to the topic with the lowest sort order.
                        minsort = topicarray[key][0].sortorder; //set the minsort to the sort order of the topic.
                    }
                }
            }
        });

    }
    let retdata = "";


    //deduplicate selectedtopics
    selectedtopics = Array.from(new Set(selectedtopics)); //remove duplicates from the array.
    if (retkey !== "NONE"){
        let found = selectedtopics.indexOf(retkey);
        if (found > -1) {
            selectedtopics.splice(found, 1); //remove the topic from the selected topics.
        }
        selectedtopics.push(retkey); //add the key to the selected topics.
    }
    let i=0;
    if (selectedtopics.length > numtopics) {
        i = selectedtopics.length - numtopics; //start from the end of the array.
    }


    //what date do we want to search from?  
    //just add all.  
    let mylist = [];
    for (; i<selectedtopics.length; i++) {
        if (topicarray[ selectedtopics[i] ] !== undefined) {
            retdata += "**" + selectedtopics[i] + "\n"; //add the topic to the data.
            retkey = selectedtopics[i]; //set the key to the topic.

            for (let j=0; j<topicarray[ selectedtopics[i] ].length; j++) {
                //add date here.  
                let item = topicarray[ selectedtopics[i] ][j];
//                let filename = getUri(item.topic);
//				doc += `File: ${item.file}, Line: ${item.line}, Sort: ${item.sortorder}  \n`;
//                retdata += `Topic: [${item.topic}](${filename})  \n`;
//                retdata += `**${item.file}:${item.line}\n`;
//                retdata += `[${item.file}](${item.file}#L${item.line})  \n`;
                
//                retdata += item.data + "\n"; //add all data for the topic.
                mylist.push(item);
            }
        }
    }

    //sort the mylist by date.
    mylist.sort((a, b) => {
        return a.date - b.date; //sort by date.
    });

    for (let i=0; i<mylist.length; i++) {
        //add the date to the data.  
        let item = mylist[i];
//        retdata += `**${item.topic}\n`;
        retdata += `**${item.file}:${item.line}  \n`;
        retdata += item.data + "  \n"; //add all data for the topic.
    }
    //for now returning all topic data in book.  
    return [retkey, retdata]; //return the topic and the data.
}

export async function gitChanges(topics: string[]) : Promise<string> {
    //get the git changes for the topic.  
    //this will be used to update the topic in the book.  
    //for now just return the changes for last topic.  
    //wait for this to complete and retrieve this file.  
    //> git --no-pager log -p --reverse -- book/20250429.txt > book/20250429.log

    const mytopicfile = topics[topics.length-1]; //get the topic file.
    const mytopiclogfile = mytopicfile + ".log"; //get the topic log file.

    //read this log file if exists. 
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    const fileUri = folderUri.with({ path: posix.join(folderUri.path, mytopiclogfile) });    
    const readData = await vscode.workspace.fs.readFile(fileUri);
    const readStr = Buffer.from(readData).toString('utf8');


    const terminal = vscode.window.createTerminal(`Ext Terminal #${NEXT_TERM_ID++}`);
    terminal.sendText("git --no-pager log -p --reverse -- " + mytopicfile + " > " + mytopiclogfile);
    terminal.sendText("; exit");
    

    return readStr;
}


//write to the book/source as needed.  
export async function write(request: vscode.ChatRequest, context: vscode.ChatContext) : Promise<[string, string]>{
    return ["NONE", "NONE"];    
}


//default GIT_BOOK
export async function read(prompt: string, mode: number = GIT_BOOK) : Promise<[string, string]>{
    //adjust request to include book context needed.  
//    return getBook();
    //only want pertinent context.  
    //latest selections etc.  
    //create sort order for toicarray.  
    //then retrieve topic information.  
    //find the topic in the topicarray if we have passed some
    let selectedtopics = findInputTopics(prompt); 
    console.log("Selected topics: ", selectedtopics);

    sortArray(topicarray);

    //pick a topic to return.  
    //right now random.  
    //get all context from the topicarray.  
    //get from selectionhistory if exists.  
    let [topkey, topics] = pickTopic(selectedtopics); //get the topic from the topicarray.
    //find last topic and add all git changes.  

    if (selectedtopics.length > 0 && topkey !== selectedtopics[selectedtopics.length-1]){
        selectedtopics.push(topkey); //add the topic to the list of selected topics.
    }

    if (mode & GIT_CODE){
        try {
            const folderUri = vscode.workspace.workspaceFolders[0].uri;
            const stat = await vscode.workspace.fs.stat(folderUri.with({ path: topkey }));
            //assume file exists if stats doesnt fail.  
            let git = await gitChanges(selectedtopics); //get the git changes for the topic.
            topics += git;  //add the git changes to the full context of topics.
        }
        catch (error) {
            console.error(`Error reading file: ${error}`);
        }
    }

    return [topkey, topics];


}

export function formatDate(date: Date = new Date()): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}${month}${day}`;
};

export function getBook(context: vscode.ExtensionContext | null = null) {
    loadBook(context);
}

export async function closeFileIfOpen(file:vscode.Uri) : Promise<void> {
    const tabs: vscode.Tab[] = vscode.window.tabGroups.all.map(tg => tg.tabs).flat();
    const index = tabs.findIndex(tab => tab.input instanceof vscode.TabInputText && tab.input.uri.path === file.path);
    if (index !== -1) {
        await vscode.window.tabGroups.close(tabs[index]);
    }
}

async function readFileNamesInFolder(path: string): Promise<Array<string>> {
    let topicUri = getUri(path);
    let total = 0;
    let count = 0;
    let retarray = [];
    for (const [name, type] of await vscode.workspace.fs.readDirectory(topicUri)) {
        //what order does this come in?  Is it alphabetical?
        if (type === vscode.FileType.Directory) {
            const fileUri = topicUri.with({ path: posix.join(topicUri.path, name) });
            retarray.push(path + name); //add the directory name to the array.

        }
        if (type === vscode.FileType.File) {
            const fileUri = topicUri.with({ path: posix.join(topicUri.path, name) });
            retarray.push(path + name); //add the file name to the array.
        }
    }
    return retarray;

}

async function readFilesInFolder(folder: vscode.Uri): Promise<{ total: number, count: number, page: string }> {
    let total = 0;
    let count = 0;
    let booknow = 0;
    let openpage = "";
    let allfiles = [];
    for (const [name, type] of await vscode.workspace.fs.readDirectory(folder)) {
        //what order does this come in?  Is it alphabetical?
        if (type === vscode.FileType.Directory) {
            const fileUri = folder.with({ path: posix.join(folder.path, name) });
            await readFilesInFolder(fileUri).then((result) => {
                total += result.total;
                count += result.count;
            });

        }
        if (type === vscode.FileType.File) {
            const fileUri = folder.with({ path: posix.join(folder.path, name) });
            allfiles.push(fileUri);
            let filePath = posix.dirname(fileUri.path);
            const stat = await vscode.workspace.fs.stat(folder.with({ path: filePath }));
            total += stat.size;
            count += 1;
        }
    }
    //sort reverse by path.
    //most recent at top.  
    allfiles.sort((fileA, fileB) => fileB.path.localeCompare(fileA.path));
    for (let i = 0; i < allfiles.length; i++) {
        const fileUri = allfiles[i];
        let altdate = 0;
        try{
            let stats = await vscode.workspace.fs.stat(fileUri);
            const modifiedDate = new Date(stats.mtime);
            //alt date in case this is not named correctly.
            let altdate = modifiedDate.getFullYear()*10000 + modifiedDate.getMonth()*100 + modifiedDate.getDate();
        } catch (error) {
            console.error(`Error reading file: ${error}`);
        }

        await vscode.workspace.openTextDocument(fileUri).then((document) => {
            let text = document.getText();
            console.log(`${fileUri.path} ... read`);
            // parse this.  

            let d = loadPage(text, fileUri.path, altdate);
            if (d.valueOf() > booknow) {
                booknow = d.valueOf(); //get the most recent date.
                openpage = fileUri.path;

                selectedtopic = currenttopic; //set selected topic
                
            }

//                console.log(text);
            // Optionally insert the text into the active editor
    //		insertTextIntoActiveEditor(text);
            /*
            closeFileIfOpen(fileUri).then(() => {
                console.log(`${fileUri.path} ... closed`);
            });
            */
        });

    }
    return { total, count, page: getBookPath() + "/" + booknow.toString() };
}


export function getFileName(filePath: string): string {
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
    else{
        //get date of the file
        const folderUri = vscode.workspace.workspaceFolders[0].uri;

//       const stat => await vscode.workspace.fs.stat(folderUri.with({ path: filePath }))
//        console.log((new Date(stat.mtime)).getFullYear() * 10000); //get the date of the file.
//       return (new Date(stat.mtime)).getFullYear() * 10000;

    }
    return 0;
}

function initArray(topic: string, array: {[key: string] : Array<BookTopic> | undefined} = topicarray) {
    if (!(topic in array) || array[topic] === undefined) {
        array[topic] = [];
    }
}

export function updatePage(filePath: string, text: string, linefrom: number = 0, lineto: number = 0, show: boolean = false) {
    //update the current page with the text and filePath.  
    //this will be used to update the current topic.  
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    // this should be a book path.  Use as you would work on the project.  
    const fileUri = folderUri.with({ path: posix.join(folderUri.path, filePath) });

    const wsEdit = new vscode.WorkspaceEdit();
    wsEdit.createFile(fileUri, { ignoreIfExists: true });
    vscode.workspace.applyEdit(wsEdit).then(() => {


        vscode.workspace.openTextDocument(fileUri).then((document) => {

            vscode.window.showTextDocument(document).then((editor) => {
                /*
            const editor = vscode.window.visibleTextEditors.find(
                (editor) => editor.document.uri.fsPath === document.uri.fsPath
            );   
            */     
    //        let editor = document.editor;
                editor.edit(editBuilder => {
                    if (lineto === 0 && linefrom === 0) {
                        var firstLine = editor.document.lineAt(0);
                        var lastLine = editor.document.lineAt(editor.document.lineCount - 1);
                        var textRange = new vscode.Range(firstLine.range.start, lastLine.range.end);
                        editBuilder.replace(textRange, text); //replace the entire document with the new text.
                    }
                    else if (lineto === -1 && linefrom === -1){
                        //append to the end of the document.
                        var lastLine = editor.document.lineAt(editor.document.lineCount - 1);
                        var textRange = new vscode.Range(lastLine.range.end, lastLine.range.end);
                        editBuilder.insert(textRange.start, "\n" + text); //append the text to the end of the document.
                    }

                }).then(() => {
                    // Optionally, you can show a message to indicate the file has been updated
                    if (!show) {
//                        vscode.commands.executeCommand('workbench.action.closeActiveEditor');
                        setTimeout(() => {
                            vscode.commands.executeCommand("workbench.action.openPreviousRecentlyUsedEditor");                         
                        }, 400); //wait a second before going back to previous editor.

                    }
                    else{
                        //still go back to previous editor?  maybe not just boolean for more possibilities.
                        vscode.commands.executeCommand("workbench.action.openPreviousRecentlyUsedEditor");                         
                    }
                });
            });
        });
    });
}


async function fixVectraError(filePath: vscode.Uri){
    if (filePath.path in vectrafixes){
        //already tried to fix this file.  
    }
    else{
        vectrafixes[filePath.path] = true; //mark this file as fixed.
        try {
            const fileContentBytes = await vscode.workspace.fs.readFile(filePath);
            // If it's a text file, convert to string
            const fileContentString = Buffer.from(fileContentBytes).toString('utf8');
            // Remove the last characters until we find a valid JSON structure
            const jsonEndIndex = fileContentString.indexOf('}]}');
            if (jsonEndIndex !== fileContentString.length - 3) {
                // If the end of the JSON structure is not at the end of the file, truncate it
                const fixedContent = fileContentString.substring(0, jsonEndIndex + 3);
                // Write the fixed content back to the file
                await vscode.workspace.fs.writeFile(filePath, Buffer.from(fixedContent, 'utf8'));
                console.log(`Fixed vectra error in file: ${filePath.path}`);
                
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Error reading file: ${error.message}`);
        }
    }
}

export async function getSummary(input : string, CTX_WND: number = 5000) : Promise<string> {
    //get the summary of the chunks.  
    //this will be used to summarize the book.
    let chunks = await getChunks(input, CTX_WND); //get the chunks from the book.

    let summary = "";
    let sumchunk = [];
    for (let i=0; i<chunks.length-1; i++) {
        //send this chunk to the summarization model.  
        let summary = await ollama.chat({
            model: 'llama3.1:8b',
//            model: 'deepseek-coder-v2:latest',
            //deepseek-r1:latest 
            //granite-code:latest
            //codegemma:latest 
            //model: 'gemma3n:latest',
            //model: 'gemma3:4b',
//            model: 'granite3.3:8b',
    
            messages: [
                { role: 'system', content: `You are a rearranging large pieces of text 
                    and creating abridged versions.  ::FULL VERSION::  Indicates the full text which is being abridged.  
                    ::ABRIDGED VERSION::  The abridged version is only slightly shorter than the original text. Roughly half the size.  
                    When creating the abridged version, the same writing style and syntax as the original is used.  ` },
                { role: 'user', content: `::FULL VERSION::  \n
                    ${chunks[i]}
                    ${chunks[i+1]} \n 
                    After analyzing the above, 
                    here is a shortened version of the same content.  \n
                    ::ABRIDGED VERSION::\n` }
            ]
        });
        sumchunk.push(summary["message"]["content"]); //add the summary to the array.
        console.log(`Summary for chunk ${i/CTX_WND}: ${summary}`);
    }
    if (sumchunk.length > 1) {
        //recursively join the summaries together.
        //will this be good or just a mess?  
        //we are n*(n+1)/2 here.  Time is the constraint.  
        //dependent on how long the summaries are.  
        console.log(`Summarizing ${sumchunk.length} summaries...`);
        summary = sumchunk.join("  \n"); //join the summaries together.
        return getSummary(summary, CTX_WND); //recursively summarize the summaries.
    }
    else{
        summary = chunks[0]; //just return the first chunk.
    }
    return summary;
}

//option to get in date order or topic order.  
export async function getChunks(text: string, CTX_WND: number = 5000) : Promise<Array<string>> {
    //summarize piece by piece.  
    let numchunks = Math.ceil(text.length / CTX_WND); //number of chunks to summarize.
    let chunks = [];
    let i = 0;
    for (i=0; i<text.length; i+=CTX_WND) {
        let end = text.indexOf('\n', (i+1)*CTX_WND);
        //maybe \n** is a better end of chunk.
        if (end === -1) {
            if (text.length < (i+2)*CTX_WND) {
                end = text.length-CTX_WND; //if no newline found, take the rest of the string
            }
            else{
                end = end - (i+1)*CTX_WND; //if no newline found, take the rest of the string
            }

        }
        //adjust chunk to lines, or perhaps next topic, not sure.  
        let chunk = text.substring(i, i + CTX_WND + end);
        chunks.push(chunk); //add the chunk to the array.
    }
    if (i < text.length) {
        //add the last chunk if there is any remaining text.
        chunks.push(text.substring(i));
    }
    return chunks;
}    

export async function markdown(prompt: string) : Promise<string> {
    //this just adjustst the base string to include links to markdown files.  
    //replace **topic with [topic](topic.md)
    //replace #link with [link](link)

    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    let marked = prompt.replace(/(\*\*|\#)(\S+)/g, (match, p1, p2) => {
        // p1 is either ** or #
        // p2 is the topic or link 
        let fname = p2;
        let fileUri = folderUri.with({ path: posix.join(folderUri.path, fname) });
       // this should be a book path.  Use as you would work on the project.  
        if (p1 === "#"){
                fileUri = p2;
                return `[${p1}${p2}](${fileUri})`; //return the markdown link.
        }
        else{
            let colon = p2.lastIndexOf(":");
            if (colon !== -1) {
                //this is a file:line reference.  

                let fname = p2.slice(0, colon); //get the file name.
                let line = p2.slice(colon + 1); //get the line number. 
                //remove folder from file name.  
                p2 = p2.replace(folderUri.path + "/", ""); //remove the folder path from the file name for display purposes.  
                return `[${p1}${p2}](${fname}#L${line})`; //return the markdown link.
            }
            p2 = p2.replace(folderUri.path + "/", ""); //remove the folder path from the file name for display purposes.  
            return `[${p1}${p2}](${fileUri.path})`; //return the markdown link.

        }
    });
    return marked;

}

export async function summary(prompt: string) : Promise<string> {
    //this will be used to find similar topics in the book.  
    //for now just return the topics in the book.
    //should have just topice really expecting.  
    let sim = await similar(prompt); //get the similar topics from the book.
    for (let i=0; i<sim.length; i++) {
        let topic = sim[i].topic;
        prompt = "**" + topic + " \n" + prompt; //add the topic to the prompt.
    }

    //read the prompt and similar topics.  
    let b = await read(prompt, GIT_BOOK);

    //large context window.  testing gemma3n:latest
    let summary = await getSummary(b[1], 5000); //get the summary of the chunks.
    console.log(`Summary: ${summary}`);

    return summary;
}


export async function similar(prompt: string) : Promise<Array<BookTopic>> {
    //this will be used to find similar topics in the book.  
    //for now just return the topics in the book.
    let selectedtopics = findInputTopics(prompt); 
    console.log("Selected topics: ", selectedtopics);
    let bvFolder = getUri(bookvectorFolder);
    let pathParts = [];
    if (selectedtopics.length === 0) {
        //if no topics selected, return all topics.
    }
    else{
        for (let i=0; i<selectedtopics.length; i++) {
            if (topicvectorarray[selectedtopics[i]] !== undefined) {
                //for now use first defined topic vector array.
                pathParts.push(selectedtopics[i].split("/"));

            }
        }

    }
    if (pathParts.length === 0) {
        //if no path parts, use global index.
        pathParts.push([""]);
    }
    let model = 'nomic-embed-text'; //default model to use for embedding.
    let vec = await getVector(prompt, model);

    let ret = [];
    for (let j=0; j<pathParts.length; j++){
        for (let i=0; i<pathParts[j].length+1; i++) {
            let sub1 = pathParts[j].slice(0, i).join('/');
            //what is teh second parameter here?  
            //looks like we are doing some form of FT search not sure how to enable..
            //wink-bm25-text-search
            try {
                if (sub1 in topicvectorarray) {
                    //get more results from closer path or less?  
                    let res = await topicvectorarray[sub1].queryItems(vec, prompt, pathParts[j].length -i+2); 
                    if (res.length > 0) {
                        for (const result of res) {
                            ret.push(result.item.metadata); //should be BookTopic type.
                            console.log(`[${result.score}] ${result.item.metadata.data}`);
                        }
                    } else {
                        console.log(`No results found.`);
                    }
                }
            }
            catch (err) {
                console.error(`Error querying index for topic ${sub1}: ${err.message}`); //create the folder if it does not exist.
                //check for vectra error at end of file and fix.  

                console.log(`${topicvectorarray[sub1].folderPath} does not exist, creating new index.`);
                //remove up to }]}
                fixVectraError(vscode.Uri.file(posix.join(bvFolder.path.slice(1), sub1, "index.json")));
            }
        }
    }
    //deduplicate ret array.  

    for (let i=0; i<ret.length; i++) {
        for (let j=i+1; j<ret.length; j++) {
            //same file and line number. no need to duplicate.  
            if (ret[i].file === ret[j].file && ret[i].line === ret[j].line) {
                ret.splice(j, 1);
                j--;
            }
        }
    }
    return ret;

}




async function getVector(text: string, model: string = 'nomic-embed-text') {
    //get vector from text.  
    //>ollama pull nomic-embed-text

    let embedding = await ollama.embed({ model: model, input: text });
    return embedding["embeddings"][0]; //return the embedding vector.

}

async function addVectorData(topic: BookTopic) {
    //check if we have a vector index for this topic.
    //if not, create one.
    let pathParts = topic.topic.split("/");
    let bvFolder = getUri(bookvectorFolder);
    if (topicvectorarray[topic.topic] === undefined) {

        //init global index
        try{
            //create a global index for all topics.
            if ("" in topicvectorarray){
                    
            }
            else{
                topicvectorarray[""] = new LocalIndex(posix.join(bvFolder.path.slice(1), "")); //create a new index for global use.  
                if (!await topicvectorarray[""].isIndexCreated()) {
                    //if the index does not exist, create it.
                    await topicvectorarray[""].createIndex();
                }
            }
        }
        catch (err) {
            console.error(`Error creating global index: ${err.message}`); //create the folder if it does not exist.
        }

        //get name from topic.  
        //maybe want to create an index by first subfolder or second etc.  
        if (pathParts.length > 1) {
            const folderUri = bvFolder.with({ path: posix.join(bvFolder.path, pathParts.slice(0,-1).join('/')) });
            console.log(`Creating folder: ${folderUri.path}`);
            try{
                //why are we getting a leading slash?  posix.join should not do this.
            fs.mkdirSync(folderUri.path.slice(1), { recursive: true });
            }
            catch (err) {
                console.error(`Error creating directory: ${err.message}`); //create the folder if it does not exist.
            }

            try{

                topicvectorarray[topic.topic] = new LocalIndex(posix.join(bvFolder.path.slice(1), topic.topic)); //create a new index for the topic.
                if (!await topicvectorarray[topic.topic].isIndexCreated()) {
                    //if the index does not exist, create it.
                    await topicvectorarray[topic.topic].createIndex();
                }
            }
            catch (err) {
                console.error(`Error creating index for topic ${topic.topic}: ${err.message}`); //create the folder if it does not exist.
            }
            //create index for each subfolder, lets start at two entries? 
            //some unnecessary duplication here, but maybe worth?  
            //So we have #folders worth of indexes along with #topics.  
            for (let i=1; i<pathParts.length; i++) {
                let sub1 = pathParts.slice(0, i).join('/');
                if (!(sub1 in topicvectorarray)) {
                    //this will fail if we have a topic with the name index.json perhaps
                    try{
                        topicvectorarray[sub1] = new LocalIndex(posix.join(bvFolder.path.slice(1), sub1)); //create a new index for the subfolder.
                        if (!await topicvectorarray[sub1].isIndexCreated()) {
                            //if the index does not exist, create it.
                            await topicvectorarray[sub1].createIndex();
                        }
                    }
                    catch (err) {
                        console.error(`Error creating index for subfolder ${sub1}: ${err.message}`); //create the folder if it does not exist.
                    }
                }

            }
        }
        else{
            try{
                topicvectorarray[topic.topic] = new LocalIndex(posix.join(bvFolder.path.slice(1), topic.topic)); //create a new index for the topic.
                if (!await topicvectorarray[topic.topic].isIndexCreated()) {
                    //if the index does not exist, create it.
                    await topicvectorarray[topic.topic].createIndex();
                }

            }
            catch (err) {
                console.error(`Error creating index for topic ${topic.topic}: ${err.message}`); //create the folder if it does not exist.
            }
        }
    }


    let checkexisting = await topicvectorarray[topic.topic].listItemsByMetadata({
        data: topic.data, date: topic.date, file: topic.file, line: topic.line, topic: topic.topic
        //this should get the last occurrence of this data when vector file is created.  
    });

    let timelag = new Date();
    timelag.setDate(timelag.getDate() - 270); //set the time lag to 9 months ago.
    let checkdate = timelag.getFullYear()*10000 + timelag.getMonth()*100 + timelag.getDate();

    console.log(`Checking existing items for topic ${topic.topic}:`, checkexisting);
    if (checkexisting.length > 0) {
        //assume it is already there.  Duplicate data.  No need to add again.  
        //randomly upsert if the topic is older than 9 months.  
        //this may be problematic not sure how well this upsert is working.  
        //not sure if this works or not...
        //too much trouble to check now.  
        //dont think I need this, if we are checking the date as well.  
/*        
        let upsert = true;
        for (let i=0; i<checkexisting.length; i++) {
            let tempdate = parseInt(String(checkexisting[0].metadata.date)); //get the date from the existing item.
            if (tempdate > checkdate) {
                upsert = false;
            }
        }
        if (upsert){
            let timelag = new Date();
            checkdate = timelag.getFullYear()*10000 + timelag.getMonth()*100 + timelag.getDate();
            //only upsert every 9 months or so.
            topicvectorarray[topic.topic].upsertItem({
                vector: await getVector(topic.data),
                metadata: {str: topic.data, date: checkdate, file: topic.file, line: topic.line, topic: topic.topic},
            }); //insert the item into the index.
        }
*/
    }
    else{

        topicvectorarray[topic.topic].upsertItem({
            vector: await getVector(topic.data),
            //sort order not used.  
            metadata: {data: topic.data, date: topic.date, file: topic.file, line: topic.line, topic: topic.topic},
        }); //insert the item into the index.


        //update global index as well.  
        await topicvectorarray[""].upsertItem({
            vector: await getVector(topic.data), 
            metadata: {data: topic.data, date: topic.date, file: topic.file, line: topic.line, topic: topic.topic},
        }); //insert the item into the index.


        for (let i=1; i<pathParts.length; i++) {
            let sub1 = pathParts.slice(0, i).join('/');
            await topicvectorarray[sub1].upsertItem({
                        vector: await getVector(topic.data), 
                        metadata: {data: topic.data, date: topic.date, file: topic.file, line: topic.line, topic: topic.topic},
                    }); //insert the item into the index.

        }

    }

}

export function loadPage(text: string, filePath: string, altdate: number=0): Number {
    //get the completions from the text.  
    //each topic or comment should be parsed and added to 
    //completions...
    let filename = getFileName(filePath);

    currenttopic = filename.split(".")[0]; //default topic is the file name.

    if (!(currenttopic in topicarray) || topicarray[currenttopic] === undefined) {
        topicarray[currenttopic] = [];
    }
    let mydate = getFileDate(filename); //get the date of the file.    
    if (mydate === 0 && altdate !== 0){
        mydate = altdate; //use the alternate date if we have one.
    }
    let mypage = {"file": filePath, "line": 0, "topic": currenttopic, "sortorder": 0, "date": mydate, "data": ""};
    //adjust sortorder based on order of occurrence for now. 
    let mytopic = {"file": filePath, "line": 0, "topic": currenttopic, "sortorder": 0, "date": mydate, "data": ""};
    let subtopic = {"file": filePath, "line": 0, "topic": currenttopic, "sortorder": 0, "date": mydate, "data": ""};

    let strs = text.split("\n");
    let tkey = currenttopic;
    let topicstart = {};
    keyfind: for (let j=defmap.length-1; j>=0; j--) {
        for (const [key, val] of Object.entries(defmap[j])) {
            topicstart[key] = []; //initialize the topic start array.
        }
    }
    mypage.data = text;
  
    for (let i=0; i<strs.length; i++) {
        let str = strs[i].trim();

        mytopic.data += str + "\n"; //add to current topic data.
        subtopic.data += str + "\n"; //add to current subtopic data.

        if (!defstring.includes(str.charAt(0))) {
            //if the first character is not a definition, then it is a comment.  
            //add to the current topic.  

            continue;
        }
        //search from longest key first.  
        keyfind: for (let j=defmap.length-1; j>=0; j--) {
            for (const [key, val] of Object.entries(defmap[j])) {
                if (str.startsWith(key)) {
                    let type = val;
//                    if (type === "TOPIC") {
                    topicstart[key].push(i);
                    if (key === "**") {
                        currenttopic = str.slice(2).trim(); //get the topic key from the line.                        

                        break keyfind;
                    }
    /*
    var defmap = [{"#": "REF",">": "CMD", "-": "SUBTASK"}, 
        {"##": "REF2", "**": "TOPIC", "@@": "QUESTION", "--": "NOTE", "==": "ANSWER", "$$": "ENV", "!!": "ERROR"}, 
        {"-->": "ENDCOMMENT"}, 
        {"<!--": "STARTCOMMENT"}];
    */
                    //allow for --notes.  
                    else if (key.length < 3 && key !== "**"){


                        //adjust sortorder based on order of occurrence for now. 

                        break keyfind;
                    }

                }
            }


        }

    }

    //iterate through to populate topic trees.  
    //make 0 the most recent entry.  
    //reverse through file.  
    for (let i=topicstart['**'].length-1; i>-1; i--) {
        let startline = strs[topicstart['**'][i] ];
        tkey = startline.slice(2).trim(); //get the topic key from the line.
        initArray(tkey, topicarray); //if doesnt exist, add.  
        let myorder = 0;
        myorder = topicarray[tkey]?.length || 0; //get the current order of the topic.
        mytopic = {"file": filePath, "line": topicstart['**'][i], "topic": tkey, "sortorder": myorder, "date": mydate, "data": ""};
        mytopic.data = strs.slice(topicstart['**'][i], (i+1)<topicstart['**'].length?topicstart['**'][i+1]:strs.length).join("\n"); //get the topic data from the lines.

        //add to vectra (vector DB) this data for later similarity search?  
        //complete index as well as topic based index.  


        //check if exists already.  
        const found = topicarray[tkey]?.find(element => element.file === mytopic.file && element.line === mytopic.line);
        if (found === undefined) {
            topicarray[tkey]?.push(mytopic); //add the previous topic to the array.
            addVectorData(mytopic); //add the topic to the vector DB.
        }

        //adjust sortorder based on order of occurrence for now. 

        currenttopic = tkey;
    }
    let topicidx = 0;
    if (topicstart['**'].length > 0) {
        //set first topic to last entry in file.  
        currenttopic = strs[topicstart['**'][topicidx++] ].slice(2).trim(); //set the current topic to the first topic found.
    }

    //add the date to the topic start array in case we 
    // have some lines without topic.

    //some confusion from starting at end of array.  
    //desire is to put most recent at [0] index.
    for (const [key, val] of Object.entries(topicstart)) {
        topicidx = topicstart["**"].length - 1; //reset topic index for each key.
        for (let i=topicstart[key].length-1; i>-1; i--) {
            let startline = strs[topicstart[key][i] ];

            //get current topic from line number.  
            while (startline < topicstart["**"][topicidx] && topicidx > -1) {
                topicidx--; //increment topic index until we find a topic that is after the startline.
            }
            if (topicidx === -1) {
                //no more topics, use date as topic.
                currenttopic = mydate.toString(); //set the current topic to the date.
            }
            else{
                currenttopic = strs[topicstart["**"][topicidx] ].slice(2).trim(); //set the current topic to the next topic found.
            }
            //end get the current topic from the line number.

            let ckey = startline.slice(key.length).trim();
            let myorder = 0;
            myorder = arrays[key][ckey]?.length || 0; //get the current order of the topic.
            

            subtopic = {"file": filePath, "line": topicstart[key][i], "topic": currenttopic, "sortorder": myorder, "date": mydate, "data": ""};
            //for now just get two lines of data for subtopics.
            subtopic.data = strs.slice(topicstart[key][i],topicstart[key][i]+2 ).join("\n"); //get the subtopic data from the lines.

            initArray(ckey, arrays[key]); //if doesnt exist, add.  

            const found = arrays[key][ckey]?.find(element => element.file === subtopic.file && element.line === subtopic.line);
            if (found === undefined) {
                arrays[key][ckey]?.push(subtopic); //add the previous topic to the array.
            }
        }
    }
    initArray(currenttopic, topicarray); //if doesnt exist, add.  

    const found = topicarray[currenttopic]?.find(element => element.file === mytopic.file && element.line === mytopic.line);
    if (found === undefined) {
        topicarray[currenttopic]?.push(mytopic); //add the previous topic to the array.
        addVectorData(mytopic); //add the topic to the vector DB.
    }
//do we want this?  
    topicarray[mydate.toString()]?.push(mypage);       
    return mydate;
}

export function getBookPath() : string{
    const mySettings = vscode.workspace.getConfiguration('mrrubato');	
    let bookFolder = mySettings.bookfolder;
    return bookFolder;
}

export function getBookVectorPath() : string{
    const mySettings = vscode.workspace.getConfiguration('mrrubato');	
    let bookvectorFolder = mySettings.bookvectorfolder;
    return bookvectorFolder;
}


export function getUri(path: string) : vscode.Uri {
    if (!vscode.workspace.workspaceFolders) {
        return vscode.Uri.parse("");
    }
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    const retUri = folderUri.with({ path: posix.join(folderUri.path, path) });
    return retUri;
}

function getBookUri() : vscode.Uri {
    if (!vscode.workspace.workspaceFolders) {
        return vscode.Uri.parse("");
    }
    // this should be a book path.  Use as you would work on the project.  
    const folderUri = vscode.workspace.workspaceFolders[0].uri;

    const bookFolder = getBookPath(); //get the book folder from settings.
    bookvectorFolder = getBookVectorPath(); //get the book vector folder from settings.
    const bookUri = folderUri.with({ path: posix.join(folderUri.path, bookFolder) });
    return bookUri;
}

function loadBook(context?: vscode.ExtensionContext) {
    if (!vscode.workspace.workspaceFolders) {
        return vscode.window.showInformationMessage('No folder or workspace opened');
    }
    //read all files in /book folder and parse them.  
 
    const bookUri = getBookUri(); //get the book uri.
    const fileUri = bookUri.with({ path: posix.join(bookUri.path, '/definitions.txt') });

    topicarray = {};   //reset topic array.
    arrays = {}; //reset definition arrays.  
    for (let i=0; i<defmap.length; i++) {
        for (const [key, val] of Object.entries(defmap[i])) {   
            arrays[key] = {}; //initialize the array for each key.  
        }
    }

    readFilesInFolder(bookUri).then((result) => {
        console.log(`Total size: ${result.total} bytes, File count: ${result.count}`);
        console.log(topicarray);
        //add this to our CompletionItemProvider.   
        sortArray(topicarray); //sort the topic array by date.
        for (let i=0; i<defmap.length; i++) {
            for (const [key, val] of Object.entries(defmap[i])) {
                sortArray(arrays[key], key);
            }
        }

        //open the most recent file.
        select(result.page + ".txt"); //select and open topic
        
        
        let YYYYmmdd = result.page.split('/').at(-1); //get the date from the path.
        let currentdate = createDateFromYYYYmmdd(YYYYmmdd); //get the current date in YYYYMMDD format.
        let prevdate = new Date(currentdate);
        prevdate.setFullYear(currentdate.getFullYear() - 1); //get the date one year ago.
        
        //see if this logic works.  OK we have a small relationship graph.  
        buildTopicGraph(prevdate.toISOString().slice(0,10).replace(/-/g,""), currentdate.toISOString().slice(0,10).replace(/-/g,"")); //build the topic graph for last year.  
        console.log(bookgraph);

        //start workers.  
        Worker.initWorkers(context); //start the workers.

    
    });


    function createDateFromYYYYmmdd(dateString) {
        try{
            const year = parseInt(dateString.substring(0, 4));
            const month = parseInt(dateString.substring(4, 6)) - 1; // Month is 0-indexed
            const day = parseInt(dateString.substring(6, 8));
            return new Date(year, month, day);
        } catch (error) {
            console.error(`Error parsing date: ${error}`);
            return new Date(); // Return null or handle the error as needed
        }
      }
}

