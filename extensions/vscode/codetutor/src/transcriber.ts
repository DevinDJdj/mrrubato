import * as vscode from 'vscode';
import { posix, basename } from 'path';
import * as tokenizer from './tokenizer'; // Import the Token interface

import * as fs from 'fs';

//try to use tokenizer..

export var topichistory = [];
export var cmdhistory = [];

var current_lang = "_meta";
var current_topic = "NONE";
var current_cmd = "";


export function transcribe(str: string, topic: string = "NONE"): Array<{topic: string, data: string, vars: {[key: string]: string}, cmds: Array<any>}> {
    //tokenize the input string.
    let lines = tokenizer.tokenize(str, topic);
    //now we have a list of tokens.  We need to group them by line.
    let topics = [];
    let cmds = [];
    let topicobj = null;
    let commandobj = null;
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

                break;

        }
    }
    //add last topic and command to history.
    if (topicobj !== null && topicobj.data.trim().length > 0) {
        topichistory.push(topicobj);
        topics.push(topicobj);
    }
    if (commandobj !== null && commandobj.cmd.trim().length > 0) {
        cmdhistory.push(commandobj);
        cmds.push(commandobj);
    }

    return topics; //mostly use topics[n].cmds for commands.
}
