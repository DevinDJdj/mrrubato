var ast = "";
var graphstr = "";


function getBookGraph(fileName, codeString){
    var dotstr = "digraph {\n";
    let dotlabels = getBookDOTLabels();
    dotstr += dotlabels + "\n";
    let dot = getBookDOT(fileName);

    dotstr += dot + "}\n";

    netgraph = new FUNCS.NETGRAPH.NetworkGraph(document.getElementById('booknetwork'));
    netgraph.simpleGraph(dotstr);
}

function getCodeGraph(fileName, codeString){

    graphstr = "";
    if (fileName.endsWith(".js") || fileName.endsWith(".mjs")) {
        let n = acornParse(codeString);
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
        
    }

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

    getBookGraph(fileName, codeString);

}

function getDotString(input, depth=1){
    ret = "";
    if (typeof(input) === "Array"){
        ret = "digraph weighted {\n";
        for (var i = 1; i < input.length; i++) {
            for (var j = 0; j < depth && i+j<input.length; j++) {
                ret += input[i+j-1] + " -> " + input[i+j] + " [width=" + (depth-j) + "] \n";
            }
        }
        ret += "}\n";
        return ret;
    }
}
function filbertParse(codeString){
    var parseFn = filbert.parse;
    var ranges = false;
    var locations = false;
    try {
        var code = codeString;
        ast = parseFn(code, { locations: locations, ranges: ranges });
    }
    catch (e) {
        return "ERROR in filbertParse: " + e.toString();
    }
    return ast;

}


function acornParse(codeString){
    names = acornGetFunctionNames(codeString);
    return names;
}

function acornGetFunctionNames(codeString) {
    var names = [];
    acorn.walk.simple(acorn.parse(codeString), {
        AssignmentExpression: function(node) {
            if(node.left.type === "Identifier" && (node.right.type === "FunctionExpression" || node.right.type === "ArrowFunctionExpression")) {
                names.push(node.left.name);
            }
        },
        VariableDeclaration: function(node) {
            node.declarations.forEach(function (declaration) {
                if(declaration.init && (declaration.init.type === "FunctionExpression" || declaration.init.type === "ArrowFunctionExpression")) {
                    names.push(declaration.id.name);
                }
            });
        },
        Function: function(node) {
            if(node.id) {
                names.push(node.id.name);
            }
        }
    });
    return names;
}

