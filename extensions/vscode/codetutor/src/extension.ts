// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';

const BASE_PROMPT =
  'You are a helpful code tutor. Your job is to teach the user with simple descriptions and sample code of the concept. Respond with a guided overview of the concept in a series of messages. Do not give the user the answer directly, but guide them to find the answer themselves. If the user asks a non-programming question, politely decline to respond.';

  const EXERCISES_PROMPT =
  'You are a helpful tutor. Your job is to teach the user with fun, simple exercises that they can complete in the editor. Your exercises should start simple and get more complex as the user progresses. Move one concept at a time, and do not move on to the next concept until the user provides the correct answer. Give hints in your exercises to help the user learn. If the user is stuck, you can provide the answer and explain why it is the answer. If the user asks a non-programming question, politely decline to respond.';
// define a chat handler
const handler: vscode.ChatRequestHandler = async (
	request: vscode.ChatRequest,
	context: vscode.ChatContext,
	stream: vscode.ChatResponseStream,
	token: vscode.CancellationToken
  ) => {
	// initialize the prompt
	let prompt = BASE_PROMPT;
  
	if (request.command === 'exercise') {
	  prompt = EXERCISES_PROMPT;
	}
  
	// initialize the messages array with the prompt
	const messages = [vscode.LanguageModelChatMessage.User(prompt)];
  
	// get all the previous participant messages
	const previousMessages = context.history.filter(
	  h => h instanceof vscode.ChatResponseTurn
	);
  
	// add the previous messages to the messages array
	previousMessages.forEach(m => {
	  let fullMessage = '';
	  m.response.forEach(r => {
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
	  
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "codetutor" is now active!');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	const disposable = vscode.commands.registerCommand('codetutor.helloWorld', () => {
		// The code you place here will be executed every time your command is executed
		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from codetutor!');
	});

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}
