#adapt from
#https://github.com/kach/nearley/blob/master/examples/csv.ne
#https://github.com/kach/nearley/blob/master/examples/classic_crontab.ne
#nearleyc grammar/book/book.ne -o grammar/book/book.js -e book


@{%
var appendItem = function (a, b) { 
    return function (d) { 
        return d[a].concat([d[b]]); 
        } 
    };
var empty = function (d) { return []; };
var emptyStr = function (d) { return ""; };
var currentState = null;
var currentTopic = null;
%}

file              -> newline rows             {% function (d) { return { rows: d[1] }; } %}

rows              -> row                        
                    | rows newline row                {% appendItem(0,2) %}

row               -> comment                   {% id %}
                    | topic                    {% id %}

topic             -> startt                 {% function(d){ return [d[0]];} %}
                    | startt newline anyLine        {% appendItem(0, 2) %}
                    | topic newline anyLine             {% appendItem(0, 2) %}

comment           -> comment_start rows comment_end

anyLine           -> cmd                       {% id %}
                    | comment_start                  {% id %}
                    | comment_end                  {% id %}
                    | question                  {% id %}
                    | environment_var           {% id %}
                    | note_                     {% id %}
                    | subtask_                  {% id %}
                    | reference_                {% id %}
                    | anyrow                    {% id %}

                    

startt        -> "**" [^\n]:* {% newTopic %}


cmd               -> ">" [^\n]:* {% id %}
comment_start     -> "<!--" newline {% commentStart %}
comment_end       -> "-->" newline  {% commentEnd %}
question          -> "@@" [^\n]:* {% function(d) { return d[0]; }%}
environment_var   -> "$$" [^\n]:* {% function(d) { return d[0]; }%}
note_             -> "--":+ [^\n]:* {% function(d) { return d[0]; }%}
subtask_          -> "-":+ [^\n]:* {% function(d) { return d[0]; }%}
reference_          -> "#":+ [^\n]:* {% function(d) { return d[0]; }%}
anyrow            -> [^\n]:* {% function(d) { return d[0]; }%}


newline           -> "\r" "\n"                       {% empty %}
                    | "\r" | "\n"                     {% empty %}

@{%
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

%}
