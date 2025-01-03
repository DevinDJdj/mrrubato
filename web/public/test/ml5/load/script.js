// set global - needed for external libraries
/* globals ml5 */

const message = document.querySelector("#message")

let nn

function start(){
    nn = ml5.neuralNetwork({task: 'classification'})

    // in the previous exercise we received three files for the trained model.
    // upload these files to this glitch project, and enter the urls here.
    // note that the .bin file has a special assets url!
    const modelInfo = {
        model: './model.json',
        metadata: './model_meta.json',
        weights: 'https://cdn.glitch.me/a8eacb87-6843-4dda-88d5-fb8ec9cde9af/model.weights.bin?v=1641327207167',
    }
    
    nn.load(modelInfo, modelLoaded)
    
}

function modelLoaded() {
    message.innerHTML = "Model loaded - start classifying"
    console.log("classify iris flower")
    // iris flower has: sepal_length, sepal_width,p etal_length, petal_width
    // invent a new flower with four numbers and classify which iris flower it is:
    classify([2,3.5,5,7])    
}

function classify(input) {
    nn.classify(input, handleResults)
}

function handleResults(result, error) {
    if (error) console.error(error)
    console.log(result[0].label + " confidence:" + result[0].confidence)
    message.innerHTML = result[0].label + " confidence:" + result[0].confidence
}


tf.ready().then(() => { 
    console.log(tf.backend().blockSize) 
    start();
  });
