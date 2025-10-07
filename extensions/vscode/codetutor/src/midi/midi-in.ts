const vscode = require('vscode');
const JMVSC = require('jazz-midi-vscode');
const JZZ = require('jzz');
import * as mykeys from './mykeys';

let mkeys : mykeys.MyKeys;

//use shared JSON config..
import * as config from '../../../../../../config.json';


function getNonce() {
	let text = '';
	const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	for (let i = 0; i < 32; i++) {
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	}
	return text;
}

export function activate(context) {
    const extpath = context.extensionPath;
    
    var panels = {};

    //load config.  

    mkeys = new mykeys.MyKeys(config );


    context.subscriptions.push(vscode.commands.registerCommand('midi-demo.midi-in', async function (port) {
        const column = vscode.window.activeTextEditor ? vscode.window.activeTextEditor.viewColumn : undefined;
        if (panels[port]) {
            panels[port].reveal(column);
            return;
        }
        panels[port] = vscode.window.createWebviewPanel('midi-demo.midi-in-view', port, column, { enableScripts: true });
        panels[port].onDidDispose(() => { delete panels[port]; }, null, context.subscriptions);
        function ref(a, b) {
            return JMVSC.context() === 'backend' ? panels[port].webview.asWebviewUri(vscode.Uri.file(extpath + '/' + a)) : b;
//            return panels[port].webview.asWebviewUri(vscode.Uri.file(extpath + '/' + a));
        }
       JMVSC.init(panels[port]);



       panels[port].webview.onDidReceiveMessage(message => {
              // Handle messages from the webview if needed
              console.log("Message from webview:", message);
              switch (message.command) {
                    case 'alert':
                        vscode.window.showErrorMessage(message.text);
                        return;
              } 
         });



         var midiport = JZZ().openMidiIn(port).or(() => {
             panels[port].webview.html = `<html><body><h1>${port}</h1><p>Cannot open port!</p></body></html>`;
             return;
         });

            midiport.connect((msg) => {
                console.log('MIDI message:', msg);
                //mykeys.push(msg);
                mkeys.key(msg, 0, null); //no callback for now.
//                panels[port].webview.postMessage({ command: 'midi', message: msg });
            });
         

         const scriptPath = vscode.Uri.joinPath(context.extensionUri, 'src', 'midi', 'input.js');
         const scriptUri = panels[port].webview.asWebviewUri(scriptPath);
         const nonce = getNonce();
       panels[port].webview.html =`<!DOCTYPE html>
<html>
<head>
<script src="${ref('node_modules/jazz-midi-vscode/main.js', 'https://cdn.jsdelivr.net/npm/jazz-midi-vscode')}"></script>
<script src="${ref('node_modules/jzz/javascript/JZZ.js', 'https://cdn.jsdelivr.net/npm/jzz')}"></script>
</head>
<body>
<h1>${port}</h1>
<pre id="log"></pre>
<script>
//const vscode = acquireVsCodeApi();
//vscode.postMessage({command: 'alert', text: 'hello'}); // Send an initial message to the extension if needed
var log = document.getElementById('log');
var port = JZZ().openMidiIn('${port}').or(() => log.innerHTML = 'Cannot open port!');
port.connect((msg) => log.innerHTML += msg + '\\n');
console.log("midi/input.js running");
</script>

<script nonce="${nonce}" src="${scriptUri}"></script>

</body>
</html>`;

}));
}

export function deactivate() {}

module.exports = {
    activate,
    deactivate
}
