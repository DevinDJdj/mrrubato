// Generated automatically by nearley, version 2.20.1
// http://github.com/Hardmath123/nearley
(function () {
function id(x) { return x[0]; }

var appendItem = function (a, b) { return function (d) { return d[a].concat([d[b]]); } };
var appendItemChar = function (a, b) { return function (d) { return d[a].concat(d[b]); } };
var empty = function (d) { return []; };
var emptyStr = function (d) { return ""; };
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
    {"name": "file", "symbols": ["rows"], "postprocess": function (d) { console.log(d); return { rows: d[0] }; }},
    {"name": "header", "symbols": ["row"], "postprocess": id},
    {"name": "rows", "symbols": ["row"]},
    {"name": "rows", "symbols": ["rows", "newline", "row"], "postprocess": appendItem(0,2)},
    {"name": "topic$string$1", "symbols": [{"literal":"*"}, {"literal":"*"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "topic", "symbols": ["topic$string$1", "any_line"], "postprocess": function(d){ return d[1].join(""); }},
    {"name": "cmd", "symbols": [{"literal":">"}, "any_line"], "postprocess": function(d){ return d[1].join(""); }},
    {"name": "question$string$1", "symbols": [{"literal":"@"}, {"literal":"@"}], "postprocess": function joiner(d) {return d.join('');}},
    {"name": "question", "symbols": ["question$string$1", "any_line"], "postprocess": function(d){ return d[1].join(""); }},
    {"name": "special_line", "symbols": [/[^@>\*]/, "any_line"], "postprocess": function(d){ return d[0] + d[1].join(""); }},
    {"name": "any_line", "symbols": []},
    {"name": "any_line", "symbols": ["any_line", "char"], "postprocess": appendItemChar(0,1)},
    {"name": "any_line", "symbols": ["any_line", "special_char"], "postprocess": appendItemChar(0,1)},
    {"name": "row", "symbols": [], "postprocess": emptyStr},
    {"name": "row", "symbols": ["topic"], "postprocess": function (d) { return { topic: d[0] }; }},
    {"name": "row", "symbols": ["cmd"], "postprocess": function (d) { return { cmd: d[0] }; }},
    {"name": "row", "symbols": ["question"], "postprocess": function (d) { return { question: d[0] }; }},
    {"name": "row", "symbols": ["special_line"], "postprocess": function (d) { return d[0]; }},
    {"name": "field", "symbols": ["unquoted_field"], "postprocess": id},
    {"name": "field", "symbols": [{"literal":"\""}, "quoted_field", {"literal":"\""}], "postprocess": function (d) { return d[1]; }},
    {"name": "quoted_field", "symbols": [], "postprocess": emptyStr},
    {"name": "quoted_field", "symbols": ["quoted_field", "quoted_field_char"], "postprocess": appendItemChar(0,1)},
    {"name": "quoted_field_char", "symbols": [/[^"]/], "postprocess": id},
    {"name": "quoted_field_char", "symbols": [{"literal":"\""}, {"literal":"\""}], "postprocess": function (d) { return "\""; }},
    {"name": "unquoted_field", "symbols": [], "postprocess": emptyStr},
    {"name": "unquoted_field", "symbols": ["unquoted_field", "char"], "postprocess": appendItemChar(0,1)},
    {"name": "char", "symbols": [/[^\*\n\r",@>]/], "postprocess": id},
    {"name": "special_char", "symbols": [/[@>\*]/], "postprocess": id},
    {"name": "newline", "symbols": [{"literal":"\r"}, {"literal":"\n"}], "postprocess": empty},
    {"name": "newline", "symbols": [{"literal":"\r"}]},
    {"name": "newline", "symbols": [{"literal":"\n"}], "postprocess": empty},
    {"name": "an_asterisk", "symbols": [/[\*]/]}
]
  , ParserStart: "file"
}
if (typeof module !== 'undefined'&& typeof module.exports !== 'undefined') {
   module.exports = grammar;
} else {
   window.booka = grammar;
}
})();
