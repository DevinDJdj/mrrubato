"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};

export var topichistory = [];
export var cmdhistory = [];
export var current_lang = "_meta";
export var current_topic = "NONE";
var current_cmd = "";
export function transcribe(str, topic="NONE") {
    //tokenize the input string.
    //    let lines = tokenizer.tokenize(str, topic);
    var lines = str.split("\n");
    //now we have a list of tokens.  We need to group them by line.
    var topics = [];
    var cmds = [];
    var blanktopicobj = {
        topic: topic,
        data: "",
        vars: {},
        cmds: Array(),
    };
    var topicobj = __assign({}, blanktopicobj);
    var blankcommandobj = {
        lang: "",
        cmd: "",
        topic: topic,
        vars: {},
        data: "",
    };
    var commandobj = __assign({}, blankcommandobj);
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        var linestr = line.trim();
        console.log(linestr);
        var basetype = linestr.substring(0, 2);
        switch (basetype) {
            case "**":
                if (topicobj !== null && topicobj.data.trim().length > 0) {
                    topichistory.push(__assign({}, topicobj));
                    topics.push(__assign({}, topicobj));
                }
                topic = linestr.slice(2).trim();
                topicobj = {
                    topic: topic,
                    data: linestr + "\n",
                    vars: {},
                    cmds: Array(),
                };
                current_topic = topic;
                break;
            case "> ":
            case ">>":
                if (commandobj !== null && commandobj.cmd.trim().length > 0) {
                    cmdhistory.push(__assign({}, commandobj));
                    cmds.push(__assign({}, commandobj));
                    topicobj.cmds.push(__assign({}, commandobj));
                    commandobj = __assign({}, blankcommandobj);
                }
                commandobj = __assign({}, blankcommandobj);
                current_cmd = linestr.slice(2).trim();
                commandobj.cmd = current_cmd;
                commandobj.topic = current_topic;
                break;
            case "$$":
                if (linestr.trim().length < 3) {
                    if (current_cmd.trim().length > 0) {
                        cmdhistory.push(__assign({}, commandobj));
                        topicobj.cmds.push(__assign({}, commandobj));
                        cmds.push(__assign({}, commandobj));
                        commandobj = __assign({}, blankcommandobj);
                    }
                    break;
                }
                var v = linestr.slice(2).trim().split("=");
                if (v.length > 1) {
                    if (commandobj !== null && commandobj.cmd.trim().length > 0) { //add to command
                        var key = v[0].trim();
                        var value = v.slice(1).join("=").trim();
                        commandobj.vars[key] = value;
                    }
                    else if (topicobj !== null && topicobj.data.trim().length > 0) {
                        topicobj.data += linestr + "\n";
                        var key = v[0].trim();
                        var value = v.slice(1).join("=").trim();
                        topicobj.vars[key] = value;
                    }
                }
                break;
            default:
                topicobj.data += linestr + "\n";
                if (commandobj !== null && commandobj.cmd.trim().length > 0) {
                    commandobj.data += linestr + "\n";
                }
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
