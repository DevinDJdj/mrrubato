var ast = "";
var graphstr = "";



function getDOTLabelsString(dotlabels){
    dotlabels.sort((a, b) => a.key.localeCompare(b.key) || a.depth - b.depth);
    let dotstr = "";
    for (let i = 0; i < dotlabels.length-1; i++) {
        let dl = dotlabels[i];
        let dl2 = dotlabels[i+1];
        if (dl.key == dl2.key){
            //splice them together
            dl2.width += dl.width;
            dotlabels.splice(i, 1);
            i--;
        }
    }
    for (let i = 0; i < dotlabels.length; i++) {
        let dl = dotlabels[i];
//        dotstr += dotlabels[i] + "\n";

        let size = dl.width || 1; //default size to 1 if not specified
        if (size < 1){
            size = 1; //minimum size
        }
        else if (size > 8){
            size = 8; //maximum size
        }
        size = size*5;
        size += dl.depth*5; //add depth to size
        let color = getColorFromSequence(dl.depth, "hex"); //drawkeyboard.js
        dotstr += `${dl.lakey} [label="${dl.key}", fillcolor="${color}", fontsize=${size}];\n`;      // [fontsize=${size}]
    }
    return dotstr;

}

function getBookGraph(fileName, graphString){
    var dotstr = "digraph {\n";
    dotstr += 'label="40pt Graph Label"'   + "\n";
    dotstr += 'fontsize=40' + "\n";
    dotstr += 'labelloc="t"' + "\n";
    dotstr += 'labeljust="l"' + "\n";
    let dotlabels = getBookDOTLabels(fileName);
    //not sure what else we can sort by..
    dotstr += getDOTLabelsString(dotlabels) + "\n";
//    dotstr += dotlabels + "\n";
    
    let dot = getBookDOT(fileName);

    dotstr += dot + "}\n";

    netgraph = new FUNCS.NETGRAPH.NetworkGraph(document.getElementById('booknetwork'));
    netgraph.simpleGraph(dotstr);
}

function getCodeGraph(fileName, codeString){

    graphstr = "";
    try{
        if (fileName.endsWith(".js")){
            let n = acornParse(codeString, {ecmaVersion: 2020});
            graphstr = getDotString(n);
        }
        else if (fileName.endsWith(".mjs")){
            let n = acornParse(codeString, {ecmaVersion: 2020, sourceType: "module"});
            graphstr = getDotString(n);
        }
        else if (fileName.endsWith(".py")) {
            ast = filbertParse(codeString);
            console.log(ast);
            graphstr = getDotString(ast);
        }
        else if (fileName.endsWith(".lisp")) {
            //languages/lisp/test.lisp
            graphstr = getDotString(["test1", "test2", "test3", "test4", "test5"], 2);
        }
        else{
            //test this with everything else.  Probably want two graphs.  
            graphstr = getDotString(["test1", "test2", "test3", "test4", "test5"], 2);
            
        }

        getBookGraph(fileName, graphstr);

        if (graphstr === "") {
            console.log("ERROR: No graph generated");
        }
        else{
            netgraph = new FUNCS.NETGRAPH.NetworkGraph(document.getElementById('mynetwork'));
            netgraph.simpleGraph(graphstr);
            netgraph.setSelectionCallback(function(selection){
            console.log(selection);
            });
        }
    }
    catch (e) {
        console.log("ERROR: " + e.toString());
        graphstr = "ERROR: " + e.toString();
    }


}

function getDOTLabels(input){
    dotstr = "";
    Object.entries(input).forEach(([key, value]) => {
        dotstr += `${genLabel(key)} [label="${key}"];\n`;
    });
    return dotstr;
      
}

function getDotString(input, depth=1){

    var dotstr = "digraph {\n";
    dotstr += 'label="40pt Graph Label"'   + "\n";
    dotstr += 'fontsize=40' + "\n";
    dotstr += 'labelloc="t"' + "\n";
    dotstr += 'labeljust="l"' + "\n";

    dotstr += getDOTLabels(input) + "\n";

    if (typeof(input) === "Array"){
        for (var i = 1; i < input.length; i++) {
            for (var j = 0; j < depth && i+j<input.length; j++) {
                dotstr += input[i+j-1] + " -> " + input[i+j] + " [width=" + (depth-j) + "] \n";
            }
        }
        dotstr += "}\n";
        return dotstr;
    }
    else{
        //should be a map of string to array of strings.  
        Object.entries(input).forEach(([key, value]) => {
            for (var i = 0; i < value.length; i++) {
                //we can have either straight strings or objects with label and weight.
                let weight = value[i].weight || 1; //default weight to 1 if not specified
                //maybe need weight if we have multiple calls?  
                let label = value[i].label || value[i]; //default label to value if not specified
                dotstr += genLabel(key) + " -> " + genLabel(label) + " [width=" + weight + "] \n";
            }

//            console.log(`${key}: ${value}`);
          });
          dotstr += "}\n";
          return dotstr;        


    }
}
function filbertParse(codeString){
    var parseFn = filbert.parse;
    var ranges = false;
    var locations = false;
    names = [];
    try {
        var code = codeString;
        ast = parseFn(code, { locations: locations, ranges: ranges });
        for (var i = 0; i < ast.body.length; i++) {
            if (ast.body[i].type === "FunctionDeclaration") {
                names.push(ast.body[i].id.name);
            }
            else if (ast.body[i].type === "VariableDeclaration") {
                for (var j = 0; j < ast.body[i].declarations.length; j++) {
                    if (ast.body[i].declarations[j].init && ast.body[i].declarations[j].init.type === "FunctionExpression") {
                        ast.body[i].declarations[j].name = ast.body[i].declarations[j].id.name;
                    }
                }
            }
        }
    }
    catch (e) {
        return "ERROR in filbertParse: " + e.toString();
    }
    //for now just returning function names.  
    return names;

}


function acornParse(codeString, options={ecmaVersion: 2020, sourceType: "script"}){
    names = acornGetFunctionNames(codeString, options);
    return names;
}


function acornGetCalls(ast, options={ecmaVersion: 2020, sourceType: "script"}){
    var names = [];
    try {
        acorn.walk.simple(ast, {
            CallExpression(node) {
                if (node.callee.type === 'Identifier') {
                    names.push(node.callee.name);
                }
            }
        });
    } catch (e) {
        return ["ERROR in acornGetCalls: " + e.toString()];
    }
    return names;
}

function acornGetFunctionNames(codeString, options={ecmaVersion: 2020, sourceType: "script"}){ 
//    var names = [];
    var names = {};
    acorn.walk.simple(acorn.parse(codeString, options), {
        AssignmentExpression: function(node) {
            if(node.left.type === "Identifier" && (node.right.type === "FunctionExpression" || node.right.type === "ArrowFunctionExpression")) {
                names[node.left.name] = acornGetCalls(node.right.body, options);
//                names.push(node.left.name);
            }
        },
        //is this what is being used or not?  
        VariableDeclaration: function(node) {
            node.declarations.forEach(function (declaration) {
                if(declaration.init && (declaration.init.type === "FunctionExpression" || declaration.init.type === "ArrowFunctionExpression")) {
                    names[declaration.id.name] = acornGetCalls(declaration.init.body, options);
//                    names.push(declaration.id.name);
                }
            });
        },
        
        Function: function(node) {
            if(node.id) {
                names[node.id.name] = acornGetCalls(node.body, options);
//                names.push(node.id.name);
            }
        }
    });
    return names;
}

