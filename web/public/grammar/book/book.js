// Generated automatically by nearley, version 2.20.1
// http://github.com/Hardmath123/nearley
(function () {
function id(x) { return x[0]; }

var appendItem = function (a, b) {
    //if d[a] is a string, make it an array.   
    return function (d) { 
        console.log(d);
        return d[a]; 
        } 
    };
var appendItemA = function (a, b) { return function (d) { return d[a].concat([d[b]]); } };
var appendItemB = function (a, b) { return function (d) { return d[a].concat(d[b]); } };

var appendItemChar = function (a, b) { return function (d) { return d[a].concat(d[b]); } };

var appendString = function(a, b){
    return function(d){
        return d[a] + '\n' + d[b];
    }
};

var empty = function (d) { return []; };
var emptyStr = function (d) { return ""; };
var currentState = null;
var currentStr = "";
var currentTopic = null;
var topicarray = {};
var refarray = [];



/***** COMMON FUNCTIONS *****/

function startTopic(d){
    console.log("starttopic");
    console.log(d);
    topicarray[currentTopic ] =  d[0];
    mytopicarray = topicarray;
    return [ d[0] ];

}
function updTopic(d) {
    console.log("updatetopic");
    console.log(d);
//    console.log(topicarray);
    topicarray[currentTopic ] =  d[1];
    mytopicarray = topicarray;


    return d[0] + "\n" + d[1].join("");
//    return d[0] + "\n" + d[1];

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
    {"name": "file", "symbols": ["rows"], "postprocess": function(d){ console.log("rows"); console.log(d); return { rows: d[0] }; }},
    {"name": "rows", "symbols": ["rows", "newline", "row"], "postprocess": appendItemA(0,2)},
    {"name": "rows", "symbols": ["row"]},
    {"name": "row", "symbols": ["field"]},
    {"name": "row", "symbols": ["row", {"literal":","}, "field"], "postprocess": appendItem(0,2)},
    {"name": "field", "symbols": ["unquoted_field"], "postprocess": id},
    {"name": "unquoted_field", "symbols": [], "postprocess": emptyStr},
    {"name": "unquoted_field", "symbols": ["unquoted_field", "char"], "postprocess": appendItemChar(0,1)},
    {"name": "char", "symbols": [/[^\n\r",]/], "postprocess": id},
    {"name": "startt", "symbols": ["an_asterisk", "an_asterisk", "chars"], "postprocess": function(d){ console.log(d);console.log(topicarray); currentTopic = "**" + d[2]; return d[0] + d[1] + d[2]; }},
    {"name": "cmd", "symbols": [{"literal":">"}, "chars"], "postprocess": function(d) { return {cmd: d[1]}; }},
    {"name": "comment_start$string$1", "symbols": [{"literal":"<"}, {"literal":"!"}, {"literal":"-"}, {"literal":"-"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "comment_start", "symbols": ["comment_start$string$1"], "postprocess": commentStart},
    {"name": "comment_end$string$1", "symbols": [{"literal":"-"}, {"literal":"-"}, {"literal":">"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "comment_end", "symbols": ["comment_end$string$1"], "postprocess": commentEnd},
    {"name": "question$string$1", "symbols": [{"literal":"@"}, {"literal":"@"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "question", "symbols": ["question$string$1", "chars"], "postprocess": function(d) { return d[1]; }},
    {"name": "environment_var$string$1", "symbols": [{"literal":"$"}, {"literal":"$"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "environment_var", "symbols": ["environment_var$string$1", "chars"], "postprocess": function(d) { return d[1]; }},
    {"name": "note_$ebnf$1$string$1", "symbols": [{"literal":"-"}, {"literal":"-"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "note_$ebnf$1", "symbols": ["note_$ebnf$1$string$1"]},
    {"name": "note_$ebnf$1$string$2", "symbols": [{"literal":"-"}, {"literal":"-"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "note_$ebnf$1", "symbols": ["note_$ebnf$1", "note_$ebnf$1$string$2"], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "note_", "symbols": ["note_$ebnf$1", "chars"], "postprocess": function(d) { return d[1]; }},
    {"name": "subtask_$ebnf$1", "symbols": [{"literal":"-"}]},
    {"name": "subtask_$ebnf$1", "symbols": ["subtask_$ebnf$1", {"literal":"-"}], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "subtask_", "symbols": ["subtask_$ebnf$1", "chars"], "postprocess": function(d) { return d[1]; }},
    {"name": "reference_$ebnf$1", "symbols": [{"literal":"#"}]},
    {"name": "reference_$ebnf$1", "symbols": ["reference_$ebnf$1", {"literal":"#"}], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "reference_", "symbols": ["reference_$ebnf$1", "chars"], "postprocess": function(d) { myrefarray.push(d[1]); return d[1]; }},
    {"name": "anyrow", "symbols": ["not_asterisk"], "postprocess": function(d) { return d[0] + ""; }},
    {"name": "anyrow", "symbols": ["an_asterisk"], "postprocess": function(d) { return d[0] + ""; }},
    {"name": "anyrow", "symbols": ["not_asterisk", "chars"], "postprocess": function(d) { return d[0] + d[1]; }},
    {"name": "anyrow", "symbols": [], "postprocess": emptyStr},
    {"name": "anyLine", "symbols": ["cmd"], "postprocess": id},
    {"name": "anyLine", "symbols": ["question"], "postprocess": id},
    {"name": "anyLine", "symbols": ["environment_var"], "postprocess": id},
    {"name": "anyLine", "symbols": ["note_"], "postprocess": id},
    {"name": "anyLine", "symbols": ["subtask_"], "postprocess": id},
    {"name": "anyLine", "symbols": ["reference_"], "postprocess": id},
    {"name": "anyLine", "symbols": ["anyrow"], "postprocess": id},
    {"name": "topic", "symbols": ["startt", "newline"], "postprocess": startTopic},
    {"name": "topic", "symbols": ["topic", "anyLine", "newline"], "postprocess": appendItemA(0,1)},
    {"name": "newline", "symbols": [/[\r\n]/]},
    {"name": "newline", "symbols": [/[\n]/]},
    {"name": "chars$ebnf$1", "symbols": [/[^\n]/]},
    {"name": "chars$ebnf$1", "symbols": ["chars$ebnf$1", /[^\n]/], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "chars", "symbols": ["chars$ebnf$1"], "postprocess": function(d) { return d[0].join(""); }},
    {"name": "comment$ebnf$1", "symbols": []},
    {"name": "comment$ebnf$1", "symbols": ["comment$ebnf$1", "anyLine"], "postprocess": function arrpush(d) {return d[0].concat([d[1]]);}},
    {"name": "comment", "symbols": ["comment_start", "comment$ebnf$1", "comment_end"], "postprocess": function(d){ return d[1];}},
    {"name": "not_asterisk", "symbols": [/[^\*\n]/]},
    {"name": "an_asterisk", "symbols": [/[\*]/]}
]
  , ParserStart: "file"
}
if (typeof module !== 'undefined'&& typeof module.exports !== 'undefined') {
   module.exports = grammar;
} else {
   window.book = grammar;
}
})();
