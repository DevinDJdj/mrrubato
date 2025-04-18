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
const ollama_1 = __importDefault(require("ollama"));
const toolParticipant_1 = require("./toolParticipant");
const BASE_PROMPT = 'You are a helpful code tutor. Your job is to teach the user with simple descriptions and sample code of the concept. Respond with a guided overview of the concept in a series of messages. Do not give the user the answer directly, but guide them to find the answer themselves. If the user asks a non-programming question, politely decline to respond.';
const EXERCISES_PROMPT = 'You are a helpful tutor. Your job is to teach the user with fun, simple exercises that they can complete in the editor. Your exercises should start simple and get more complex as the user progresses. Move one concept at a time, and do not move on to the next concept until the user provides the correct answer. Give hints in your exercises to help the user learn. If the user is stuck, you can provide the answer and explain why it is the answer. If the user asks a non-programming question, politely decline to respond.';
// define a chat handler
function get_current_weather(city) {
    return `The current weather in ${city} is sunny.`;
}
async function getStreamingResponse(request, context, stream, token) {
    try {
        const response = await ollama_1.default.chat({
            model: 'llama3:8b',
            messages: [{ role: 'user', content: request.prompt }],
            stream: true,
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
                },
            ],
        });
        for await (const part of response) {
            process.stdout.write(part.message.content);
            stream.markdown(part.message.content);
            if (token.isCancellationRequested) {
                break;
            }
            //		console.log(part.message.tool_calls);
        }
    }
    catch (error) {
        console.error('Error calling Ollama:', error);
    }
}
function activate(context) {
    (0, toolParticipant_1.registerToolUserChatParticipant)(context);
    // define a chat handler
    const handler = async (request, context, stream, token) => {
        //vscode.window.showInformationMessage('Hello world!');
        // initialize the prompt
        let prompt = BASE_PROMPT;
        if (request.command === 'exercise') {
            prompt = EXERCISES_PROMPT;
            stream.markdown('Starting exercise\n');
            await getStreamingResponse(request, context, stream, token);
            return;
        }
        if (request.command === 'book') {
            //query book only.  
            stream.markdown('Reading a book\n');
            //get book snippet.  
            readFile(request, context, stream, token);
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
    //start the MCP server as well.  
    //vscode.commands.createMcpServer('mrrubato.mytutor', tutor);
}
function readFile(request, context, stream, token) {
    if (!vscode.workspace.workspaceFolders) {
        return vscode.window.showInformationMessage('No folder or workspace opened');
    }
    const folderUri = vscode.workspace.workspaceFolders[0].uri;
    const fileUri = folderUri.with({ path: path_1.posix.join(folderUri.path, 'definitions.txt') });
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