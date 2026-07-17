const vscode = require('vscode');
const JZZ = require('jzz');

var numconns = 0;
var myintervalLoop = null;

export function activate(context) {
    context.subscriptions.push(vscode.window.registerTreeDataProvider('midi-demo.tree', {
        getChildren: async function(item) {
            var info, x, ret;
            if (!item) {
                return [
                    { label: 'MIDI-Out', tooltip: 'MIDI-Out ports', collapsibleState: vscode.TreeItemCollapsibleState.Expanded },
                    { label: 'MIDI-In', tooltip: 'MIDI-In ports', collapsibleState: vscode.TreeItemCollapsibleState.Expanded }
                ];
            }
            else if (item.label === 'MIDI-Out') {
                info = (await JZZ()).info();
                ret = [];
                for (x of info.outputs) {
                    ret.push({ label: x.name, command: { command: 'midi-demo.midi-out', arguments: [ x.name ] } });
                }
                return ret;
            }
            else if (item.label === 'MIDI-In') {
                info = (await JZZ()).info();
                //populate number of connections..
                numconns = info.outputs.length + info.inputs.length;
                ret = [];
                for (x of info.inputs) {
                    ret.push({ label: x.name, command: { command: 'midi-demo.midi-in', arguments: [ x.name ] } });
                    //activate the panel on click
                    vscode.commands.executeCommand('midi-demo.midi-in', x.name);
                }
                return ret;
            }
        },
        getTreeItem: function(item) {
            return item;
        }

    }));


    myintervalLoop = setInterval(async () => {
        //check if we have new midi info?  
        let info = (await JZZ()).info();
        if (numconns !== info.outputs.length + info.inputs.length) {
            numconns = info.outputs.length + info.inputs.length;
            clearInterval(myintervalLoop); //dont want multiple loops running..
            activate(context);
            numconns = info.outputs.length + info.inputs.length;
        }
    }, 60000); 

}

export function deactivate() {}

module.exports = {
    activate,
    deactivate
}
