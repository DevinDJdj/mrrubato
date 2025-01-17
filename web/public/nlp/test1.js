//nearleyc grammars/grammar.ne -o grammars/grammar.js
//browserify nlp/test1.js -o nlp/bundle1.js


const nearley = require("nearley");

//const grammar = require("../grammar/grammar.js");
const grammar = require("../grammar/program.js");


// Create a Parser object from our grammar.
const parser = new nearley.Parser(nearley.Grammar.fromCompiled(grammar));

// Parse something!
parser.feed("foo\n");

// parser.results is an array of possible parsings.
console.log(JSON.stringify(parser.results)); // [[[[["foo"],"\n"]]]]


//const nearley = require("nearley");
const compile = require("nearley/lib/compile");
const generate = require("nearley/lib/generate");
const nearleyGrammar = require("nearley/lib/nearley-language-bootstrapped");

function compileGrammar(sourceCode) {
    // Parse the grammar source into an AST
    const grammarParser = new nearley.Parser(nearleyGrammar);
    grammarParser.feed(sourceCode);
    const grammarAst = grammarParser.results[0]; // TODO check for errors

    // Compile the AST into a set of rules
    const grammarInfoObject = compile(grammarAst, {});
    // Generate JavaScript code from the rules
    const grammarJs = generate(grammarInfoObject, "grammar");

    // Pretend this is a CommonJS environment to catch exports from the grammar.
    const module = { exports: {} };
    eval(grammarJs);

    return module.exports;
}

const grammara = compileGrammar("main -> foo | bar");

const parsera = new nearley.Parser(nearley.Grammar.fromCompiled(grammar));

parsera.feed("foo");

// parser.results is an array of possible parsings.
console.log(JSON.stringify(parsera.results)); // [[[[["foo"],"\n"]]]]