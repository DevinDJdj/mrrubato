// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
//npx --package yo --package generator-code -- yo code
//npm install --global yo generator-code
//if not working run this..
//>cd [extensiondir]
//>tsc -watch -p ./
//npm install --save @vscode/prompt-tsx


import * as vscode from 'vscode';
import { renderPrompt } from '@vscode/prompt-tsx';
import { posix } from 'path';
import { PlayPrompt } from './prompts';

import { LanguageModelPromptTsxPart, LanguageModelToolInvocationOptions, LanguageModelToolResult } from 'vscode';


import { registerToolUserChatParticipant } from './toolParticipant';

const BASE_PROMPT =
  'You are a helpful code tutor. Your job is to teach the user with simple descriptions and sample code of the concept. Respond with a guided overview of the concept in a series of messages. Do not give the user the answer directly, but guide them to find the answer themselves. If the user asks a non-programming question, politely decline to respond.';

  const EXERCISES_PROMPT =
  'You are a helpful tutor. Your job is to teach the user with fun, simple exercises that they can complete in the editor. Your exercises should start simple and get more complex as the user progresses. Move one concept at a time, and do not move on to the next concept until the user provides the correct answer. Give hints in your exercises to help the user learn. If the user is stuck, you can provide the answer and explain why it is the answer. If the user asks a non-programming question, politely decline to respond.';
// define a chat handler



export function activate(context: vscode.ExtensionContext) {

    registerToolUserChatParticipant(context);
	// define a chat handler
	const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {
		//vscode.window.showInformationMessage('Hello world!');
		// initialize the prompt
		let prompt = BASE_PROMPT;

		if (request.command === 'exercise') {
			prompt = EXERCISES_PROMPT;
		}

		if (request.command === 'book'){
			//query book only.  
			stream.markdown('Reading a book\n');
			//get book snippet.  
			readFile(request, context, stream, token);

			let myquery = "play with me and use tool #get_alerts";  //calling via # doesnt work.  


			const { messages } = await renderPrompt(
				PlayPrompt,
				{ userQuery: myquery }, 
				{ modelMaxPromptTokens: request.model.maxInputTokens },
				request.model);
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
		const previousMessages = context.history.filter(
			(h) => h instanceof vscode.ChatResponseTurn
		);

		// add the previous messages to the messages array
		previousMessages.forEach((m) => {
			let fullMessage = '';
			m.response.forEach((r) => {
				const mdPart = r as vscode.ChatResponseMarkdownPart;
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

function readFile(request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) {
	if (!vscode.workspace.workspaceFolders) {
		return vscode.window.showInformationMessage('No folder or workspace opened');
	}
	const folderUri = vscode.workspace.workspaceFolders[0].uri;
	const fileUri = folderUri.with({ path: posix.join(folderUri.path, 'definitions.txt') });
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
function insertTextIntoActiveEditor(text: string): Thenable<boolean> | undefined {
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
			} else {
				vscode.window.showErrorMessage('Failed to insert text');
			}
			return success;
		});
	} catch (error) {
		vscode.window.showErrorMessage(`Error inserting text: ${error instanceof Error ? error.message : String(error)}`);
		return Promise.resolve(false);
	}
}

// This method is called when your extension is deactivated
export default function deactivate() {}



class MyUriHandler implements vscode.UriHandler {
	// This function will get run when something redirects to VS Code
	// with your extension id as the authority.
	handleUri(uri: vscode.Uri): vscode.ProviderResult<void> {
		console.log(`Handling Uri: ${uri.toString()}`);
		let message = "Handled a Uri!";
		if (uri.query) {
			message += ` It came with this query: ${uri.query}`;
		}
		vscode.window.showInformationMessage(message);
	}
}

