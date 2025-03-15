//https://winkjs.org/wink-nlp/wink-nlp-in-browsers.html
//browserify test.js -o bundle.js
const winkNLP = require( 'wink-nlp' );
const model = require( 'wink-eng-lite-web-model' );
const nlp = winkNLP( model )
global.nlp = module.exports
// Acquire "its" and "as" helpers from nlp.
const its = nlp.its;
const as = nlp.as;

// Define a function to read a document from a text string
function readDoc(text) {
    // Parse the document object using the readDoc function
    const doc = nlp.readDoc(text);
    
    // Extract specific information from the document object
    doc.entities().each((e) => e.markup());
    
    // Return the parsed document object
    return doc.out(its.markedUpText);
}
    
// Test the readDoc function
teststr = "Its quarterly profits jumped 76% to $1.13 billion for the three months to December, from $639million of previous year.";
document.getElementById("result").innerHTML = readDoc(teststr);

