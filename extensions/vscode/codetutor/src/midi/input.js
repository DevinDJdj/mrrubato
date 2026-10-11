//@ts-check

(function () {
console.log("midi/input.js loaded");
//const vscode = acquireVsCodeApi(); // Get the VS Code API instance
//vscode.postMessage({command: 'alert', text: 'hello'}); // Send an initial message to the extension if needed
console.log("midi/input.js finished");
let info = document.getElementById('info');
if (info) {
    info.innerHTML = "MIDI input initialized.<br>Show Lang here..";
}


}());