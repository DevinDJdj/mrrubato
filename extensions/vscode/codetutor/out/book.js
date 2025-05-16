"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.arrays = exports.commandarray = exports.temptopicarray = exports.temptopics = exports.topicarray = exports.alltopicsa = exports.alltopics = void 0;
exports.logCommand = logCommand;
exports.getCommandType = getCommandType;
exports.open = open;
exports.findTopics = findTopics;
exports.getTempTopicsFromPath = getTempTopicsFromPath;
exports.adjustSort = adjustSort;
exports.pickTopic = pickTopic;
exports.gitChanges = gitChanges;
exports.write = write;
exports.read = read;
exports.getBook = getBook;
exports.closeFileIfOpen = closeFileIfOpen;
exports.getFileName = getFileName;
exports.updatePage = updatePage;
exports.loadPage = loadPage;
exports.getBookPath = getBookPath;
exports.getUri = getUri;
const vscode = __importStar(require("vscode"));
const path_1 = require("path");
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
var gitstruct = { "bydate": {}, "bytopic": {}, "alltopics": "", "allcontent": {} }; //context holds sequential string.  
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
var definitions = { "REF": "#", "REF2": "##", "TOPIC": "**", "STARTCOMMENT": "<!--", "ENDCOMMENT": "-->", "CMD": ">", "QUESTION": "@@", "NOTE": "--", "SUBTASK": "-" };
var defmap = [{ "#": "REF", ">": "CMD", "-": "SUBTASK" },
    { "##": "REF2", "**": "TOPIC", "@@": "QUESTION", "--": "NOTE", "==": "ANSWER", "$$": "ENV", "!!": "ERROR" },
    { "-->": "ENDCOMMENT" },
    { "<!--": "STARTCOMMENT" }];
var defstring = "!@#$%^&*<>/-+";
exports.alltopics = [];
exports.alltopicsa = [];
exports.topicarray = {};
exports.temptopics = [];
exports.temptopicarray = {};
exports.commandarray = {};
exports.arrays = {};
//this will look like arrays[">"]["TOPIC"] = ...
var refarray = [];
let mynow = new Date(); //get the current date in YYYYMMDD format.    
let NEXT_TERM_ID = 1;
//store data as tabs open and close and based on location in the tab.  
//from this info generate the context when querying the model.  
//right now only front-side loading.  Possibly add RAG processing later?  
//need to include some random data in the context to make sure 
//the logic is not circular.  
function logCommand(command) {
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
function getCommandType(str) {
    if (str.length < 2) {
        return ["", ""];
    }
    else {
        return [str.charAt(0), str.charAt(1)]; //get the first two characters of the string for now.
    }
}
function open(context) {
    return getBook();
}
function getDateFromString(dateString) {
    if (dateString.length !== 8) {
        return new Date(); // Return current date if the string is not in the expected format
    }
    const year = parseInt(dateString.substring(0, 4), 10);
    const month = parseInt(dateString.substring(4, 6), 10) - 1; // Months are 0-indexed
    const day = parseInt(dateString.substring(6, 8), 10);
    return new Date(year, month, day);
}
function getDaysBetweenDates(startDate, endDate) {
    const startTime = startDate.getTime();
    const endTime = endDate.getTime();
    const timeDiff = endTime - startTime;
    const daysDiff = Math.round(timeDiff / (1000 * 60 * 60 * 24));
    return daysDiff;
}
function getRecency(bt, mydate = new Date()) {
    let cumdate = 0;
    for (let i = 0; i < bt.length; i++) {
        //need better calculation of recency.
        //get closest to mydate.  
        cumdate += getDaysBetweenDates(getDateFromString(bt[i].date.toString()), mydate);
        bt[i].sortorder = 0;
    }
    if (bt.length > 0) {
        return cumdate / bt.length; //average recency of the topics.
    }
    else {
        return 0;
    }
}
function findTopics(inputString) {
    // Create a regex pattern to match double asterisks and capture the text after them
    //need to add newline at start.  
    const regex = /\*\*(.*?)\*/g;
    let matches = [];
    // Use the regex to find all instances in the input string
    let match;
    while ((match = regex.exec(inputString)) !== null) {
        if (match[1]) {
            matches.push(match[1].trim());
        }
    }
    return matches;
}
async function getTempTopicsFromPath(path) {
    //get the file name from the path.  
    //this will be used to get the file name from the path.  
    let topics = await readFileNamesInFolder(path);
    //create new entries in the topicarray.
    //these should be relative paths now.  
    for (let i = 0; i < topics.length; i++) {
        let mytopic = topics[i];
        const found = exports.temptopics.find((topic) => topic === mytopic);
        if (!found) {
            exports.temptopics.push(mytopic); //add the topic to the array.
        }
    }
    return topics;
}
function adjustSort(array) {
    //go through topicarray
    //and adjust the sort order based on the date.
    //and other things.  
}
//do we want to reset all here?  
//for now the book isnt large enough to worry about this type of performance.  But...
function sortArray(array, typekey = '') {
    if (typekey === '') {
        exports.alltopics = []; //reset all topics.
    }
    Object.keys(array).forEach((key) => {
        if (array[key] !== undefined) {
            //sort the topics by date.  
            if (array[key].length > 0) {
                array[key][0].sortorder = getRecency(array[key]); //set the sort order to recency.
            }
        }
        exports.alltopics.push(key);
        exports.alltopicsa.push(key.substring(0, 1)); //add the first character of the topic to the array.
    });
}
function pickTopic(selectedtopics, defaultprompts = [], numtopics = 10) {
    //pick a topic from the topicarray based on the sort order.
    //still need to improve when we have no selected topics.  
    let minsort = 1000000; //set to a large number.
    let retkey = "NONE";
    Object.keys(exports.topicarray).forEach((key) => {
        if (exports.topicarray[key] !== undefined) {
            //sort the topics by date.  
            if (exports.topicarray[key].length > 0) {
                if (exports.topicarray[key][0].sortorder < minsort && 0.5 < (Math.random() * minsort)) { //pick a random topic with the lowest sort order.
                    retkey = exports.topicarray[key][0].topic; //set the key to the topic with the lowest sort order.
                    minsort = exports.topicarray[key][0].sortorder; //set the minsort to the sort order of the topic.
                }
            }
        }
    });
    let retdata = "";
    //random recent topic.  
    retdata += "**" + retkey + "\n"; //add the random topic to the data.
    if (exports.topicarray[retkey] !== undefined) {
        for (let i = 0; i < exports.topicarray[retkey].length; i++) {
            retdata += exports.topicarray[retkey][i].data + "\n"; //add all data for the topic.
        }
    }
    for (let i = 0; i < selectedtopics.length; i++) {
        if (exports.topicarray[selectedtopics[i]] !== undefined) {
            retdata += "**" + selectedtopics[i] + "\n"; //add the topic to the data.
            retkey = selectedtopics[i]; //set the key to the topic.
            for (let j = 0; j < exports.topicarray[selectedtopics[i]].length; j++) {
                retdata += exports.topicarray[selectedtopics[i]][j].data + "\n"; //add all data for the topic.
            }
        }
    }
    //for now returning all topic data in book.  
    return [retkey, retdata]; //return the topic and the data.
}
function gitChanges(topics) {
    //get the git changes for the topic.  
    //this will be used to update the topic in the book.  
    //for now just return the changes for last topic.  
    //wait for this to complete and retrieve this file.  
    //> git --no-pager log -p --reverse -- book/20250429.txt > book/20250429.log
    const mytopicfile = topics[topics.length - 1]; //get the topic file.
    const mytopiclogfile = mytopicfile + ".log"; //get the topic log file.
    const terminal = vscode.window.createTerminal(`Ext Terminal #${NEXT_TERM_ID++}`);
    terminal.sendText("git --no-pager log -p --reverse -- " + mytopicfile + " > " + mytopiclogfile);
    let retdata = "";
    return retdata;
}
//write to the book/source as needed.  
async function write(request, context) {
    return ["NONE", "NONE"];
}
async function read(prompt, context) {
    //adjust request to include book context needed.  
    //    return getBook();
    //only want pertinent context.  
    //latest selections etc.  
    //create sort order for toicarray.  
    //then retrieve topic information.  
    //find the topic in the topicarray if we have passed some
    let selectedtopics = findTopics(prompt);
    console.log("Selected topics: ", selectedtopics);
    sortArray(exports.topicarray);
    //pick a topic to return.  
    //right now random.  
    //get all context from the topicarray.  
    let [topkey, topics] = pickTopic(selectedtopics); //get the topic from the topicarray.
    //find last topic and add all git changes.  
    selectedtopics.unshift(topkey); //add the topic to the list of selected topics.
    try {
        const folderUri = vscode.workspace.workspaceFolders[0].uri;
        const stat = await vscode.workspace.fs.stat(folderUri.with({ path: topkey }));
        //assume file exists.  
        let git = gitChanges(selectedtopics); //get the git changes for the topic.
        topics += git; //add the git changes to the full context of topics.
    }
    catch (error) {
        console.error(`Error reading file: ${error}`);
    }
    return [topkey, topics];
}
function formatDate(date = new Date()) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
}
;
function getBook() {
    loadBook();
}
async function closeFileIfOpen(file) {
    const tabs = vscode.window.tabGroups.all.map(tg => tg.tabs).flat();
    const index = tabs.findIndex(tab => tab.input instanceof vscode.TabInputText && tab.input.uri.path === file.path);
    if (index !== -1) {
        await vscode.window.tabGroups.close(tabs[index]);
    }
}
async function readFileNamesInFolder(path) {
    let topicUri = getUri(path);
    let total = 0;
    let count = 0;
    let retarray = [];
    for (const [name, type] of await vscode.workspace.fs.readDirectory(topicUri)) {
        //what order does this come in?  Is it alphabetical?
        if (type === vscode.FileType.Directory) {
            const fileUri = topicUri.with({ path: path_1.posix.join(topicUri.path, name) });
            retarray.push(path + name); //add the directory name to the array.
        }
        if (type === vscode.FileType.File) {
            const fileUri = topicUri.with({ path: path_1.posix.join(topicUri.path, name) });
            retarray.push(path + name); //add the file name to the array.
        }
    }
    return retarray;
}
async function readFilesInFolder(folder) {
    let total = 0;
    let count = 0;
    let allfiles = [];
    for (const [name, type] of await vscode.workspace.fs.readDirectory(folder)) {
        //what order does this come in?  Is it alphabetical?
        if (type === vscode.FileType.Directory) {
            const fileUri = folder.with({ path: path_1.posix.join(folder.path, name) });
            readFilesInFolder(fileUri).then((result) => {
                total += result.total;
                count += result.count;
            });
        }
        if (type === vscode.FileType.File) {
            const fileUri = folder.with({ path: path_1.posix.join(folder.path, name) });
            allfiles.push(fileUri);
            let filePath = path_1.posix.dirname(fileUri.path);
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
        vscode.workspace.openTextDocument(fileUri).then((document) => {
            let text = document.getText();
            console.log(`${fileUri.path} ... read`);
            // parse this.  
            loadPage(text, fileUri.path);
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
    return { total, count };
}
function getFileName(filePath) {
    //get the date of the file.  
    //get the filename without the extension and path.  
    let myName = path_1.posix.basename(filePath);
    return myName; //remove the extension.
}
function getFileDate(filePath) {
    filePath = filePath.split(".")[0]; //remove the extension.
    if (!Number.isNaN(filePath)) {
        return Number(filePath); //get the date of the file.  
    }
    return 0;
}
function initArray(topic, array = exports.topicarray) {
    if (!(topic in array) || array[topic] === undefined) {
        array[topic] = [];
    }
}
function updatePage(filePath, text, linefrom = 0, lineto = 0, show = false) {
    //update the current page with the text and filePath.  
    //this will be used to update the current topic.  
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    // this should be a book path.  Use as you would work on the project.  
    const fileUri = folderUri.with({ path: path_1.posix.join(folderUri.path, filePath) });
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
                    else if (lineto === -1 && linefrom === -1) {
                        //append to the end of the document.
                        var lastLine = editor.document.lineAt(editor.document.lineCount - 1);
                        var textRange = new vscode.Range(lastLine.range.end, lastLine.range.end);
                        editBuilder.insert(textRange.start, "\n" + text); //append the text to the end of the document.
                    }
                }).then(() => {
                    // Optionally, you can show a message to indicate the file has been updated
                    if (!show) {
                        vscode.commands.executeCommand("workbench.action.openPreviousRecentlyUsedEditor");
                    }
                });
            });
        });
    });
}
function loadPage(text, filePath) {
    //get the completions from the text.  
    //each topic or comment should be parsed and added to 
    //completions...
    let filename = getFileName(filePath);
    currenttopic = filename.split(".")[0]; //default topic is the file name.
    if (!(currenttopic in exports.topicarray) || exports.topicarray[currenttopic] === undefined) {
        exports.topicarray[currenttopic] = [];
    }
    let mydate = getFileDate(filename.split(".")[0]); //get the date of the file.    
    let mypage = { "file": filePath, "line": 0, "topic": currenttopic, "sortorder": 0, "date": mydate, "data": "" };
    //adjust sortorder based on order of occurrence for now. 
    let mytopic = { "file": filePath, "line": 0, "topic": currenttopic, "sortorder": 0, "date": mydate, "data": "" };
    let strs = text.split("\n");
    let tkey = currenttopic;
    for (let i = 0; i < strs.length; i++) {
        let str = strs[i].trim();
        mypage.data += str + "\n"; //add to current page data.
        mytopic.data += str + "\n"; //add to current topic data.
        if (!defstring.includes(str.charAt(0))) {
            //if the first character is not a definition, then it is a comment.  
            //add to the current topic.  
            continue;
        }
        keyfind: for (let j = defmap.length - 1; j >= 0; j--) {
            for (const [key, val] of Object.entries(defmap[j])) {
                if (str.startsWith(key)) {
                    let type = val;
                    //                    if (type === "TOPIC") {
                    if (key === "**") {
                        initArray(tkey, exports.topicarray); //if doesnt exist, add.  
                        exports.topicarray[tkey]?.push(mytopic); //add the previous topic to the array.
                        tkey = str.slice(j + 1);
                        let myorder = 0;
                        myorder = exports.topicarray[tkey]?.length || 0; //get the current order of the topic.
                        mytopic = { "file": filePath, "line": i, "topic": tkey, "sortorder": myorder, "date": mydate, "data": "" };
                        //adjust sortorder based on order of occurrence for now. 
                        currenttopic = tkey;
                        break keyfind;
                    }
                    else if (key === ">") {
                        initArray(tkey, exports.arrays[key]); //if doesnt exist, add.  
                        exports.arrays[key][tkey]?.push(mytopic); //add the previous topic to the array.
                        tkey = str.slice(j + 1);
                        let myorder = 0;
                        myorder = exports.arrays[key][tkey]?.length || 0; //get the current order of the topic.
                        mytopic = { "file": filePath, "line": i, "topic": tkey, "sortorder": myorder, "date": mydate, "data": "" };
                        //adjust sortorder based on order of occurrence for now. 
                        break keyfind;
                    }
                }
            }
        }
    }
    initArray(currenttopic, exports.topicarray); //if doesnt exist, add.  
    exports.topicarray[currenttopic]?.push(mytopic);
    exports.topicarray[mydate.toString()]?.push(mypage);
}
function getBookPath() {
    const mySettings = vscode.workspace.getConfiguration('mrrubato');
    let bookFolder = mySettings.bookfolder;
    return bookFolder;
}
function getUri(path) {
    if (!vscode.workspace.workspaceFolders) {
        return vscode.Uri.parse("");
    }
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    const retUri = folderUri.with({ path: path_1.posix.join(folderUri.path, path) });
    return retUri;
}
function getBookUri() {
    if (!vscode.workspace.workspaceFolders) {
        return vscode.Uri.parse("");
    }
    // this should be a book path.  Use as you would work on the project.  
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    const bookFolder = getBookPath(); //get the book folder from settings.
    const bookUri = folderUri.with({ path: path_1.posix.join(folderUri.path, bookFolder) });
    return bookUri;
}
function loadBook() {
    if (!vscode.workspace.workspaceFolders) {
        return vscode.window.showInformationMessage('No folder or workspace opened');
    }
    //read all files in /book folder and parse them.  
    const bookUri = getBookUri(); //get the book uri.
    const fileUri = bookUri.with({ path: path_1.posix.join(bookUri.path, '/definitions.txt') });
    exports.topicarray = {}; //reset topic array.
    exports.arrays = {}; //reset definition arrays.  
    for (let i = 0; i < defmap.length; i++) {
        for (const [key, val] of Object.entries(defmap[i])) {
            exports.arrays[key] = {}; //initialize the array for each key.  
        }
    }
    readFilesInFolder(bookUri).then((result) => {
        console.log(`Total size: ${result.total} bytes, File count: ${result.count}`);
        console.log(exports.topicarray);
        //add this to our CompletionItemProvider.   
        sortArray(exports.topicarray); //sort the topic array by date.
        sortArray(exports.arrays['>']);
    });
}
//# sourceMappingURL=book.js.map