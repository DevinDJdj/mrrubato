let classifier;
let video;
let canvas;

function setup() {
    // Create a canvas and place it inside the container div
    canvas = createCanvas(320, 240);
    canvas.parent('container');

    // Create a video element and start the webcam
    video = createCapture(VIDEO);
    video.size(320, 240);
    // Hide the default video element
    video.hide(); 
   

    // Initialize the image classifier with MobileNet
    classifier = ml5.imageClassifier('MobileNet', video, modelReady);
}

function draw() {
    // Draw the video feed to the canvas
    image(video, 0, 0, width, height); // Ensure the video is drawn to fill the canvas
}

function modelReady() {
    console.log('Model is ready!');
}

function saveModel() {
    console.log('Model saved!');
    alert('Model saved!');
    // Placeholder for save model logic
}

function trainModel() {
    if (classifier) {
        console.log('Training the model...');
        alert('Training the model...');
        // Placeholder for training logic
    } else {
        console.error('Classifier not ready.');
    }
}

// Add event listeners after the DOM has fully loaded
window.onload = function () {
    const saveButton = document.getElementById('saveButton');
    const trainButton = document.getElementById('trainButton');

    if (saveButton && trainButton) {
        saveButton.addEventListener('click', saveModel);
        trainButton.addEventListener('click', trainModel);
    } else {
        console.error('Buttons not found in the DOM.');
    }
};

// Ensure setup is called to initialize the classifier and webcam
setup();