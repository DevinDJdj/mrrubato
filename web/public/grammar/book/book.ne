#adapt from
#https://github.com/kach/nearley/blob/master/examples/csv.ne
#https://github.com/kach/nearley/blob/master/examples/classic_crontab.ne
#nearleyc grammar/book/book.ne -o grammar/book/book.js -e book
#nearley-unparse grammar/book/book.js -d 10
#nearley-test -i "**MYTOPIC\nSome comment" grammar/book/book.js


@{%
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

%}



file              -> rows             {% function(d){ console.log("rows"); console.log(d); return { rows: d[0] }; } %}



rows              ->  rows topic   {% appendItemA(0,1) %}
                    | topic                    


startt        -> an_asterisk an_asterisk chars                  {% function(d){ console.log(d);console.log(topicarray); currentTopic = "**" + d[2]; return d[0] + d[1] + d[2]; } %}
                



cmd               -> ">" chars {% function(d) { return {cmd: d[1]}; } %}
comment_start     -> "<!--"  {% commentStart %}
comment_end       -> "-->"   {% commentEnd %}
question          -> "@@" chars  {% function(d) { return d[1]; }%}
environment_var   -> "$$" chars  {% function(d) { return d[1]; }%}
note_             -> "--":+ chars  {% function(d) { return d[1]; }%}
subtask_          -> "-":+ chars  {% function(d) { return d[1]; }%}
reference_        -> "#":+ chars  {% function(d) { myrefarray.push(d[1]); return d[1]; }%}
anyrow            -> not_asterisk  {% function(d) { return d[0] + ""; } %} 
                    | an_asterisk  {% function(d) { return d[0] + ""; } %}
                    | not_asterisk chars  {% function(d) { return d[0] + d[1]; }%}
                    | null {% emptyStr %}



anyLine           -> cmd                       {% id %}
                    | question                  {% id %}
                    | environment_var           {% id %}
                    | note_                     {% id %}
                    | subtask_                  {% id %}
                    | reference_                {% id %}
                    | anyrow                    {% id %}


#topic             -> startt anyLine:*                 {% updTopic %}
topic             -> startt newline                        {% startTopic %}
                    | topic anyLine newline               {% appendItemA(0,1) %}

newline           -> [\r\n]
                    | [\n]                          {% emptyStr %}

chars           ->  [^\n]:+        {% function(d) { return d[0].join(""); } %}


                    
comment           -> comment_start anyLine:* comment_end     {% function(d){ return d[1];} %}

not_asterisk        -> [^\*\n]
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

