//too much trouble to change these.  
var midiarray = [{"base": []}];
var users = [];

MAX_LOCAL_QUERY_LENGTH = 8000; //maximum length of local query.  This is the maximum length of the context that will be sent to the LLM.
var currentmidiuser = 0;
var pedal = false;
var currentlanguage = "base";
var lastnote = null;

var feedbackdelay = 10; //10 seconds
var transcript = "";
