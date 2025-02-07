# csv.ne
# from the Antlr grammar at: http://www.antlr3.org/grammar/list.html
# see also: https://github.com/antlr/grammars-v4
#nearleyc grammar/book/booka.ne -o grammar/book/booka.js -e booka
#nearley-unparse grammar/book/booka.js -d 10
#nearley-test -i "**MYTOPIC\nSome comment" grammar/book/booka.js


@{%
var appendItem = function (a, b) { return function (d) { return d[a].concat([d[b]]); } };
var appendItemChar = function (a, b) { return function (d) { return d[a].concat(d[b]); } };
var empty = function (d) { return []; };
var emptyStr = function (d) { return ""; };
var currentTopic = null;
var topicarray = {};
var refarray = [];

%}

#file              -> header newline rows             {% function (d) { console.log(d); return { header: d[0], rows: d[2] }; } %}
file                -> rows                           {% function (d) { console.log(d); return { rows: d[0] }; } %}

header            -> row                             {% id %}

rows              -> row
                    | rows newline row            {% appendItem(0,2) %}

topic             -> "**" any_line                     {% function(d){ return d[1].join(""); } %}
cmd                 -> ">" any_line                     {% function(d){ return d[1].join(""); } %}
question          -> "@@" any_line                      {% function(d){ return d[1].join(""); } %}
special_line        -> [^@>\*] any_line                     {% function(d){ return d[0] + d[1].join(""); } %}

any_line    ->    null                            
                   | any_line char             {% appendItemChar(0,1) %}
                   | any_line special_char      {% appendItemChar(0,1) %}


#row               -> field
#                   | row "," field                   {% appendItem(0,2) %}

row                 -> null                         {% emptyStr %}
                    | topic                          {% function (d) { return { topic: d[0] }; } %}
                    | cmd                            {% function (d) { return { cmd: d[0] }; } %}
                    | question                            {% function (d) { return { question: d[0] }; } %}
#                    | unquoted_field char          {% appendItemChar(0,1) %}
                    | special_line                        {% function (d) { return d[0]; } %}

field             -> unquoted_field                  {% id %}
                   | "\"" quoted_field "\""          {% function (d) { return d[1]; } %}

quoted_field      -> null                            {% emptyStr %}
                   | quoted_field quoted_field_char  {% appendItemChar(0,1) %}

quoted_field_char -> [^"]                            {% id %}
                   | "\"" "\""                       {% function (d) { return "\""; } %}

unquoted_field    -> null                            {% emptyStr %}
                   | unquoted_field char             {% appendItemChar(0,1) %}

char              -> [^\*\n\r",@>]                       {% id %}

special_char       -> [@>\*]                            {% id %}

newline           -> "\r" "\n"                       {% empty %}
                   | "\r" | "\n"                     {% empty %}


an_asterisk         -> [\*]



@{%
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

%}
