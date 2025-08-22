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
exports.isTsxToolUserMetadata = isTsxToolUserMetadata;
exports.registerStatusBarTool = registerStatusBarTool;
exports.updateStatusBarItem = updateStatusBarItem;
exports.registerCompletionTool = registerCompletionTool;
exports.startWatchingWorkspace = startWatchingWorkspace;
exports.registerToolUserChatParticipant = registerToolUserChatParticipant;
const prompt_tsx_1 = require("@vscode/prompt-tsx");
const vscode = __importStar(require("vscode"));
const Book = __importStar(require("./book"));
const toolsPrompt_1 = require("./toolsPrompt");
let myStatusBarItem;
function isTsxToolUserMetadata(obj) {
    // If you change the metadata format, you would have to make this stricter or handle old objects in old ChatRequest metadata
    return !!obj &&
        !!obj.toolCallsMetadata &&
        Array.isArray(obj.toolCallsMetadata.toolCallRounds);
}
function positionToString(pos) {
    return `[${pos.line},${pos.character}]`;
}
function editorRanges(prefix, editor) {
    if (editor === undefined) {
        return;
    }
    if (editor.visibleRanges.length === 1) {
        let visibleRange = editor.visibleRanges[0];
        //        console.log(`${prefix} visible ${positionToString(visibleRange.start)} ${positionToString(visibleRange.end)}  selectionStart ${positionToString(editor.selection.start)} selectionEnd ${positionToString(editor.selection.end)}`);
        editor.document.getText(visibleRange).split('\n').forEach((line, index) => {
            //            console.log(`line ${index + visibleRange.start.line}: ${line}`);
            //add this to context.  
        });
    }
}
;
function registerStatusBarTool(context) {
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
function updateStatusBarItem() {
    editorRanges('updateStatusBarItem: ', vscode.window.activeTextEditor);
    const n = getNumberOfSelectedLines(vscode.window.activeTextEditor);
    if (n > 0) {
        myStatusBarItem.text = `$(megaphone) ${n} line(s) selected`;
        myStatusBarItem.show();
    }
    else {
        myStatusBarItem.hide();
    }
}
function getNumberOfSelectedLines(editor) {
    let lines = 0;
    if (editor) {
        lines = editor.selections.reduce((prev, curr) => prev + (curr.end.line - curr.start.line), 0);
    }
    return lines;
}
function registerCompletionTool(context) {
    //need multiple providers for "*", "#", ">", "@", "="
    //# -> refs
    //> -> commands
    //@ -> users
    //@@ -> questions
    //== -> answers
    const provider2 = vscode.languages.registerCompletionItemProvider('plaintext', {
        provideCompletionItems(document, position) {
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
            keyfind: for (let j = Book.defmap.length - 1; j >= 0; j--) {
                for (const [k, v] of Object.entries(Book.defmap[j])) {
                    //for now excluding the '-' key.
                    if (linePrefix.endsWith(k)) {
                        if (k.length === 1 && !linePrefix.startsWith(k)) {
                            //cant do autocomplete for single characters.  
                            //only from two characters to prevent overautocomplete.  
                            continue;
                        }
                        else {
                            for (const [key, value] of Object.entries(Book.arrays[k])) {
                                if (value !== undefined && value.length > 0) {
                                    let ci = new vscode.CompletionItem(key, vscode.CompletionItemKind.Text);
                                    ci.detail = `${k}: ${key}`;
                                    let doc = "";
                                    let sortText = "0000";
                                    for (let item of value) {
                                        let filename = Book.getUri(item.topic);
                                        doc += `File: ${item.file}, Line: ${item.line}, Sort: ${item.sortorder}  \n`;
                                        doc += `Topic: [${item.topic}](${filename})  \n`;
                                        doc += `Link: [${item.file}](${item.file}#L${item.line})  \n`;
                                        let data = item.data.substring(0, 255);
                                        doc += `Data: ${data}  \n`;
                                        //set sortText to top if it is in selection history.  
                                        const found = Book.selectionhistory.findIndex((t) => t === item.topic);
                                        if (found > -1) {
                                            sortText = (Book.MAX_SELECTION_HISTORY - found).toString(16).padStart(4, '0').toUpperCase();
                                        }
                                    }
                                    ci.documentation = new vscode.MarkdownString(`${doc}`);
                                    if (sortText === "0000") {
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
                            let filename = Book.getUri(item.topic);
                            doc += `File: ${item.file}, Line: ${item.line}, Sort: ${item.sortorder}  \n`;
                            doc += `Topic: [${item.topic}](${filename})  \n`;
                            doc += `Link: [${item.file}](${item.file}#L${item.line})  \n`;
                            let data = item.data.substring(0, 255);
                            doc += `Data: ${data}  \n`;
                            //set sortText to top if it is in selection history.  
                            const found = Book.selectionhistory.findIndex((t) => t === item.topic);
                            if (found > -1) {
                                sortText = (Book.MAX_SELECTION_HISTORY - found).toString(16).padStart(4, '0').toUpperCase();
                            }
                        }
                        ci.documentation = new vscode.MarkdownString(`${doc}`);
                        if (sortText === "0000") {
                            sortText = value[0].sortorder.toString(16).padStart(4, '0').toUpperCase();
                        }
                        ci.sortText = sortText;
                        myarray.push(ci);
                    }
                }
                return myarray;
            }
            if (linePrefix.endsWith('/')) {
                //include all topics with this.  
                //need sorted keys.  
                //                    console.log(Book.topicarray);
                //allow to trigger even if we have already completed.  
                if (linePrefix.startsWith('**')) {
                }
                else if (linePrefix.substring(linePrefix.lastIndexOf(' ') + 1).startsWith('**')) {
                    //adjust linePrefix to be just the topic.
                    linePrefix = linePrefix.substring(linePrefix.lastIndexOf(' ') + 1);
                }
                let myarray = Book.findTopicsCompletion(linePrefix);
                //use Book.alltopics to get sorted array.  
                return myarray;
            }
            else {
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
    }, '*', //trigger single character
    '>', '/', //trigger on '/'
    '#', '@', '!', '-', '$');
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
function startWatchingWorkspace(context) {
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
        watcher.onDidChange(async (fileUri) => {
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
function registerToolUserChatParticipant(context) {
    const handler = async (request, chatContext, stream, token) => {
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
        const options = {
            justification: 'To make a request to @toolsTSX',
        };
        // Render the initial prompt
        const result = await (0, prompt_tsx_1.renderPrompt)(toolsPrompt_1.ToolUserPrompt, {
            context: chatContext,
            request,
            toolCallRounds: [],
            toolCallResults: {}
        }, { modelMaxPromptTokens: model.maxInputTokens }, model);
        let messages = result.messages;
        result.references.forEach(ref => {
            if (ref.anchor instanceof vscode.Uri || ref.anchor instanceof vscode.Location) {
                stream.reference(ref.anchor);
            }
        });
        const toolReferences = [...request.toolReferences];
        const accumulatedToolResults = {};
        const toolCallRounds = [];
        const runWithTools = async () => {
            // If a toolReference is present, force the model to call that tool
            const requestedTool = toolReferences.shift();
            if (requestedTool) {
                options.toolMode = vscode.LanguageModelChatToolMode.Required;
                options.tools = vscode.lm.tools.filter(tool => tool.name === requestedTool.name);
            }
            else {
                options.toolMode = undefined;
                options.tools = [...tools];
            }
            // Send the request to the LanguageModelChat
            const response = await model.sendRequest(messages, options, token);
            // Stream text output and collect tool calls from the response
            const toolCalls = [];
            let responseStr = '';
            for await (const part of response.stream) {
                if (part instanceof vscode.LanguageModelTextPart) {
                    stream.markdown(part.value);
                    responseStr += part.value;
                }
                else if (part instanceof vscode.LanguageModelToolCallPart) {
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
                const result = (await (0, prompt_tsx_1.renderPrompt)(toolsPrompt_1.ToolUserPrompt, {
                    context: chatContext,
                    request,
                    toolCallRounds,
                    toolCallResults: accumulatedToolResults
                }, { modelMaxPromptTokens: model.maxInputTokens }, model));
                messages = result.messages;
                const toolResultMetadata = result.metadatas.getAll(toolsPrompt_1.ToolResultMetadata);
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
            },
        };
    };
    const toolUser = vscode.chat.createChatParticipant('chat-tools-sample.tools', handler);
    toolUser.iconPath = new vscode.ThemeIcon('tools');
    context.subscriptions.push(toolUser);
}
//# sourceMappingURL=toolParticipant.js.map