import { renderPrompt } from '@vscode/prompt-tsx';
import * as vscode from 'vscode';
import * as Book from './book';
import * as fs from 'fs';
import * as transcriber from './transcriber';
import { ToolCallRound, ToolResultMetadata, ToolUserPrompt } from './toolsPrompt';

import mmap from '@riaskov/mmap-io';

let myStatusBarItem: vscode.StatusBarItem;


import * as midiin from './midi/midi-in';
import * as tree from './midi/tree';

//import midiin from './midi/midi-in.js';
//import tree from './midi/tree.js';
//
//const midiin = require('./midi/midi-in');
//const tree = require('./midi/tree');


export interface TsxToolUserMetadata {
    toolCallsMetadata: ToolCallsMetadata;
}

export interface ToolCallsMetadata {
    toolCallRounds: ToolCallRound[];
    toolCallResults: Record<string, vscode.LanguageModelToolResult>;
}

export function isTsxToolUserMetadata(obj: unknown): obj is TsxToolUserMetadata {
    // If you change the metadata format, you would have to make this stricter or handle old objects in old ChatRequest metadata
    return !!obj &&
        !!(obj as TsxToolUserMetadata).toolCallsMetadata &&
        Array.isArray((obj as TsxToolUserMetadata).toolCallsMetadata.toolCallRounds);
}

function positionToString(pos: vscode.Position): string {
    return `[${pos.line},${pos.character}]`;
}

function editorRanges(prefix: string, editor: vscode.TextEditor | undefined) {
    if (editor === undefined) { return; }
    if (editor.visibleRanges.length === 1) {
        let visibleRange = editor.visibleRanges[0];
//        console.log(`${prefix} visible ${positionToString(visibleRange.start)} ${positionToString(visibleRange.end)}  selectionStart ${positionToString(editor.selection.start)} selectionEnd ${positionToString(editor.selection.end)}`);
        editor.document.getText(visibleRange).split('\n').forEach((line, index) => {
//            console.log(`line ${index + visibleRange.start.line}: ${line}`);
            //add this to context.  
        });
    }
};

export function registerStatusBarTool(context: vscode.ExtensionContext) {
	const myCommandId = 'sample.showSelectionCount';
	context.subscriptions.push(vscode.commands.registerCommand(myCommandId, () => {
		const n = getNumberOfSelectedLines(vscode.window.activeTextEditor);
		vscode.window.showInformationMessage(`Yeah, ${n} line(s) selected... Keep going!`);
	}));

	// create a new status bar item that we can now manage
	myStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
	myStatusBarItem.command = myCommandId;
	context.subscriptions.push(myStatusBarItem);

	// register some listener that make sure the status bar 
	// item always up-to-date
	context.subscriptions.push(vscode.window.onDidChangeTextEditorSelection(changeEvent => { 
        updateStatusBarItem(); 
    }));


//    vscode.window.onDidChangeTextEditorSelection( changeEvent => { editorRanges('selection changed: ', changeEvent.textEditor); }, null, context.subscriptions);
//    vscode.window.onDidChangeTextEditorVisibleRanges( changeEvent => { editorRanges('visible ranges changed: ', changeEvent.textEditor); }, null, context.subscriptions);

	// update status bar item once at start
	updateStatusBarItem();
}

export function updateStatusBarItem() {

    editorRanges('updateStatusBarItem: ', vscode.window.activeTextEditor);
	const n = getNumberOfSelectedLines(vscode.window.activeTextEditor);

	if (n > 0) {
		myStatusBarItem.text = `$(megaphone) ${n} line(s) selected`;
		myStatusBarItem.show();
	} else {
		myStatusBarItem.hide();
	}
}

function getNumberOfSelectedLines(editor: vscode.TextEditor | undefined): number {
	let lines = 0;
	if (editor) {
		lines = editor.selections.reduce((prev, curr) => prev + (curr.end.line - curr.start.line), 0);
	}
	return lines;
}

export function registerCompletionTool(context: vscode.ExtensionContext){

    //need multiple providers for "*", "#", ">", "@", "="
    //# -> refs
    //> -> commands
    //@ -> users
    //@@ -> questions
    //== -> answers

    const provider2 = vscode.languages.registerCompletionItemProvider(
        'plaintext',
        {
            provideCompletionItems(document: vscode.TextDocument, position: vscode.Position) {

                // get all text until the `position` and check if it reads `console.`
                // and if so then complete if `log`, `warn`, and `error`
                let myarray = [];


                let linePrefix = document.lineAt(position).text.slice(0, position.character);
                if (position.character === 0) {
                    //new line, get previous line.  
                    //if topic, then logCommand.  
                    //not a good idea to do this here.  
                    /*
                    linePrefix = document.lineAt(position.line-1).text;
                    if (linePrefix.startsWith('**')) {
                        //if it is a topic, then logCommand.  
                        Book.addToHistory(linePrefix.substring(2));
                        Book.logCommand(linePrefix);
                    }
                    */
                }
                if (linePrefix.endsWith('**')) {

                    console.log(Book.topicarray);
                    myarray = Book.findTopicsCompletion("");
                    return myarray;
                }

                keyfind: for (let j=Book.defmap.length-1; j>=0; j--) {
                    for (const [k, v] of Object.entries(Book.defmap[j])) {
                        //for now excluding the '-' key.
                        if (linePrefix.endsWith(k)) {
                            if (k.length ===1 && !linePrefix.startsWith(k)) {
                                //cant do autocomplete for single characters.  
                                //only from two characters to prevent overautocomplete.  
                                continue;
                            }
                            else{
                                for (const [key, value] of Object.entries(Book.arrays[k])) {

                                    if (value !== undefined && value.length > 0) {

                                        let ci = new vscode.CompletionItem(key, vscode.CompletionItemKind.Text);
                                        ci.detail = `${k}: ${key}`;
                                        let doc = "";
                                        let sortText = "0000";
                                        for (let item of value) {
                                            doc = Book.itemToDoc(item);
            
                                            //set sortText to top if it is in selection history.  
                                            const found = Book.selectionhistory.findIndex((t) => t === item.topic);
                                            if (found > -1){
                                                sortText = (Book.MAX_SELECTION_HISTORY-found).toString(16).padStart(4, '0').toUpperCase();
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
                        }
                    }
                }
                if (linePrefix.endsWith('>') && linePrefix.startsWith('>')) {
                    console.log(Book.arrays['>']);
                    for (const [key, value] of Object.entries(Book.arrays['>'])) {
                        if (value !== undefined && value.length > 0) {

                            let ci = new vscode.CompletionItem(key, vscode.CompletionItemKind.Text);
                            ci.detail = `Command: ${key}`;
                            let doc = "";
                            let sortText = "0000";
                            for (let item of value) {
                                doc = Book.itemToDoc(item);

                                //set sortText to top if it is in selection history.  
                                const found = Book.selectionhistory.findIndex((t) => t === item.topic);
                                if (found > -1){
                                    sortText = (Book.MAX_SELECTION_HISTORY-found).toString(16).padStart(4, '0').toUpperCase();
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
                if (linePrefix.endsWith('/')){
                    //include all topics with this.  


                    //need sorted keys.  
//                    console.log(Book.topicarray);
                    //allow to trigger even if we have already completed.  
                    if (linePrefix.startsWith('**')){

                    }
                    else if (linePrefix.substring(linePrefix.lastIndexOf(' ')+1).startsWith('**')){
                        //adjust linePrefix to be just the topic.
                        linePrefix = linePrefix.substring(linePrefix.lastIndexOf(' ')+1);
                    }
                    let myarray = Book.findTopicsCompletion(linePrefix);
                        //use Book.alltopics to get sorted array.  
                    return myarray;


                }
                else{
                    /*
                    for (const [key, value] of Object.entries(Book.topicarray)) {
                        if (value !== undefined && value.length > 0) {
                            let ci = new vscode.CompletionItem(key, vscode.CompletionItemKind.Text);
                            ci.detail = `Topic: ${key}`;
                            let doc = "";
                            for (let item of value) {
                                doc += `File: ${item.file}, Line: ${item.line}, Sort: ${value[0].sortorder}\n`;
                                doc += `Link: [${item.file}](${item.file}#L${item.line})\n`;
                            }
                            ci.documentation = new vscode.MarkdownString(`${doc}`);
                            ci.sortText = value[0].sortorder.toString(16).padStart(4, '0').toUpperCase();
                            myarray.push(ci);
                        }                    
                    }
                    */
                    return myarray;
                }
            }
        },
        '*', //trigger single character
        '>',
        '/', //trigger on '/'
        '#', 
        '@',
        '!', 
        '-', 
        '$', 
//        '\n', //trigger on newline
        //not sure this is a good idea.  Seems to work ok.  


        //switch from '.' to '**' to trigger on '**' instead 
    );
    //add custom completions to the extension 
    context.subscriptions.push(provider2);
}


function getWorkspaceTestPatterns() {
	if (!vscode.workspace.workspaceFolders) {
		return [];
	}

    let bookPath = Book.getBookPath();
	return vscode.workspace.workspaceFolders.map(workspaceFolder => ({
		workspaceFolder,
		pattern: new vscode.RelativePattern(workspaceFolder.uri.path + "/" + bookPath, '**/*.txt'),
	}));
}


//this may reload unnecessarily.  
export function startWatchingWorkspace(context: vscode.ExtensionContext) {
	return context.subscriptions.push(...getWorkspaceTestPatterns().map(({ pattern }) => {
		const watcher = vscode.workspace.createFileSystemWatcher(pattern);

		watcher.onDidCreate(fileUri => {
            vscode.workspace.openTextDocument(fileUri).then((document) => {
                let text = document.getText();
                console.log(`${fileUri.path} ... read`);
                // parse this.  
                Book.loadPage(text, fileUri.path);
            });

		});
		watcher.onDidChange(async fileUri => {
            vscode.workspace.openTextDocument(fileUri).then((document) => {
                let text = document.getText();
                console.log(`${fileUri.path} ... read`);
                // parse this.  
                Book.loadPage(text, fileUri.path);
            });

		});



		return watcher;
	}));
}


export function stopWatchingMMAP(name: string){
    let basePath = "temp/";
    fs.unwatchFile(basePath + name);
}


//use for monitoring topic state changes when selecting times and filters..
export function startWatchingMMAP(name: string){
    //watch the mmap file for changes and update the book accordingly.
    let basePath = "temp/";

    //read initial if exists..
    if (fs.existsSync(basePath + name)) {
        const file = fs.openSync(basePath + name, 'r');
        const stats = fs.fstatSync(file);
        const data = Buffer.alloc(stats.size);
        fs.readSync(file, data, 0, stats.size, 0);
        const content = data.toString();
        console.log(`Initial read of MMAP file ${name}, size: ${stats.size}`);
        // Book.loadPage(content, "mmap:" + name);
    }

    fs.watchFile(basePath + name, { interval: 3000 }, (curr, prev) => {
        if (curr.mtimeMs !== prev.mtimeMs) {
            const file = fs.openSync(basePath + name, 'r+');
            const data = Buffer.alloc(curr.size);
            fs.readSync(file, data, 0, curr.size, 0);
            const content = data.toString();

//            const newBuf = mmap.map(curr.size, mmap.MAP_SHARED, file, 0);
            // Process the new data in newBuf
            console.log(`MMAP file ${name} changed, new size: ${curr.size}`);
            // For example, you could parse the new data and update the book accordingly
            // Book.loadPage(newBuf.toString(), "mmap:" + name);
        }
    });


}

export function startWatchingTranscriber(lang: string, transcriptFolder: string = "C:/devinpiano/transcripts/"){
    //watch the transcriber folder for changes and update the book accordingly.
    //get fname as YYYYMMDD.txt
    let now = Book.formatDate();
    let fname = `${transcriptFolder}${lang}/${now}.txt`;

    if (!fs.existsSync(fname)) {
        //create the file if it doesn't exist.  
        fs.writeFileSync(fname, "");
    }
    fs.readFile(fname, 'utf8', (err, data) => {
        if (err) {
            console.error(`Error reading file ${fname}:`, err);
        }
        else{
            console.log(`File ${fname} read successfully.`);
            let topics = transcriber.transcribe(data, now); //use date as initial topic.);
            if (topics.length > 0){
                let topic = topics[topics.length-1].topic;
                Book.addToHistory(topic);

            }

        }
    });

    //is default 5000 ms ok
    fs.watchFile(fname, { interval: 5000 }, (curr, prev) => {
        if (curr.size !== prev.size && curr.size > prev.size) {
            const stream = fs.createReadStream(fname, { start: prev.size, end: curr.size });
            let incomingData = '';
            stream.on('data', (chunk) => {
                incomingData += chunk.toString();
                console.log(`Received chunk of data: ${chunk.toString()}`);
            });

            stream.on('error', (error) => {
                console.error('Error reading stream:', error);
            });
            
            stream.on('end', () => {
                console.log('Finished reading stream.');
                let topics = transcriber.transcribe(incomingData, Book.selectedtopic); //use selected topic to start..
                console.log("Transcribed topics:", topics);
                let today = new Date();
                let todaydate = today.getFullYear()*10000 + (today.getMonth()+1)*100 + today.getDate();
                let file = todaydate + ".txt";
                if (topics.length > 0){
                    //read commands and do something..
                    let topic = topics[topics.length-1];
                    //open topic if not already open..
                    console.log("Current topic:", Book.selectedtopic);
                    console.log("Adding to history and selecting topic ", topic);
                    if (topic.topic !== Book.selectedtopic){
                        //only add to history if topic has changed.  
                        Book.updatePage(Book.getBookPath() + "/" + file, '**' + transcriber.current_topic + '\n', -1, -1); //append to end of file.
                        
                        Book.addToHistory(topic.topic);
                        Book.select(topic.topic);
                        vscode.commands.executeCommand('workbench.action.chat.open', "@mr /read " + "**" + topic.topic );

                        //for now just open if it exists..


                        for (let l of topic.data.split('\n')){
                            if (l.startsWith("Pause")){
                                vscode.commands.executeCommand('workbench.action.chat.open', "@mr /stop");
                            }
                        }
                    }
                    for (let cmd of topic.cmds){
                        console.log("Processing command: ", cmd);
                        //for now just log the command.  In the future we can do something with it.
                        if (cmd.cmd === "Pause"){
                            vscode.commands.executeCommand('workbench.action.chat.open', "@mr /stop");
                        }
                        if (cmd.cmd === "Record Feedback"){
                            //do something with the feedback.  For now just log it.
                            let input = "";
                            if (cmd.vars && cmd.vars['FEEDBACK']){
                                input = cmd.vars['FEEDBACK'] + '\n';
                            }
                            if (cmd.vars && cmd.vars['ORIGINAL']){
                                input = cmd.vars['ORIGINAL'] + "\n";
                            }
                            //add data to file..

//                            Book.updatePage("book/" + topic.topic, input);
                            //get todays date for filename.  

                            Book.updatePage(Book.getBookPath() + "/" + file, input, -1, -1); //append to end of file.

                        }
                        if (cmd.cmd === "Time Jump" || cmd.cmd === "Time Zoom"){
                            //see what time is set and adjust topic selection accordingly..
                            let t = Date.now()/1000;
                            if (cmd.vars && cmd.vars['TIME']){
                                t = parseFloat(cmd.vars['TIME']);
                            }
                            let w = 86400; // default 1 day
                            if (cmd.vars && cmd.vars['WINDOW']){
                                w = parseFloat(cmd.vars['WINDOW']);
                            }
                            let s = t - w/2;
                            if (cmd.vars && cmd.vars['START']){
                                s = parseFloat(cmd.vars['START']);
                            }
                            let e = t + w/2;
                            if (cmd.vars && cmd.vars['END']){
                                e = parseFloat(cmd.vars['END']);
                            }
                            console.log(`Time Jump/Zoom to ${new Date(s*1000).toISOString()} - ${new Date(e*1000).toISOString()}`);
                            Book.setTime(t, s, e, w);

                        }
                    }

                }
            });            
        }
    });

}

export function registerToolUserChatParticipant(context: vscode.ExtensionContext) {
    const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, chatContext: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {
        if (request.command === 'list') {
            stream.markdown(`Available tools: ${vscode.lm.tools.map(tool => tool.name).join(', ')}\n\n`);
            return;
        }

        let model = request.model;
        if (model.vendor === 'copilot' && model.family.startsWith('o1')) {
            // The o1 models do not currently support tools
            const models = await vscode.lm.selectChatModels({
                vendor: 'copilot',
                family: 'gpt-4o'
            });
            model = models[0];
        }

        // Use all tools, or tools with the tags that are relevant.
        const tools = request.command === 'all' ?
            vscode.lm.tools :
            vscode.lm.tools.filter(tool => tool.tags.includes('mcpiano'));
        const options: vscode.LanguageModelChatRequestOptions = {
            justification: 'To make a request to @toolsTSX',
        };

        // Render the initial prompt
        const result = await renderPrompt(
            ToolUserPrompt,
            {
                context: chatContext,
                request,
                toolCallRounds: [],
                toolCallResults: {}
            },
            { modelMaxPromptTokens: model.maxInputTokens },
            model);
        let messages = result.messages;
        result.references.forEach(ref => {
            if (ref.anchor instanceof vscode.Uri || ref.anchor instanceof vscode.Location) {
                stream.reference(ref.anchor);
            }
        });

        const toolReferences = [...request.toolReferences];
        const accumulatedToolResults: Record<string, vscode.LanguageModelToolResult> = {};
        const toolCallRounds: ToolCallRound[] = [];
        const runWithTools = async (): Promise<void> => {
            // If a toolReference is present, force the model to call that tool
            const requestedTool = toolReferences.shift();
            if (requestedTool) {
                options.toolMode = vscode.LanguageModelChatToolMode.Required;
                options.tools = vscode.lm.tools.filter(tool => tool.name === requestedTool.name);
            } else {
                options.toolMode = undefined;
                options.tools = [...tools];
            }

            // Send the request to the LanguageModelChat
            const response = await model.sendRequest(messages, options, token);

            // Stream text output and collect tool calls from the response
            const toolCalls: vscode.LanguageModelToolCallPart[] = [];
            let responseStr = '';
            for await (const part of response.stream) {
                if (part instanceof vscode.LanguageModelTextPart) {
                    stream.markdown(part.value);
                    responseStr += part.value;
                } else if (part instanceof vscode.LanguageModelToolCallPart) {
                    toolCalls.push(part);
                }
            }

            if (toolCalls.length) {
                // If the model called any tools, then we do another round- render the prompt with those tool calls (rendering the PromptElements will invoke the tools)
                // and include the tool results in the prompt for the next request.
                toolCallRounds.push({
                    response: responseStr,
                    toolCalls
                });
                const result = (await renderPrompt(
                    ToolUserPrompt,
                    {
                        context: chatContext,
                        request,
                        toolCallRounds,
                        toolCallResults: accumulatedToolResults
                    },
                    { modelMaxPromptTokens: model.maxInputTokens },
                    model));
                messages = result.messages;
                const toolResultMetadata = result.metadatas.getAll(ToolResultMetadata);
                if (toolResultMetadata?.length) {
                    // Cache tool results for later, so they can be incorporated into later prompts without calling the tool again
                    toolResultMetadata.forEach(meta => accumulatedToolResults[meta.toolCallId] = meta.result);
                }

                // This loops until the model doesn't want to call any more tools, then the request is done.
                return runWithTools();
            }
        };

        await runWithTools();

        return {
            metadata: {
                // Return tool call metadata so it can be used in prompt history on the next request
                toolCallsMetadata: {
                    toolCallResults: accumulatedToolResults,
                    toolCallRounds
                }
            } satisfies TsxToolUserMetadata,
        };
    };

    const toolUser = vscode.chat.createChatParticipant('chat-tools-sample.tools', handler);
    toolUser.iconPath = new vscode.ThemeIcon('tools');
    context.subscriptions.push(toolUser);
}


export function registerPiano(context: vscode.ExtensionContext) {
    midiin.activate(context);
    tree.activate(context);
    

}

export function unregisterPiano() {
    midiin.deactivate();
    tree.deactivate();
}