// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
//npx --package yo --package generator-code -- yo code
//npm install --global yo generator-code
//if not working run this..
//>cd [extensiondir]
//>tsc -watch -p ./
//npm install --save @vscode/prompt-tsx
//npm install --save ollama


import * as vscode from 'vscode';
import { renderPrompt } from '@vscode/prompt-tsx';
import { posix } from 'path';
import { PlayPrompt } from './prompts';
import * as Book from './book';
import ollama from 'ollama';

import { LanguageModelPromptTsxPart, LanguageModelToolInvocationOptions, LanguageModelToolResult } from 'vscode';


import { startWatchingWorkspace, updateStatusBarItem, registerStatusBarTool, registerCompletionTool, registerToolUserChatParticipant } from './toolParticipant';
import { start } from 'repl';

const BASE_PROMPT =
  'You are a helpful code tutor. Your job is to teach the user with simple descriptions and sample code of the concept. Respond with a guided overview of the concept in a series of messages. Do not give the user the answer directly, but guide them to find the answer themselves. If the user asks a non-programming question, politely decline to respond.';

  const EXERCISES_PROMPT =
  'You are a helpful tutor. Your job is to teach the user with fun, simple exercises that they can complete in the editor. Your exercises should start simple and get more complex as the user progresses. Move one concept at a time, and do not move on to the next concept until the user provides the correct answer. Give hints in your exercises to help the user learn. If the user is stuck, you can provide the answer and explain why it is the answer. If the user asks a non-programming question, politely decline to respond.';
// define a chat handler
let max_context_length = 512000; //for now using this max context length.  

let activeEditor = vscode.window.activeTextEditor;

let isWorking = false;
let workFunc = null;
let workPrompt = "Improve my code";

function get_current_weather(city: string): string {
	return `The current weather in ${city} is sunny.`;
}



function validateChange(topkey: string, change: string): boolean {
	//check if the change is valid.
	const allDiagnostics = vscode.languages.getDiagnostics();
	//get diagnostics for all open files.  
	//if there is some error, prompt to try to fix.  
	//return the diagnostic info.  
	console.log(allDiagnostics);

	return true;
}

function getRandomPrompt(): string {
	const mySettings = vscode.workspace.getConfiguration('mrrubato');	

	if (mySettings.workprompts.length > 0){
		let rand = Math.floor(Math.random() * mySettings.workprompts.length);
		let prompt = mySettings.workprompts[rand].prompt;
		return prompt;
	}
	else{
		return "Just starting help me figure things out.";
	}
}

function updatePrompts(topkey: string, topics: string, fullMessage: string) {
	//update the prompts here.
	const mySettings = vscode.workspace.getConfiguration('mrrubato');	

	let addltopics = Book.findTopics(fullMessage);

	const topicArray = mySettings.defaultprompts.map(obj => obj.topic); 
	let bookdata = Book.pickTopic(addltopics, topicArray, 5);
	if (mySettings.codingmode === "git"){
		let git = Book.gitChanges(addltopics); //get the git changes for the topic.
		bookdata[1] += git;  //add the git changes to the full context of topics.
	
	}
	else if (mySettings.codingmode === "book"){
		//get the book context for the topic.
		//nothing additional.  
	}

	topics = topics + bookdata[1].slice(-max_context_length/2); //dont want to overwrite the full context.  
	topics = topics.slice(-max_context_length);

	//need to determine weight of prompt.  
	mySettings.roboprompts.push({'prompt': fullMessage, 'topics': topics, weight: 0.5});
	//random delete a prompt.  
	if (mySettings.roboprompts.length > mySettings.numworkprompts){
		let val = mySettings.roboprompts.shift();

		val.weight = val.weight*(Math.random());
		if (val.weight > 0.125){
			//iterate around 2-3 times.  
			//delete the first one.
			//keep thinking about this or not.  
			mySettings.roboprompts.push(val);
		}
		if (val.weight < 0.0125){
			mySettings.roboprompts.push({'prompt': getRandomPrompt(), 'topics': topics, weight: 0.5})
		}
	}
	//for now add this prompt.  
	//probably need several steps here..
	//maybe one call to rewrite this.  


}

function roboupdate(topkey: string, topics: string, fullMessage: string) {
	//update the source code and highlight what chnaged.
	if (validateChange(topkey, fullMessage)){
//		Book.updatePage(topkey, fullMessage);
		updatePrompts(topkey, topics, fullMessage);
	}
	//Book.updatePage("book/20230110.txt", "hello");
	if (activeEditor) {

		updateStatusBarItem();
		//show the change made and switch to this page.  
	}
}

async function work(request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) {
	const mySettings = vscode.workspace.getConfiguration('mrrubato');	
	let workPrompt = mySettings.workprompt;
	if (!mySettings.runinbackground){
		//not running in background per settings.
		return;
	}

	else{
		//run the work function here.
		console.log('Running background agent');
//		stream.markdown('**Running background agent**  \n' + mySettings.runinbackground);
		if (!isWorking){
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


		let [topkey, topicdata] = await Book.read(request.prompt, context);
		//get topic to work on and context.  
		//const topics = "test"
		let fullMessage = await Chat(topicdata + request.prompt, context, stream, token);

		roboupdate(topkey, topicdata, fullMessage);


	} catch (error) {
	   console.error('Error calling Ollama:', error);
	}

}

async function Chat(prompt: string, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) {
	let ret = "";
	try {

		//connect remote
		//client = ollama.Client(host='http://192.168.1.154:11434')
		//response = client.generate(model='llama3.2b', prompt=my_prompt)
		//actual_response = response['response']


		await Book.read(prompt, context);
	  const response = await ollama.chat({
		model: 'llama3.1:8b',
//		model: 'deepseek-coder-v2:latest',
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
		stream.markdown(part.message.content);	
		ret += part.message.content;
		if (token.isCancellationRequested) {
		  break;
		}
		console.log(part.message.tool_calls);
	}
	} catch (error) {
	   console.error('Error calling Ollama:', error);
	}
	return ret;
  }
  


export function activate(context: vscode.ExtensionContext) {
	//not being activated until chatted to...
    registerToolUserChatParticipant(context);
	registerCompletionTool(context);
	registerStatusBarTool(context);
	startWatchingWorkspace(context); //watch for changes to book.  

	Book.open(context); //open the book.  
	// define a chat handler
	const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {
		//vscode.window.showInformationMessage('Hello world!');
		// initialize the prompt
		let prompt = BASE_PROMPT;
		console.log(`Chat request: ${request.command} with prompt: ${request.prompt}`);


		if (request.command === 'stats'){
			const mySettings = vscode.workspace.getConfiguration('mrrubato');	

			stream.markdown('**My agent default prompts**  ' + mySettings.defaultprompts.length + '  \n');
			stream.markdown('**My agent work prompts** ' + mySettings.workprompts.length + '  \n');
			stream.markdown('**My agent run in background** ' + mySettings.runinbackground + 	'  \n');
			stream.markdown('**My agent run interval** ' + mySettings.runinterval + '  \n');
			stream.markdown('**My agent coding mode** ' + mySettings.codingmode + '  \n');
			stream.markdown('**My agent work prompt** ' + mySettings.workprompt.slice(-255) + '  \n');

		}
		if (request.command === 'list') {
			//list the files in the book.  
			if (request.prompt === "prompts"){
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
			let [topkey, topics] = await Book.read(request.prompt, context);
			mySettings.workprompts.push({'prompt': workPrompt, 'topics': topics, weight: 1});
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
			vscode.commands.executeCommand(
				"workbench.action.chat.open",
				options
			  );


			return;
		}

		if (request.command === 'book'){
			//query book only.  
			stream.markdown('Reading a book\n');
			//get book snippet.  
			readFile(request, context, stream, token);
			Book.updatePage("book/20230110.txt", "hello");
			let myquery = "play with me and use tool #file:definitions.txt";  //calling via # doesnt work.  


			//call external ollama.  
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

	const gencommand = vscode.commands.registerCommand('mrrubato.mytutor.generate', async (text="") => {
		if (text === "") {
			const editor = vscode.window.activeTextEditor;
			if (editor) {
				const selection = editor.selection;
				text = editor.document.getText(selection);
				if (text === "") {
					//if no selection, 
					//get the current line and the text to the cursor.
					let offset = editor.selection.active;
					const fileTextToCursor = editor.document.getText(new vscode.Range(offset.line, 0, offset.line, offset.character));
					text = fileTextToCursor;
				}
			}
		}
		  	  
		//run the desired command here.  
		let cmdtype = Book.getCommandType(text);
		switch (cmdtype[0]) {
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
			case "#":
				//open on web.
				break;
			case "!":
				//find in log files
				//logdirs
				break;
			case "$":
				//find env variables
				switch (cmdtype[1]) {
					case '$':
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
						//open the file
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
			case "":
				//failure return?  
				break;

		}		
		//log the command to genbook if valid.  
		Book.logCommand(text);
	});

	context.subscriptions.push(disposable);
	
	//start the MCP server as well.  
	//vscode.commands.createMcpServer('mrrubato.mytutor', tutor);
	activeEditor = vscode.window.activeTextEditor;

	vscode.window.onDidChangeActiveTextEditor(editor => {
		activeEditor = editor;
		if (editor) {
			triggerUpdateDecorations();
			triggerGetBookContext();
			updateStatusBarItem();
		}
	}, null, context.subscriptions);

}

let uitimeout: NodeJS.Timeout | undefined = undefined;

function updateDecorations() {
	//
}

function triggerUpdateDecorations(throttle = false) {
	if (throttle) {
		uitimeout = setTimeout(updateDecorations, 500);
	} else {
		updateDecorations();
	}

}

function getBookContext() {
	//
	if (!activeEditor) {
		return vscode.window.showInformationMessage('No active editor found');
	}
	console.log(activeEditor.document.uri.toString());// + activeEditor.document);
}



function triggerGetBookContext(throttle = false) {
	if (throttle) {
		uitimeout = setTimeout(getBookContext, 500);
	} else {
		getBookContext();
	}

}

async function getStats(request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) {
	if (!vscode.workspace.workspaceFolders) {
		return vscode.window.showInformationMessage('No folder or workspace opened');
	}

	async function countAndTotalOfFilesInFolder(folder: vscode.Uri): Promise<{ total: number, count: number }> {
		let total = 0;
		let count = 0;
		for (const [name, type] of await vscode.workspace.fs.readDirectory(folder)) {
			if (type === vscode.FileType.File) {
				const filePath = posix.join(folder.path, name);
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
	const folderPath = posix.dirname(fileUri.path);
	const folderUri = fileUri.with({ path: folderPath });

	const info = await countAndTotalOfFilesInFolder(folderUri);

	//show this as message.  
	stream.markdown(`${info.count} files in ${folderUri.toString(true)} with a total of ${info.total} bytes\n`);

//	const doc = await vscode.workspace.openTextDocument({ content: `${info.count} files in ${folderUri.toString(true)} with a total of ${info.total} bytes` });
//	vscode.window.showTextDocument(doc, { viewColumn: vscode.ViewColumn.Beside });
	
}


function readFile(request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) {
	if (!vscode.workspace.workspaceFolders) {
		return vscode.window.showInformationMessage('No folder or workspace opened');
	}
	const folderUri = vscode.workspace.workspaceFolders[0].uri;
	// this should be a book path.  Use as you would work on the project.  
	const fileUri = folderUri.with({ path: posix.join(folderUri.path, 'book/definitions.txt') });
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



