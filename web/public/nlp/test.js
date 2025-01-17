//https://winkjs.org/wink-nlp/wink-nlp-in-browsers.html
//browserify test.js -o bundle.js
const winkNLP = require( 'wink-nlp' );
const model = require( 'wink-eng-lite-web-model' );
const nlp = winkNLP( model )
global.nlp = module.exports
// Acquire "its" and "as" helpers from nlp.
const its = nlp.its;
const as = nlp.as;

const text = `Its quarterly profits jumped 76% to $1.13 billion for the three months to December, from $639million of previous year.`;
const doc = nlp.readDoc( text );

doc.entities().each((e) => e.markup());
document.getElementById("result").innerHTML = doc.out(its.markedUpText);