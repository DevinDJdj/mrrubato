import * as vscode from 'vscode';
import path, { posix, basename } from 'path';
import * as tokenizer from './tokenizer'; // Import the Token interface
import * as Book from './book';

import * as fs from 'fs';

//try to use tokenizer..

interface Topic {
    topic: string;
    data: string;
    vars: {[key: string]: string};
    cmds: Array<{lang: string, cmd: string, topic: string, vars: {[key: string]: string}, data: string}>;
}

interface Command {
    lang: string;
    cmd: string;
    topic: string;
    vars: {[key: string]: string};
    data: string;
}

export var topichistory : Array<Topic> = [];
export var cmdhistory : Array<Command> = [];

var current_lang = "_meta";
export var current_topic = "NONE";
export var current_book = "NONE";
var current_cmd = "";
export var langmap: {[key: string]: {topic: string, lastUpdated?: string}} = {};

var TRANSCRIPT_FOLDER = "c:/devinpiano/transcripts/";
var BOOK_FOLDER = "c:/devinpiano/music/books/";

var started_time = Math.floor(Date.now() / 1000);

function getTime(relativedays=0, actual=false) {
    //for now use started_time.. so we dont keep reloading..
    let now;
    if (actual){
        now = new Date();
    } else {
        now = new Date(started_time * 1000); //use started time for most functions so not reloading transcripts..
    }
    let newDate = new Date(now.getTime() + relativedays * 24 * 60 * 60 * 1000);

    return newDate;
}

function getTimeString(relativedays=0) {
    let now = getTime(relativedays, true); //get actual time..
    return now.toISOString().replace(/[-:T]/g, '').slice(0, 15);
}




export function write(lang: string, command: string, params: {[key: string]: string}, topic: string = null, save: boolean = true, shortform: boolean = false) {

      if (topic === null || topic === undefined){
        topic = current_topic;
      } else {
        if (save){
            current_topic = topic;
            console.log('Updating current topic to ' + topic);
        }
      }
      //add utf-8?  
      let ret = "";
      if (!(lang in langmap)){
        langmap[lang] = {'topic': topic};
      }
      if (langmap[lang]['topic'] !== topic && save){
        langmap[lang]['topic'] = topic;
        ret += `**${topic}\n`;
      }
      ret += `> ${command}\n`;
      let vars: {[key: string]: string} = {};
      for (let pkey in params){
        let p = params[pkey];
        //replace any \ndefstring with \n defstring to avoid confusion.            
        let pattern = new RegExp("\n(" + Book.defstring + ")", "g");
        //for now ok, really want \n$ or \n> to break.  
        if (typeof p === 'string'){
            p = p.replace(pattern, "\n $1"); //untested..
            p = p.replace('\n', '\t'); //replace newlines with \t so we retain.. may mess up some things..
        }
        if (shortform){
            const shortformvars = ['URL', 'ALIAS', 'FEEDBACK', 'TEXT', 'TRANSCRIPT', 'COMMENT', 'QUERY', 'ANSWER', '**']; //list of variable keys to be displayed in the shortform display.

            if (pkey in shortformvars){
                p = p.length > 10 ? p.slice(0, 100) + '...' : p;            
                ret += `$$${pkey}=${p}\n`;
            }
        } else {
            ret += `$$${pkey}=${p}\n`;
        }
      }
      if (!('TIME' in params)){
        ret += `$$TIME=${getTimeString()}\n`;
      }
      ret += `$$\n`;

      if (save){
        let today = new Date().toISOString().slice(0,10).replace(/-/g,"");
        let folder = TRANSCRIPT_FOLDER + lang + '/';
        fs.mkdirSync(folder, { recursive: true });
        fs.appendFileSync(folder + today + '.txt', ret, { encoding: 'utf-8' });
      }
      return ret;

}

export function write_topic(lang: string, topic: string = "", extra: string = "", saveTranscript: boolean = true, saveBook: boolean = false) {

    let ret = "";
    let today = new Date().toISOString().slice(0,10).replace(/-/g,"");

    if (topic === ""){
        topic = current_topic;
    }
    if (extra !== ""){
        ret += `<<${lang}>>\n`;
    }
    if (topic !== current_topic && topic !== null){                
        ret += `**${topic}\n`;
        ret += `$$TIME=${getTimeString()}\n`;

        current_topic = topic;
    }
    if (extra !== ""){   
        ret += `${extra}\n`;

        if (saveBook){
            //write to permanent topic
            //write to permanent selected book/topic..
            let book = current_book ;               
            if (book !== null && book.startsWith('books/')){
                book = book.slice('books/'.length);
            }
            if (book !== null){
                let topicstr = "";
                try {
                    let file_path = path.join(BOOK_FOLDER, book);
                    fs.mkdirSync(file_path, { recursive: true });
                    let exists = fs.existsSync(`${file_path}/${today}.txt`);
                    let f = fs.openSync(`${file_path}/${today}.txt`, 'a', 'utf-8');
                    if (topic !== langmap[book].topic || !exists){ //had to change topics or new file..
                        topicstr = `**${topic}`;
                    }
                    if (topicstr !== ""){ //had to change topics..
                        fs.writeSync(f, topicstr + '\n');
                    }
                    fs.writeSync(f, extra + '\n');
                    fs.closeSync(f);
                    langmap[book].topic = topic;
                } catch (e) {
                    console.log(`Error writing to book file for current book ${book}: ${e}`);
                }
            }
        }
    }
    if (saveTranscript){
        let folder = TRANSCRIPT_FOLDER + lang + '/';
        fs.mkdirSync(folder, { recursive: true });
        let f = fs.openSync(folder + today + '.txt', 'a', 'utf-8');
        fs.writeSync(f, ret + '\n');
        fs.closeSync(f);
    }


    return ret;

}

export function transcribe(str: string, topic: string = "NONE"): Array<{topic: string, data: string, vars: {[key: string]: string}, cmds: Array<any>}> {
    //tokenize the input string.
    let lines = tokenizer.tokenize(str, topic);
    //now we have a list of tokens.  We need to group them by line.
    let topics: Array<Topic> = [];
    let cmds: Array<Command> = [];
    let topicobj: Topic = {
            topic: topic,
            data: "",
            vars: {}, 
            cmds: [],
        };

    let commandobj: Command | null = null;
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].line;
        let linestr = lines[i].map(token => token.data).join("");
        console.log( linestr);
        let basetype = linestr.substring(0, 2);

        switch (basetype) {
            case "**":
                if (topicobj !== null && topicobj.data.trim().length > 0) {
                    topichistory.push(topicobj);
                    topics.push(topicobj);
                }
                topic = linestr.slice(2).trim();
                topicobj = {
                    topic: topic,
                    data: linestr + "\n",
                    vars: {}, 
                    cmds: [],
                };
                current_topic = topic;
                break;
            case "> ":
            case ">>":
                if (commandobj !== null && commandobj.cmd.trim().length > 0) {
                    cmdhistory.push(commandobj);
                    cmds.push(commandobj);
                    topicobj.cmds.push(commandobj);
                    commandobj = null;
                }
                current_cmd = linestr.slice(2).trim();
                commandobj = {
                    lang: current_lang,
                    cmd: current_cmd,
                    topic: current_topic,
                    vars: {},
                    data: linestr + "\n",
                };
                topicobj.data += linestr + "\n";
                break;
            case "$$":
                if (linestr.trim().length < 3) {
                    if (current_cmd.trim().length > 0) {
                        cmdhistory.push(commandobj);
                        topicobj.cmds.push(commandobj);
                        cmds.push(commandobj);
                        commandobj = null;
                    }
                    break;
                }
                let v = linestr.slice(2).trim().split("=");
                if (v.length > 1) {
                    if (commandobj !== null && commandobj.cmd.trim().length > 0) { //add to command
                        commandobj.vars[v[0].trim()] = v.slice(1).join("=").trim();
                    }
                    else if (topicobj !== null && topicobj.data.trim().length > 0) {
                        topicobj.data += linestr + "\n";
                        topicobj.vars[v[0].trim()] = v.slice(1).join("=").trim();
                    }
                }
                break;
            default:
                topicobj.data += linestr + "\n";
                if (commandobj !== null) {
                    commandobj.data += linestr + "\n";
                }

        }
    }
    //add last topic and command to history.
    if (topicobj !== null && topicobj.data.trim().length > 0) {
        topichistory.push(topicobj);
        topics.push(topicobj);
    }
    if (commandobj !== null && commandobj.cmd.trim().length > 0) {
        topicobj.cmds.push(commandobj);
        cmdhistory.push(commandobj);
        cmds.push(commandobj);
    }

    return topics; //mostly use topics[n].cmds for commands.
}
