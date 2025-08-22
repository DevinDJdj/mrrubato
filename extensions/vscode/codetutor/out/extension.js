"use strict";
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
//npx --package yo --package generator-code -- yo code
//npm install --global yo generator-code
//if not working run this..
//>cd [extensiondir]
//>tsc -watch -p ./
//npm install --save @vscode/prompt-tsx
//npm install --save ollama
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.default = deactivate;
const vscode = __importStar(require("vscode"));
const prompt_tsx_1 = require("@vscode/prompt-tsx");
const path_1 = require("path");
const prompts_1 = require("./prompts");
const Book = __importStar(require("./book"));
const Worker = __importStar(require("./worker"));
const ollama_1 = __importDefault(require("ollama"));
const toolParticipant_1 = require("./toolParticipant");
const BASE_PROMPT = 'You are a helpful code tutor. Your job is to teach the user with simple descriptions and sample code of the concept. Respond with a guided overview of the concept in a series of messages. Do not give the user the answer directly, but guide them to find the answer themselves. If the user asks a non-programming question, politely decline to respond.';
const EXERCISES_PROMPT = 'You are a helpful tutor. Your job is to teach the user with fun, simple exercises that they can complete in the editor. Your exercises should start simple and get more complex as the user progresses. Move one concept at a time, and do not move on to the next concept until the user provides the correct answer. Give hints in your exercises to help the user learn. If the user is stuck, you can provide the answer and explain why it is the answer. If the user asks a non-programming question, politely decline to respond.';
// define a chat handler
let max_context_length = 512000; //for now using this max context length.  
let activeEditor = vscode.window.activeTextEditor;
let isWorking = false;
let workFunc = null;
let workPrompt = "Improve my code";
function get_current_weather(city) {
    return `The current weather in ${city} is sunny.`;
}
function validateChange(topkey, change) {
    //check if the change is valid.
    const allDiagnostics = vscode.languages.getDiagnostics();
    //get diagnostics for all open files.  
    //if there is some error, prompt to try to fix.  
    //return the diagnostic info.  
    console.log(allDiagnostics);
    return true;
}
function getRandomPrompt(promptonly = true) {
    const mySettings = vscode.workspace.getConfiguration('mrrubato');
    if (promptonly) {
        //get a random work prompt.  
        if (mySettings.workprompts.length > 0) {
            let rand = Math.floor(Math.random() * mySettings.workprompts.length);
            let prompt = mySettings.workprompts[rand].prompt;
            return prompt;
        }
        else {
            //get a random default prompt.  
            if (mySettings.defaultprompts.length > 0) {
                let rand = Math.floor(Math.random() * mySettings.defaultprompts.length);
                let prompt = mySettings.defaultprompts[rand].prompt;
                return prompt;
            }
        }
    }
    else {
        //return topics with the prompt.  
        //continue thought.  
        if (mySettings.roboprompts.length > 0) {
            let rand = Math.floor(Math.random() * mySettings.roboprompts.length);
            let prompt = mySettings.roboprompts[rand].prompt;
            let topics = mySettings.roboprompts[rand].topics;
            return topics + "\n" + prompt;
        }
        else {
            return "Just starting, help me figure things out.";
        }
    }
}
async function updatePrompts(topkey, topics, fullMessage) {
    //update the prompts here.
    const mySettings = vscode.workspace.getConfiguration('mrrubato');
    let addltopics = Book.findInputTopics(fullMessage);
    const topicArray = mySettings.defaultprompts.map(obj => obj.topic);
    let bookdata = Book.pickTopic(addltopics, topicArray, 5);
    if (mySettings.codingmode === "git") {
        let git = await Book.gitChanges(addltopics); //get the git changes for the topic.
        //		bookdata[1] += git;  //add the git changes to the full context of topics.
        bookdata[1] += git.slice(-max_context_length / 4);
    }
    else if (mySettings.codingmode === "book") {
        //get the book context for the topic.
        //nothing additional.  
    }
    topics = topics + bookdata[1].slice(-max_context_length / 2); //dont want to overwrite the full context.  
    topics = topics.slice(-max_context_length);
    //need to determine weight of prompt.  
    mySettings.roboprompts.push({ 'prompt': fullMessage, 'topics': topics, weight: 0.5 });
    //random delete a prompt.  
    if (mySettings.roboprompts.length > mySettings.numworkprompts) {
        let val = mySettings.roboprompts.shift();
        val.weight = val.weight * (Math.random());
        if (val.weight > 0.125) {
            //iterate around 2-3 times.  
            //delete the first one.
            //keep thinking about this or not.  
            mySettings.roboprompts.push(val);
        }
        if (val.weight < 0.0125) {
            //switch prompt
            mySettings.roboprompts.push({ 'prompt': getRandomPrompt(), 'topics': topics, weight: 0.5 });
        }
    }
    //for now add this prompt.  
    //probably need several steps here..
    //maybe one call to rewrite this.  
    mySettings.update('workprompt', getRandomPrompt(false));
}
function roboupdate(topkey, topics, fullMessage) {
    //update the source code and highlight what chnaged.
    if (validateChange(topkey, fullMessage)) {
        //		Book.updatePage(topkey, fullMessage);
        updatePrompts(topkey, topics, fullMessage);
    }
    //Book.updatePage("book/20230110.txt", "hello");
    if (activeEditor) {
        (0, toolParticipant_1.updateStatusBarItem)();
        //show the change made and switch to this page.  
    }
}
async function getWorkPrompt(mySettings) {
    let workPrompt = mySettings.workprompt;
    workPrompt = ""; //reset the work prompt.
    //iterate through work and see what is next.  
    if (Worker.worktopics.length > 0) {
        let worker = await Worker.incrementWorker(); //increment the worker to next step.
        //found a worker, get the prompt.
        workPrompt = worker.workflow.prompts[worker.workflow.step];
        //use context from worker to formulate query.  
    }
    if (workPrompt === "") {
        //no worker found, get a random prompt.
        workPrompt = getRandomPrompt();
    }
    return workPrompt;
}
async function work(request, context, stream, token) {
    const mySettings = vscode.workspace.getConfiguration('mrrubato');
    let workPrompt = await getWorkPrompt(mySettings); //get the work prompt from settings.
    if (!mySettings.runinbackground) {
        //not running in background per settings.
        //controlled by /stop
        return;
    }
    else {
        //run the work function here.
        console.log('Running background agent');
        //		stream.markdown('**Running background agent**  \n' + mySettings.runinbackground);
        if (!isWorking) {
            isWorking = true;
            workFunc = setInterval(() => {
                //call the function here.
                work(request, context, stream, token);
            }, mySettings.runinterval);
            //this must be restarted to change runinterval.  
        }
    }
    try {
        //connect remote
        //client = ollama.Client(host='http://192.168.1.154:11434')
        //response = client.generate(model='llama3.2b', prompt=my_prompt)
        //actual_response = response['response']
        let [topkey, topicdata] = await Book.read(workPrompt, Book.GIT_CODE);
        //get topic to work on and context.  
        //const topics = "test"
        workPrompt = workPrompt.slice(-max_context_length / 2); //limit the prompt length to max_context_length/4
        topicdata = topicdata.slice(-max_context_length + workPrompt.length); //limit the context length to max_context_length/2
        //right now getting the recent data only.  
        //maybe need to be more random.  
        let fullMessage = await Chat(topicdata + workPrompt, context, null, token);
        roboupdate(topkey, topicdata, fullMessage);
    }
    catch (error) {
        console.error('Error calling Ollama:', error);
    }
}
//only stream being used here.  
async function Chat(prompt, context, stream, token) {
    let ret = "";
    try {
        //connect remote
        //client = ollama.Client(host='http://192.168.1.154:11434')
        //response = client.generate(model='llama3.2b', prompt=my_prompt)
        //actual_response = response['response']
        await Book.read(prompt);
        const response = await ollama_1.default.chat({
            //		model: 'llama3.1:8b',
            model: 'deepseek-coder-v2:latest',
            //deepseek-r1:latest 
            //granite-code:latest
            //codegemma:latest 
            //gemma3n:latest
            //granite3.3:8b
            messages: [{ role: 'user', content: prompt }],
            stream: true,
            /*
                    tools: [{
                        'type': 'function',
                        'function': {
                          'name': 'get_current_weather',
                          'description': 'Get the current weather for a city',
                          'parameters': {
                            'type': 'object',
                            'properties': {
                              'city': {
                                'type': 'string',
                                'description': 'The name of the city',
                              },
                            },
                            'required': ['city'],
                          },
                        },
                      }
                    ],
            */
        });
        for await (const part of response) {
            process.stdout.write(part.message.content);
            if (stream !== null) {
                stream.markdown(part.message.content);
            }
            ret += part.message.content;
            //		if (token.isCancellationRequested) {
            //		  break;
            //		}
            console.log(part.message.tool_calls);
        }
    }
    catch (error) {
        console.error('Error calling Ollama:', error);
    }
    return ret;
}
function getTopicFromLocation(editor) {
    //find last topic.  
    let topic = "";
    let offset = editor.selection.active;
    let topsearch = editor.document.getText(new vscode.Range(0, 0, offset.line, offset.character));
    let topsearches = topsearch.split("\n");
    for (let i = topsearches.length - 1; i >= 0; i--) {
        if (topsearches[i].startsWith("**")) {
            //found a topic
            topic = topsearches[i].substring(2, topsearches[i].length);
            topic = topic.replace(/[\n\r]+/g, '');
            break;
        }
    }
    if (topic === "") {
        //default here if cant find one.  
        topic = Book.selectedtopic;
    }
    return topic;
}
function getTextFromCursor(editor) {
    const selection = editor.selection;
    let text = editor.document.getText(selection);
    let topic = "";
    if (text === "") {
        let offset = editor.selection.active;
        //get the text from the cursor to the end of the line.
        if (offset.character === 0) {
            //select to end of line
            offset = new vscode.Position(offset.line, editor.document.lineAt(offset.line).text.length);
        }
        //					editor.selection = new vscode.Selection(offset.line, 0, offset.line, offset.character);
        text = editor.document.getText(new vscode.Range(offset.line, 0, offset.line, offset.character));
        if (text.length > 1 && text.charAt(0) === '*' && text.charAt(1) === '*') {
            //remove the first character.
            //potential topic.  
            topic = text.substring(2, text.length);
        }
        else {
            topic = getTopicFromLocation(editor);
        }
    }
    return [text, topic];
}
function activate(context) {
    //not being activated until chatted to...
    (0, toolParticipant_1.registerToolUserChatParticipant)(context);
    (0, toolParticipant_1.registerCompletionTool)(context);
    (0, toolParticipant_1.registerStatusBarTool)(context);
    (0, toolParticipant_1.startWatchingWorkspace)(context); //watch for changes to book.  
    Book.open(context); //open the book.  
    // define a chat handler
    const handler = async (request, context, stream, token) => {
        //vscode.window.showInformationMessage('Hello world!');
        // initialize the prompt
        let prompt = BASE_PROMPT;
        console.log(`Chat request: ${request.command} with prompt: ${request.prompt}`);
        const wsUri = vscode.workspace.workspaceFolders[0].uri;
        if (request.command === 'stats') {
            const mySettings = vscode.workspace.getConfiguration('mrrubato');
            stream.markdown('**My agent default prompts**  ' + mySettings.defaultprompts.length + '  \n');
            stream.markdown('**My agent work prompts** ' + mySettings.workprompts.length + '  \n');
            stream.markdown('**My agent run in background** ' + mySettings.runinbackground + '  \n');
            stream.markdown('**My agent run interval** ' + mySettings.runinterval + '  \n');
            stream.markdown('**My agent coding mode** ' + mySettings.codingmode + '  \n');
            stream.markdown('**My agent work prompt** ' + mySettings.workprompt.slice(-255) + '  \n');
        }
        if (request.command === 'summarize' || request.command === 'summary') {
            //find similar topics.  
            //do we have a topic?  
            //do same on Ctrl+Shift+9
            let summary = await Book.summary(request.prompt);
            //replace topics.  
            stream.markdown(await Book.markdown(summary));
            return;
        }
        if (request.command === 'similar') {
            //find similar topics.  
            //do we have a topic?  
            //do same on Ctrl+Shift+9
            let topics = await Book.similar(request.prompt);
            stream.markdown('Similar topics to:  \n' + request.prompt + '  \n');
            let doc = "";
            for (let item of topics) {
                let filename = Book.getUri(item.topic);
                //				doc += `File: ${item.file}, Line: ${item.line}, Sort: ${item.sortorder}  \n`;
                doc += `[${item.topic}](${filename})  \n`;
                let fname = item.file.replace(wsUri.path, '');
                doc += `[${fname}:${item.line}](${item.file}#L${item.line})  \n`;
                let data = item.data.substring(item.topic.length + 2, 300);
                doc += `${data} $$  \n`;
            }
            stream.markdown(doc);
            return;
        }
        if (request.command === 'list') {
            //list the files in the book.  
            if (request.prompt === "prompts") {
                stream.markdown('**Listing prompts**  \n');
                const mySettings = vscode.workspace.getConfiguration('mrrubato');
                //probably dont want this in the future.  
                mySettings.update('runinbackground', true);
                stream.markdown('**My agent default prompts**  \n ' + mySettings.defaultprompts);
                //not in use yet...
                return;
            }
        }
        if (request.command === 'start') {
            //start running in background.
            const mySettings = vscode.workspace.getConfiguration('mrrubato');
            mySettings.update('runinbackground', true);
            stream.markdown('**Starting background agent**  \n ' + mySettings.runinbackground);
            //start the work function here.
            //workPrompt = request.prompt;
            mySettings.update('workprompt', request.prompt);
            work(request, context, stream, token);
            let [topkey, topics] = await Book.read(request.prompt);
            mySettings.workprompts.push({ 'prompt': workPrompt, 'topics': topics, weight: 1 });
            mySettings.update('workprompts', mySettings.workprompts);
            return;
        }
        if (request.command === 'stop') {
            const mySettings = vscode.workspace.getConfiguration('mrrubato');
            //stop running in background.
            mySettings.update('runinbackground', false);
            stream.markdown('**Stopping background agent**  \n' + mySettings.runinbackground);
            return;
        }
        if (request.command === 'exercise') {
            prompt = EXERCISES_PROMPT;
            stream.markdown('**Starting exercise**  \n');
            stream.markdown('**Answering question**  \n');
            await Chat(request.prompt, context, stream, token);
            stream.markdown('  \n**Getting Stats**  \n');
            await getStats(request, context, stream, token);
            stream.markdown('  \n**Exercise complete**  \n');
            //possibly loop here.  
            //test calling another prompt.  
            //not working, may be a feature added in future...
            let options = {
                query: "@tutor /list prompts",
                isPartialQuery: false
            };
            vscode.commands.executeCommand("workbench.action.chat.open", options);
            return;
        }
        if (request.command === 'book') {
            //query book only.  
            stream.markdown('Reading a book\n');
            //get book snippet.  
            readFile();
            Book.updatePage("book/20230110.txt", "hello");
            let myquery = "play with me and use tool #file:definitions.txt"; //calling via # doesnt work.  
            //call external ollama.  
            const { messages } = await (0, prompt_tsx_1.renderPrompt)(prompts_1.PlayPrompt, { userQuery: myquery }, { modelMaxPromptTokens: request.model.maxInputTokens }, request.model);
            const chatResponse = await request.model.sendRequest(messages, {}, token);
            for await (const fragment of chatResponse.text) {
                stream.markdown(fragment);
            }
            //			stream.markdown('```ls -l\n');
            return;
        }
        // initialize the messages array with the prompt
        const messages = [
            vscode.LanguageModelChatMessage.User(prompt),
        ];
        // get all the previous participant messages
        const previousMessages = context.history.filter((h) => h instanceof vscode.ChatResponseTurn);
        // add the previous messages to the messages array
        previousMessages.forEach((m) => {
            let fullMessage = '';
            m.response.forEach((r) => {
                const mdPart = r;
                fullMessage += mdPart.value.value;
            });
            messages.push(vscode.LanguageModelChatMessage.Assistant(fullMessage));
        });
        // add in the user's message
        messages.push(vscode.LanguageModelChatMessage.User(request.prompt));
        // send the request
        const chatResponse = await request.model.sendRequest(messages, {}, token);
        // stream the response
        for await (const fragment of chatResponse.text) {
            stream.markdown(fragment);
        }
        return;
    };
    // create participant
    const tutor = vscode.chat.createChatParticipant("mrrubato.mytutor", handler);
    // add icon to participant
    tutor.iconPath = vscode.Uri.joinPath(context.extensionUri, 'tutor.jpeg');
    //uri handler
    const disposable = vscode.commands.registerCommand('mrrubato.mytutor.start', async () => {
        // Create our new UriHandler
        const uriHandler = new MyUriHandler();
        // And register it with VS Code. You can only register a single UriHandler for your extension.
        context.subscriptions.push(vscode.window.registerUriHandler(uriHandler));
        // You don't have to get the Uri from the `vscode.env.asExternalUri` API but it will add a query
        // parameter (ex: "windowId%3D14") that will help VS Code decide which window to redirect to.
        // If this query parameter isn't specified, VS Code will pick the last windows that was focused.
        const uri = await vscode.env.asExternalUri(vscode.Uri.parse(`${vscode.env.uriScheme}://mrrubato.mytutor`));
        vscode.window.showInformationMessage(`Starting to handle Uris. Open ${uri} in your browser to test.`);
        console.log(`Starting to handle Uris. Open ${uri} in your browser to test.`);
    });
    context.subscriptions.push(disposable);
    //start listening for external URIs.  
    vscode.commands.executeCommand('mrrubato.mytutor.start');
    const searchcommand = vscode.commands.registerCommand('mrrubato.mytutor.search', async (text = "", topic = "") => {
        //what else do we do here?  
        //
        if (text === "") {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                [text, topic] = getTextFromCursor(editor);
                if (text.startsWith("**")) {
                    text = text.substring(2);
                    Book.select(text, Book.BOOK_OPEN_FILE | Book.BOOK_OPEN_WEB); //select and open topic
                }
                console.log("searching for: " + text);
                vscode.commands.executeCommand('workbench.action.findInFiles', {
                    query: text,
                    triggerSearch: true,
                    matchWholeWord: true,
                    isCaseSensitive: false,
                });
            }
        }
    });
    const gencommand = vscode.commands.registerCommand('mrrubato.mytutor.generate', async (text = "", topic = "") => {
        let topiccmd = "";
        if (text === "") {
            //probably should remove header and then run ctrl+shift+f.  
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                [text, topic] = getTextFromCursor(editor);
                if (topic !== "" && topic !== Book.selectedtopic) {
                    //select the topic.  
                    Book.select(topic, 0); //select and open topic
                    //					Book.logCommand("**" + topic); //log the command to genbook.
                    if (text.startsWith("**") > 0) {
                        //we are selecting topic, dont add twice.  
                    }
                    else {
                        topiccmd = "\n**" + topic + "\n";
                    }
                }
            }
        }
        const mySettings = vscode.workspace.getConfiguration('mrrubato');
        let temptext = text;
        //run the desired command here.  
        //export var defstring = "~!@#$%^&*<>/;-+=";
        let tokens = Book.getTokens(text);
        Book.executeTokens(tokens);
        let cmdtype = Book.getCommandType(text);
        if (cmdtype[0] !== "*") {
            //get previous topic.  
        }
        switch (cmdtype[0]) {
            case "^":
                //generate code.  
                switch (cmdtype[1]) {
                    case "^":
                        //generate code from prompt.
                        if (topic === "") {
                            const editor = vscode.window.activeTextEditor;
                            if (editor) {
                                topic = getTopicFromLocation(editor);
                            }
                        }
                        if (text.length < 2) {
                            //generate code for topic.  
                        }
                        else {
                            if (text.charAt(2) === "#") { //generate comments.  
                                //create code comments.  
                                //summarize this topic.
                                if (text.length < 3 || Book.findInputTopics(text).length === 0) {
                                    //summarize current topic.  
                                    text = "**" + topic + " " + text;
                                }
                                //pass topic and chat.  does this work?  Dont remember.  
                                vscode.commands.executeCommand('workbench.action.chat.open', "@mr /similar " + text);
                                break;
                            }
                            else if (text.charAt(2) === "+") {
                                //create code suggestions.  
                            }
                            else if (text.charAt(2) === "-") {
                                //remove code suggestions.  
                                //remove code suggestions for topic.  
                            }
                        }
                        break;
                    default:
                    //generate code suggestions in chat.  
                }
                break;
            case "%":
                switch (cmdtype[1]) {
                    case "%":
                        //work on this topic.  
                        //show work and result if watch=true
                        if (topic === "") {
                            const editor = vscode.window.activeTextEditor;
                            if (editor) {
                                topic = getTopicFromLocation(editor);
                            }
                        }
                        if (text.charAt(2) === "-") {
                            //remove worker.  
                            console.log("Removing worker: " + topic);
                            let removed = await Worker.removeWorker(topic);
                        }
                        else if (text.charAt(2) === "+") {
                            //add worker.  
                            console.log("Adding worker: " + topic);
                            let added = await Worker.addWorker(topic);
                        }
                        console.log("Workers: " + JSON.stringify(Worker.workers));
                        break;
                }
            case ">":
                //run the command.
                switch (cmdtype[1]) {
                    case ">":
                        vscode.commands.executeCommand('workbench.action.terminal.focus');
                        vscode.commands.executeCommand('workbench.action.terminal.sendSequence', { text: text.substring(2) + "\n" });
                        break;
                    default:
                        vscode.commands.executeCommand('workbench.action.terminal.focus');
                        vscode.commands.executeCommand('workbench.action.terminal.sendSequence', { text: text.substring(1) + "\n" });
                        break;
                }
                break;
            case "/":
                //path search only.  
                break;
            case "@":
                //open web link to interact with this question.  
                //aggregate question/response.  
                switch (cmdtype[1]) {
                    case "@":
                        //general question
                        break;
                    default:
                        //find person.  
                        let query = text.split(" ");
                        let entity = query[0].substring(1);
                        let system = entity.split(":")[0];
                        let person = entity.split(":").pop();
                        if (system === person) {
                            //no system specified.
                            //find person.  
                            //use copilot query.  
                            vscode.commands.executeCommand('workbench.action.chat.open', text);
                        }
                        else {
                            //find system.  teams, slack, etc.  
                            //i.e. https://learn.microsoft.com/en-us/graph/api/chatmessage-post?view=graph-rest-1.0&tabs=http
                            //i.e. https://github.com/OfficeDev/Microsoft-Teams-Samples/tree/main/samples/incoming-webhook/nodejs
                            //launch implemented program to talk to other system.  Pass temp file input via cmd.  
                            //lookup command to use for system.  
                            //vscode.commands.executeCommand('workbench.action.terminal.focus');
                            //vscode.commands.executeCommand('workbench.action.terminal.sendSequence', { text: "mycommand " + text + "\n" });
                        }
                        let question = query.slice(1).join(" ");
                        break;
                }
            case "#":
                //open on web.
                vscode.env.openExternal(vscode.Uri.parse(text.substring(1)));
                break;
            case "!":
                //find in log files
                //logdirs
                switch (cmdtype[1]) {
                    case "!":
                        temptext = text.substring(1);
                    default:
                        temptext = temptext.substring(1);
                        console.log("searching for: " + temptext.substring(1));
                        vscode.commands.executeCommand('workbench.action.findInFiles', {
                            query: text,
                            triggerSearch: true,
                            matchWholeWord: true,
                            isCaseSensitive: false,
                        });
                        break;
                }
                break;
            case "$":
                //find env variables
                switch (cmdtype[1]) {
                    case '$':
                        if (text.length < 3) {
                            //list env variables.  
                            Book.printENV();
                        }
                        else {
                            if (text.charAt(2) === "-") {
                                let kv = text.substring(3).split("=");
                                if (kv.length === 1) {
                                    if (kv[0].substring(0, 2) === "**") {
                                        Book.removeFromHistory(kv[0].substring(2));
                                    }
                                    else {
                                        Book.removeFromEnvironment(kv[0]);
                                    }
                                }
                                Book.printENV();
                            }
                            else if (text.charAt(2) === "+") {
                                let kv = text.substring(3).split("=");
                                if (kv.length === 2) {
                                    Book.addToEnvironment(kv[0], kv[1]);
                                }
                                else if (kv.length === 1) {
                                    //show variable value
                                    if (kv[0].substring(0, 2) === "**") {
                                        Book.addToHistory(kv[0].substring(2));
                                    }
                                }
                                Book.printENV();
                            }
                        }
                        //add to book.  
                        //						const fileUri = folder.with({ path: posix.join(folder.path, name) });
                        //						Book.loadPage(text, fileUri); //load the ENV for completion.  
                        //add new variable
                        //list variables and values.  
                        //$$
                        //show variable
                        //$$key
                        //set variable
                        //$$key=value
                        break;
                }
                break;
            case "-":
                //find env variables
                //add the next "-" lines to book.  
                //single is single line.  
                break;
            case "+":
                //find env variables
                break;
            case "*":
                //open the topic
                console.log("Opening topic: " + text);
                switch (cmdtype[1]) {
                    case "*":
                        temptext = text.substring(2);
                        Book.select(temptext); //select and open topic
                        break;
                    case "#":
                        //open references.html?topic=
                        break;
                    case "-":
                        //open book contents topic= 
                        break;
                    case "/":
                        //start thinking about topic
                        break;
                    case "$":
                        //open page.html?topic=
                        //show env info.  
                        break;
                    case "%":
                        //open graph.html?topic=
                        break;
                }
                break;
            case ":":
                //summarize this topic. 
                switch (cmdtype[1]) {
                    case ":":
                        //summarize this topic.
                        if (text.length < 3 || Book.findInputTopics(text).length === 0) {
                            //summarize current topic.  
                            const editor = vscode.window.activeTextEditor;
                            if (editor) {
                                topic = getTopicFromLocation(editor);
                                text = "**" + topic + " " + text;
                            }
                        }
                        else {
                            //pass topic and chat.  does this work?  Dont remember.  
                            vscode.commands.executeCommand('workbench.action.chat.open', "@mr /summary " + text);
                        }
                        break;
                    default:
                        //summarize this topic with a different prompt.
                        //no single char handler.  
                        break;
                }
            case "~":
                //summarize this topic. 
                switch (cmdtype[1]) {
                    case "~":
                        //summarize this topic.
                        if (text.length < 3 || Book.findInputTopics(text).length === 0) {
                            //summarize current topic.  
                            const editor = vscode.window.activeTextEditor;
                            if (editor) {
                                topic = getTopicFromLocation(editor);
                                text = "**" + topic + " " + text;
                            }
                        }
                        //pass topic and chat.  does this work?  Dont remember.  
                        vscode.commands.executeCommand('workbench.action.chat.open', "@mr /similar " + text);
                        break;
                    default:
                        //no single char handler.  
                        break;
                }
            case "":
                //failure return?  
                break;
        }
        //log the command to genbook if valid.  
        Book.logCommand(topiccmd + text);
        //copy to the clipboard anyway by default.  
        //if wanting to use in different environment.  
        //not sure if this is needed or not.
        //		vscode.env.clipboard.writeText(text);
        /*
        vscode.env.clipboard.readText().then((text)=>{
            clipboard_content = text;
        });
        */
    });
    context.subscriptions.push(disposable);
    //start the MCP server as well.  
    //vscode.commands.createMcpServer('mrrubato.mytutor', tutor);
    activeEditor = vscode.window.activeTextEditor;
    vscode.workspace.onDidSaveTextDocument((document) => {
        if (document.languageId === "plaintext" && document.uri.scheme === "file") {
            // do work
            triggerUpdateDecorations();
            triggerGetBookContext();
            (0, toolParticipant_1.updateStatusBarItem)();
        }
    });
    vscode.window.onDidChangeActiveTextEditor(editor => {
        activeEditor = editor;
        if (editor) {
            triggerUpdateDecorations();
            triggerGetBookContext();
            (0, toolParticipant_1.updateStatusBarItem)();
        }
    }, null, context.subscriptions);
}
let uitimeout = undefined;
//#https://code.visualstudio.com/api/references/vscode-api#DecorationRenderOptions
const smallNumberDecorationType = vscode.window.createTextEditorDecorationType({
    borderWidth: '1px',
    borderStyle: 'solid',
    overviewRulerColor: 'blue',
    overviewRulerLane: vscode.OverviewRulerLane.Right,
    light: {
        // this color will be used in light color themes
        borderColor: 'darkblue'
    },
    dark: {
        // this color will be used in dark color themes
        borderColor: 'lightblue'
    }
});
// create a decorator type that we use to decorate large numbers
const largeNumberDecorationType = vscode.window.createTextEditorDecorationType({
    cursor: 'crosshair',
    // use a themable color. See package.json for the declaration and default values.
    backgroundColor: { id: 'myextension.largeNumberBackground' }
});
function updateDecorations() {
    if (!activeEditor) {
        return;
    }
    const regEx = /\d+/g;
    const text = activeEditor.document.getText();
    const smallNumbers = [];
    const largeNumbers = [];
    let match;
    while ((match = regEx.exec(text))) {
        const startPos = activeEditor.document.positionAt(match.index);
        const endPos = activeEditor.document.positionAt(match.index + match[0].length);
        const decoration = { range: new vscode.Range(startPos, endPos), hoverMessage: 'Number **' + match[0] + '**' };
        if (match[0].length < 3) {
            smallNumbers.push(decoration);
        }
        else {
            largeNumbers.push(decoration);
        }
    }
    activeEditor.setDecorations(smallNumberDecorationType, smallNumbers);
    activeEditor.setDecorations(largeNumberDecorationType, largeNumbers);
}
function triggerUpdateDecorations(throttle = false) {
    if (throttle) {
        uitimeout = setTimeout(updateDecorations, 500);
    }
    else {
        updateDecorations();
    }
}
function getBookContext() {
    //
    if (!activeEditor) {
        return vscode.window.showInformationMessage('No active editor found');
    }
    console.log("getBookContext: " + activeEditor.document.uri.toString()); // + activeEditor.document);
}
function triggerGetBookContext(throttle = false) {
    if (throttle) {
        uitimeout = setTimeout(getBookContext, 500);
    }
    else {
        getBookContext();
    }
}
async function getStats(request, context, stream, token) {
    if (!vscode.workspace.workspaceFolders) {
        return vscode.window.showInformationMessage('No folder or workspace opened');
    }
    async function countAndTotalOfFilesInFolder(folder) {
        let total = 0;
        let count = 0;
        for (const [name, type] of await vscode.workspace.fs.readDirectory(folder)) {
            if (type === vscode.FileType.File) {
                const filePath = path_1.posix.join(folder.path, name);
                const stat = await vscode.workspace.fs.stat(folder.with({ path: filePath }));
                total += stat.size;
                count += 1;
            }
        }
        return { total, count };
    }
    if (!vscode.window.activeTextEditor) {
        return vscode.window.showInformationMessage('Open a file first');
    }
    const fileUri = vscode.window.activeTextEditor.document.uri;
    if (fileUri.scheme !== 'file') {
        return vscode.window.showInformationMessage('Open an existing file first');
    }
    const folderPath = path_1.posix.dirname(fileUri.path);
    const folderUri = fileUri.with({ path: folderPath });
    const info = await countAndTotalOfFilesInFolder(folderUri);
    //show this as message.  
    stream.markdown(`${info.count} files in ${folderUri.toString(true)} with a total of ${info.total} bytes\n`);
    //	const doc = await vscode.workspace.openTextDocument({ content: `${info.count} files in ${folderUri.toString(true)} with a total of ${info.total} bytes` });
    //	vscode.window.showTextDocument(doc, { viewColumn: vscode.ViewColumn.Beside });
}
function readFile(fname = "book/definitions.txt") {
    if (!vscode.workspace.workspaceFolders) {
        return vscode.window.showInformationMessage('No folder or workspace opened');
    }
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    // this should be a book path.  Use as you would work on the project.  
    const fileUri = folderUri.with({ path: path_1.posix.join(folderUri.path, fname) });
    //	const fileUri = folderUri.with({ path: posix.join(folderUri.path, 'definitions.txt') });
    vscode.window.showTextDocument(fileUri);
    vscode.workspace.openTextDocument(fileUri).then((document) => {
        let text = document.getText();
        console.log(text);
        // Optionally insert the text into the active editor
        //		insertTextIntoActiveEditor(text);
    });
}
/**
 * Inserts text into the active text editor at the current cursor position
 * @param text The text to insert
 * @returns A promise that resolves when the edit is applied
 */
function insertTextIntoActiveEditor(text) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor found');
        return undefined;
    }
    try {
        return editor.edit(editBuilder => {
            // Insert at each selection
            editor.selections.forEach(selection => {
                editBuilder.insert(selection.active, text);
            });
        }).then(success => {
            if (success) {
                vscode.window.showInformationMessage('Text inserted successfully');
            }
            else {
                vscode.window.showErrorMessage('Failed to insert text');
            }
            return success;
        });
    }
    catch (error) {
        vscode.window.showErrorMessage(`Error inserting text: ${error instanceof Error ? error.message : String(error)}`);
        return Promise.resolve(false);
    }
}
// This method is called when your extension is deactivated
function deactivate() { }
class MyUriHandler {
    // This function will get run when something redirects to VS Code
    // with your extension id as the authority.
    handleUri(uri) {
        console.log(`Handling Uri: ${uri.toString()}`);
        let message = "Handled a Uri!";
        if (uri.query) {
            message += ` It came with this query: ${uri.query}`;
        }
        vscode.window.showInformationMessage(message);
    }
}
//# sourceMappingURL=extension.js.map