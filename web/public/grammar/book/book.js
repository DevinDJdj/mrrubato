// Generated automatically by nearley, version 2.20.1
// http://github.com/Hardmath123/nearley
(function () {
function id(x) { return x[0]; }

var appendItem = function (a, b) { 
    return function (d) { 
        return d[a].concat([d[b]]); 
        } 
    };
var empty = function (d) { return []; };
var emptyStr = function (d) { return ""; };
var currentState = null;
var currentTopic = null;


/***** COMMON FUNCTIONS *****/
function newTopic(d) {
    let output = {};

    output[d[0]] = d[0];

    return {topic: output[d[0]] };
}

function commentStart(d) {
    return {comment: []};
}

function commentEnd(d) {
    return {comment: []};
}

var grammar = {
    Lexer: undefined,
    ParserRules: [
    {"name": "file", "symbols": ["newline", "rows"], "postprocess": function (d) { return { rows: d[1] }; }},
    {"name": "rows", "symbols": ["row"]},
    {"name": "rows", "symbols": ["rows", "newline", "row"], "postprocess": appendItem(0,2)},
    {"name": "row", "symbols": ["comment"], "postprocess": id},
    {"name": "row", "symbols": ["topic"], "postprocess": id},
    {"name": "topic", "symbols": ["startt"], "postprocess": function(d){ return [d[0]];}},
    {"name": "topic", "symbols": ["startt", "newline", "anyLine"], "postprocess": appendItem(0, 2)},
    {"name": "topic", "symbols": ["topic", "newline", "anyLine"], "postprocess": appendItem(0, 2)},
    {"name": "comment", "symbols": ["comment_start", "rows", "comment_end"]},
    {"name": "anyLine", "symbols": ["cmd"], "postprocess": id},
    {"name": "anyLine", "symbols": ["comment_start"], "postprocess": id},
    {"name": "anyLine", "symbols": ["comment_end"], "postprocess": id},
    {"name": "anyLine", "symbols": ["question"], "postprocess": id},
    {"name": "anyLine", "symbols": ["environment_var"], "postprocess": id},
    {"name": "anyLine", "symbols": ["note_"], "postprocess": id},
    {"name": "anyLine", "symbols": ["subtask_"], "postprocess": id},
    {"name": "anyLine", "symbols": ["reference_"], "postprocess": id},
    {"name": "anyLine", "symbols": ["anyrow"], "postprocess": id},
    {"name": "startt$string$1", "symbols": [{"literal":"*"}, {"literal":"*"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "startt$ebnf$1", "symbols": []},
    {"name": "startt$ebnf$1", "symbols": ["startt$ebnf$1", /[^\n]/], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "startt", "symbols": ["startt$string$1", "startt$ebnf$1"], "postprocess": newTopic},
    {"name": "cmd$ebnf$1", "symbols": []},
    {"name": "cmd$ebnf$1", "symbols": ["cmd$ebnf$1", /[^\n]/], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "cmd", "symbols": [{"literal":">"}, "cmd$ebnf$1"], "postprocess": id},
    {"name": "comment_start$string$1", "symbols": [{"literal":"<"}, {"literal":"!"}, {"literal":"-"}, {"literal":"-"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "comment_start", "symbols": ["comment_start$string$1", "newline"], "postprocess": commentStart},
    {"name": "comment_end$string$1", "symbols": [{"literal":"-"}, {"literal":"-"}, {"literal":">"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "comment_end", "symbols": ["comment_end$string$1", "newline"], "postprocess": commentEnd},
    {"name": "question$string$1", "symbols": [{"literal":"@"}, {"literal":"@"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "question$ebnf$1", "symbols": []},
    {"name": "question$ebnf$1", "symbols": ["question$ebnf$1", /[^\n]/], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "question", "symbols": ["question$string$1", "question$ebnf$1"], "postprocess": function(d) { return d[0]; }},
    {"name": "environment_var$string$1", "symbols": [{"literal":"$"}, {"literal":"$"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "environment_var$ebnf$1", "symbols": []},
    {"name": "environment_var$ebnf$1", "symbols": ["environment_var$ebnf$1", /[^\n]/], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "environment_var", "symbols": ["environment_var$string$1", "environment_var$ebnf$1"], "postprocess": function(d) { return d[0]; }},
    {"name": "note_$ebnf$1$string$1", "symbols": [{"literal":"-"}, {"literal":"-"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "note_$ebnf$1", "symbols": ["note_$ebnf$1$string$1"]},
    {"name": "note_$ebnf$1$string$2", "symbols": [{"literal":"-"}, {"literal":"-"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "note_$ebnf$1", "symbols": ["note_$ebnf$1", "note_$ebnf$1$string$2"], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "note_$ebnf$2", "symbols": []},
    {"name": "note_$ebnf$2", "symbols": ["note_$ebnf$2", /[^\n]/], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "note_", "symbols": ["note_$ebnf$1", "note_$ebnf$2"], "postprocess": function(d) { return d[0]; }},
    {"name": "subtask_$ebnf$1", "symbols": [{"literal":"-"}]},
    {"name": "subtask_$ebnf$1", "symbols": ["subtask_$ebnf$1", {"literal":"-"}], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "subtask_$ebnf$2", "symbols": []},
    {"name": "subtask_$ebnf$2", "symbols": ["subtask_$ebnf$2", /[^\n]/], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "subtask_", "symbols": ["subtask_$ebnf$1", "subtask_$ebnf$2"], "postprocess": function(d) { return d[0]; }},
    {"name": "reference_$ebnf$1", "symbols": [{"literal":"#"}]},
    {"name": "reference_$ebnf$1", "symbols": ["reference_$ebnf$1", {"literal":"#"}], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "reference_$ebnf$2", "symbols": []},
    {"name": "reference_$ebnf$2", "symbols": ["reference_$ebnf$2", /[^\n]/], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "reference_", "symbols": ["reference_$ebnf$1", "reference_$ebnf$2"], "postprocess": function(d) { return d[0]; }},
    {"name": "anyrow$ebnf$1", "symbols": []},
    {"name": "anyrow$ebnf$1", "symbols": ["anyrow$ebnf$1", /[^\n]/], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "anyrow", "symbols": ["anyrow$ebnf$1"], "postprocess": function(d) { return d[0]; }},
    {"name": "newline", "symbols": [{"literal":"\r"}, {"literal":"\n"}], "postprocess": empty},
    {"name": "newline", "symbols": [{"literal":"\r"}]},
    {"name": "newline", "symbols": [{"literal":"\n"}], "postprocess": empty}
]
  , ParserStart: "file"
}
if (typeof module !== 'undefined'&& typeof module.exports !== 'undefined') {
   module.exports = grammar;
} else {
   window.book = grammar;
}
})();
