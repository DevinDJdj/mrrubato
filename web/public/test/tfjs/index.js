let net;
//Adding the webcam
const webcamElement = document.getElementById('webcam');
const classifier = knnClassifier.create();
async function setupWebcam() {
  return new Promise((resolve, reject) => {
    const navigatorAny = navigator;
    navigator.getUserMedia = navigator.getUserMedia ||
        navigatorAny.webkitGetUserMedia || navigatorAny.mozGetUserMedia ||
        navigatorAny.msGetUserMedia;
if (navigator.getUserMedia) {
      navigator.getUserMedia({video: true},
        stream => {
          webcamElement.srcObject = stream;
          webcamElement.addEventListener('loadeddata',  () => resolve(), false);
        },
        error => reject());
    } else {
      reject();
    }
  });
}
async function app() {
  document.getElementById('console').innerText = `Loading mobilenet..`;
  // Load the model.
  net = await mobilenet.load();
  document.getElementById('console').innerText = 'Sucessfully loaded model';
  await setupWebcam();
  // Reads an image from the webcam and associates it with a specific class
  // index.
  const addExample = classId => {
    // Get the intermediate activation of MobileNet 'conv_preds' and pass that
    // to the KNN classifier.
    const activation = net.infer(webcamElement, 'conv_preds');
    // Pass the intermediate activation to the classifier.
    classifier.addExample(activation, classId);
  };
// When clicking a button, add an example for that class.
  document.getElementById('class-a').addEventListener('click', () => addExample(0));
  document.getElementById('class-b').addEventListener('click', () => addExample(1));
  document.getElementById('class-c').addEventListener('click', () => addExample(2));
while (true) {
    if (classifier.getNumClasses() > 0) {
      // Get the activation from mobilenet from the webcam.
      const activation = net.infer(webcamElement, 'conv_preds');
      // Get the most likely class and confidences from the classifier module.
      const result = await classifier.predictClass(activation);
const classes = ['Object 1', 'Object 2', 'Object 3'];
if (typeof result.confidences[result.classIndex] == 'undefined' ){
         document.getElementById('console').innerText = ``;
        return;
      }
      if(result.confidences[result.classIndex] <0.5){
        document.getElementById('console').innerText = `
        Not a great prediction! \n
        prediction: ${classes[result.classIndex]}\n
        probability: ${result.confidences[result.classIndex]}
        `;
}
      else{
          document.getElementById('console').innerText = `
          prediction: ${classes[result.classIndex]}\n
          probability: ${result.confidences[result.classIndex]}
        `;
      } 
    }
    else{ //we will use mindNet
      const result2 = await net.classify(webcamElement);
document.getElementById('console').innerText = `
      Currently using: MobileNet Model \n
      Add Classes to start training and using your own classifier using the KNN Classifier  using the buttons below!!\n \n
        prediction: ${result2[0].className}\n
        probability: ${result2[0].probability}
      `;
      }
    await tf.nextFrame();
  }
}
app();