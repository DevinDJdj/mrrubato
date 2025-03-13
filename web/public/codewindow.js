var ast = "";
var graphstr = "";

function getCodeGraph(fileName, codeString){

    if (fileName.endsWith(".js") || fileName.endsWith(".mjs")) {
        let n = acornParse(codeString);
        graphstr = getDotString(n);
    }
    else if (fileName.endsWith(".py")) {
        ast = filbertParse(codeString);
        console.log(ast);
        graphstr = getDotString(ast);
    }
    netgraph = new FUNCS.NETGRAPH.NetworkGraph(document.getElementById('mynetwork'));
    netgraph.simpleGraph(graphstr);
    netgraph.setSelectionCallback(function(selection){
      console.log(selection);
    });

}

function getDotString(input){
    ret = "";
    if (typeof(input) === "Array"){
        ret = "digraph {\n";
        for (var i = 1; i < input.length; i++) {
            ret += input[i-1] + " -> " + input[i] + "\n";
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

