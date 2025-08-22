//filbert failed, so writing my own parser.
// This is a simple parser that extracts function names from Python code.  
//it finds all function calls within functions and create a digraph of function calls.


class DilParse {
    constructor() {
        this.names = [];
    }

    parse(codeString) {
        this.names = [];
        try {
            const ast = acorn.parse(codeString, {ecmaVersion: 2020, locations: true});
            acorn.walk.simple(ast, {
                FunctionDeclaration(node) {
                    this.names.push(node.id.name);
                },
                CallExpression(node) {
                    if (node.callee.type === 'Identifier') {
                        this.names.push(node.callee.name);
                    }
                }
            });
        } catch (e) {
            return "ERROR in DilParse: " + e.toString();
        }
        return this.names;
    }
}

