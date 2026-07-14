
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
var current_cmd = "";


export function transcribe(str: string, topic: string = "NONE"): Array<{topic: string, data: string, vars: {[key: string]: string}, cmds: Array<any>}> {
    //tokenize the input string.
//    let lines = tokenizer.tokenize(str, topic);
    let lines = str.split("\n");
    //now we have a list of tokens.  We need to group them by line.
    let topics = [];
    let cmds = [];
    let blanktopicobj : Topic = {
            topic: topic,
            data: "",
            vars: {}, 
            cmds: Array<Command>(),
    };
    let topicobj = { ...blanktopicobj };

    let blankcommandobj : Command = 
                {
                    lang: "",
                    cmd: "",
                    topic: topic,
                    vars: {},
                    data: "",
                };
    let commandobj = { ...blankcommandobj };
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        let linestr = line.trim();
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
                    cmds: Array<Command>(),
                };
                current_topic = topic;
                break;
            case "> ":
            case ">>":
                if (commandobj !== null && commandobj.cmd.trim().length > 0) {
                    cmdhistory.push(commandobj);
                    cmds.push(commandobj);
                    topicobj.cmds.push(commandobj);
                    commandobj = { ...blankcommandobj };
                }
                current_cmd = linestr.slice(2).trim();
                commandobj = { ...blankcommandobj };

                break;
            case "$$":
                if (linestr.trim().length < 3) {
                    if (current_cmd.trim().length > 0) {
                        cmdhistory.push(commandobj);
                        topicobj.cmds.push(commandobj);
                        cmds.push(commandobj);
                        commandobj = { ...blankcommandobj };
                    }
                    break;
                }
                let v = linestr.slice(2).trim().split("=");
                if (v.length > 1) {
                    if (commandobj !== null && commandobj.cmd.trim().length > 0) { //add to command
                        let key = v[0].trim();
                        let value = v.slice(1).join("=").trim();
                        commandobj.vars[key] = value;
                    }
                    else if (topicobj !== null && topicobj.data.trim().length > 0) {
                        topicobj.data += linestr + "\n";
                        let key = v[0].trim();
                        let value = v.slice(1).join("=").trim();
                        topicobj.vars[key] = value;
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
