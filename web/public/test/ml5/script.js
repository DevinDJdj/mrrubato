// set global - needed for external libraries
/* globals ml5 */

let message = document.querySelector("#message")
let myNeuralNetwork

function start() {
  const options = {
    dataUrl: "./iris.csv",
    inputs: ["sepal_length", "sepal_width", "petal_length", "petal_width"],
    outputs: ["species"],
    task: "classification",
    debug: true,
  }


  // uncomment to create the neural network
  myNeuralNetwork = ml5.neuralNetwork(options, dataLoaded)  
}

function dataLoaded() {
    message.innerHTML = "Finished loading - Start training"
  
    myNeuralNetwork.normalizeData()
    const trainingOptions = {
        epochs: 32,
        batchSize: 12
    }
    
    myNeuralNetwork.train(trainingOptions, finishedTraining)
}

function finishedTraining() {
    console.log("Finished training!")
    message.innerHTML = "Finished training"
  
    // to do: test if we can classify a new flower
    classify([4.9,3,1.4,0.2])
    // to do: save the model. in part 2 we will load the model
    // myNeuralNetwork.save()
}

function classify(input) {
    myNeuralNetwork.classify(input, handleResults)
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



// use these options for yoga training
/*
// options for yoga poses
const options = {
    dataUrl: './yoga.csv',
    inputs: ['leftAnklex','leftAnkley','leftEarx','leftEary','leftElbowx','leftElbowy','leftEyex','leftEyey','leftHipx','leftHipy','leftKneex','leftKneey','leftShoulderx','leftShouldery','leftWristx','leftWristy','nosex','nosey','rightAnklex','rightAnkley','rightEarx','rightEary','rightElbowx','rightElbowy','rightEyex','rightEyey','rightHipx','rightHipy','rightKneex','rightKneey','rightShoulderx','rightShouldery','rightWristx','rightWristy'],
    outputs: ['yogapose'],
    task: 'classification',
    debug: true
}
*/