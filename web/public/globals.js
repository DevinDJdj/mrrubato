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
var currenttopic = "NONE";
var selectedtopic = "NONE";

//MLC Engine models to use.  
let selectedModel = "Llama-3.2-1B-Instruct-q4f16_1-MLC";
//selectedModel = "DeepSeek-R1-Distill-Qwen-7B-q4f16_1-MLC";
//selectedModel = "DeepSeek-R1-Distill-Qwen-1.5B-q4f16_1-MLC"; //this will be faster/better.  
//selectedModel = "TinyLlama-1.1B-Chat-v0.4-q4f16_1-MLC";
//selectedModel = "Qwen2.5-Coder-7B-Instruct-q4f32_1-MLC";
//selectedModel = "gemma-2-2b-it-q4f32_1-MLC"; //See if we can use this?  
//I think I like this model, but it was causing sparks..
let embedModel = "snowflake-arctic-embed-m-q0f32-MLC-b4";
