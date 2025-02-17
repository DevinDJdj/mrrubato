// import { Hands } from '@mediapipe/hands';
// import { Camera } from '@mediapipe/camera_utils';
// import { FaceMesh } from '@mediapipe/face_mesh';
// import { Pose } from '@mediapipe/pose';
// import * as Tone from 'tone';

const Hands = window.Hands;
const Camera = window.Camera;
const FaceMesh = window.FaceMesh;
const Pose = window.Pose;
const Tone = window.Tone;

// document.documentElement.addEventListener('mousedown', async () => {
//     if (Tone.context.state !== 'running') {
//         await Tone.start();
//         console.log('audio is ready');
//     }
//     synth.triggerAttackRelease('C4', '8n');
// });

const videoElement = document.getElementById('videoInput');
const canvasElement = document.getElementById('outputCanvas');
const canvasCtx = canvasElement.getContext('2d');

// Initialize MediaPipe Hands
const handsInstance = new Hands({
    locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
});
handsInstance.setOptions({
    maxNumHands: 2,
    modelComplexity: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});
handsInstance.onResults(onResults);

// Initialize MediaPipe FaceMesh
const faceMeshInstance = new FaceMesh({
    locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
});
faceMeshInstance.setOptions({
    maxNumFaces: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});
faceMeshInstance.onResults(onFaceResults);

// Initialize MediaPipe Pose
const poseInstance = new Pose({
    locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
});
poseInstance.setOptions({
    modelComplexity: 1,
    smoothLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});
// poseInstance.onResults(onPoseResults);

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize the webcam
    const cameraInstance = new Camera(videoElement, {
        onFrame: async () => {
            // Clear the canvas and draw the video frame first
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

            // Then process the frame with MediaPipe
            await handsInstance.send({ image: videoElement });
            await faceMeshInstance.send({ image: videoElement });
            await poseInstance.send({ image: videoElement });
        },
        width: 640,
        height: 480
    });
    cameraInstance.start();
});

// Initialize Tone.js Synthesizer and Recorder
const synth = new Tone.Synth().toDestination();
const recorder = new Tone.Recorder();
synth.connect(recorder);
let isRecording = false;
const player = new Tone.Player().toDestination();

// Function to start recording
function startRecording() {
    recorder.start();
    isRecording = true;
}

// Function to stop recording and save the loop
async function stopRecording() {
    isRecording = false;
    const recording = await recorder.stop();
    player.load(recording);
}

// Function to toggle loop playback
function toggleLoopPlayback(action) {
    if (action === 'play' && player.state !== 'started') {
        player.start();
    } else if (action === 'stop' && player.state === 'started') {
        player.stop();
    }
}

// Create two synthesizers with envelopes
const synthLeft = new Tone.Synth({
    envelope: {
        attack: 0.1,
        decay: 0.2,
        sustain: 0.5,
        release: 1
    }
}).toDestination();

const synthRight = new Tone.Synth({
    envelope: {
        attack: 0.1,
        decay: 0.2,
        sustain: 1,
        release: 1
    }
}).toDestination();

// Create flags for each synth
let isPlayingLeft = false;
let isPlayingRight = false;

let previousPositionLeft = null;
let previousPositionRight = null;

function onResults(results) {
    if (results.multiHandLandmarks) {
        for (let i = 0; i < results.multiHandLandmarks.length; i++) {
            const landmarks = results.multiHandLandmarks[i];
            const handedness = results.multiHandedness[i].label; // 'Left' or 'Right'

            for (let j = 0; j < landmarks.length; j++) {
                const x = landmarks[j].x * canvasElement.width;
                const y = landmarks[j].y * canvasElement.height;

                // Calculate the speed of the hand movement
                let speed;
                if (handedness === 'Left') {
                    if (previousPositionLeft) {
                        speed = Math.sqrt(Math.pow(x - previousPositionLeft.x, 2) + Math.pow(y - previousPositionLeft.y, 2));
                    }
                    previousPositionLeft = { x, y };
                } else {
                    if (previousPositionRight) {
                        speed = Math.sqrt(Math.pow(x - previousPositionRight.x, 2) + Math.pow(y - previousPositionRight.y, 2));
                    }
                    previousPositionRight = { x, y };
                }
                // Adjust the duration of the note based on the speed of the hand movement
                // const duration = speed ? Math.max(0.3, 1 / speed) : '8n';

                // Calculate the distance between the thumb (landmark 4) and the index finger (landmark 8)
                const thumb = landmarks[4];
                const indexFinger = landmarks[8];
                const distance = Math.sqrt(Math.pow(thumb.x - indexFinger.x, 2) + Math.pow(thumb.y - indexFinger.y, 2));

                // Normalize the distance to the range [0, 1]
                let normalizedDistance = Math.max(0, Math.min(distance, 1));

                // Ensure normalizedDistance is a number
                if (isNaN(normalizedDistance)) {
                    normalizedDistance = 0;
                }

                // Adjust the duration of the note based on the distance
                // const duration = normalizedDistance * '8n';

                // Multiply the normalized distance by a factor to make it more sensitive
                let sensitivityFactor = 2; // Adjust this value to increase or decrease sensitivity
                let duration = normalizedDistance * sensitivityFactor;

                // Convert duration to a note duration string
                // duration = duration.toFixed(0) + 'n';

                // Draw a circle at the landmark position
                canvasCtx.beginPath();
                canvasCtx.arc(x, y, 5, 0, 2 * Math.PI);
                canvasCtx.fillStyle = handedness === 'Left' ? 'blue' : 'yellow';
                canvasCtx.fill();

                // Define scales for left and right hands
                // const scaleLeft = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5'];
                // const scaleRight = ['C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5', 'C6'];
                const scaleLeft = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']; // C Major scale
                const scaleRight = ['A4', 'B4', 'C5', 'D5', 'E5', 'F5', 'G5', 'A5']; // A minor scale

                // Calculate the volume based on the y-coordinate
                let volume = 0;
                if (y !== null && canvasElement.height !== 0) {
                    volume = 1 - (y / canvasElement.height);
                }
                // Clamp volume to the range [0, 1]
                volume = Math.max(0, Math.min(volume, 1));

                if (handedness === 'Left' && !isPlayingLeft) {
                    // For the left hand, generate a musical note with Tone.js using the left hand scale
                    const note = scaleLeft[Math.floor((x / canvasElement.width) * scaleLeft.length)];
                    synthLeft.volume.value = Tone.gainToDb(volume); // Set the volume
                    synthLeft.triggerAttackRelease(note, duration);
                    isPlayingLeft = true;
                    setTimeout(() => { isPlayingLeft = false; }, 500); // Set the flag to false after the duration of the note
                } else if (handedness === 'Right' && !isPlayingRight) {
                    // For the right hand, generate a musical note with Tone.js using the right hand scale
                    const note = scaleRight[Math.floor((x / canvasElement.width) * scaleRight.length)];
                    synthRight.volume.value = Tone.gainToDb(volume); // Set the volume
                    synthRight.triggerAttackRelease(note, duration);
                    isPlayingRight = true;
                    setTimeout(() => { isPlayingRight = false; }, 500); // Set the flag to false after the duration of the note
                }
            }
        }
    }
}



// Process results from MediaPipe FaceMesh
function onFaceResults(results) {
    if (results.multiFaceLandmarks) {
        for (let i = 0; i < results.multiFaceLandmarks.length; i++) {
            const landmarks = results.multiFaceLandmarks[i];
            for (let j = 0; j < landmarks.length; j++) {
                const x = landmarks[j].x * canvasElement.width;
                const y = landmarks[j].y * canvasElement.height;
                canvasCtx.beginPath();
                canvasCtx.arc(x, y, 2, 0, 2 * Math.PI); // Draw a circle with a radius of 2.5 pixels at the landmark position
                canvasCtx.fillStyle = 'green';
                canvasCtx.fill();
            }
        }
    }
}

// Process results from MediaPipe Pose
function onPoseResults(results) {
    if (results.poseLandmarks) {
        for (let i = 0; i < results.poseLandmarks.length; i++) {
            const x = results.poseLandmarks[i].x * canvasElement.width;
            const y = results.poseLandmarks[i].y * canvasElement.height;
            canvasCtx.fillStyle = 'blue';
            canvasCtx.fillRect(x, y, 5, 5); // Draw a 5x5 pixel rectangle at the landmark position
        }
    }
}

function onHandResults(results) {
    if (results.multiHandLandmarks) {
        for (const landmarks of results.multiHandLandmarks) {
            let fingerCount = countExtendedFingers(landmarks);
            playChord(fingerCount);
        }
    }
}


// Import necessary modules from Tone.js and MediaPipe
// Make sure to include these libraries in your HTML file

const polySynth = new Tone.PolySynth(Tone.Synth).toDestination();

// Function to count extended fingers
function countExtendedFingers(landmarks) {
    // Implement the logic to count extended fingers
    // You can use the angle between landmarks or the distance between them to determine if a finger is extended
    // Return the count of extended fingers
    // This is a placeholder function, you'll need to implement the actual logic
}

// Function to play chords based on the number of extended fingers
function playChord(fingerCount) {
    const chordMap = {
        1: ['C4'],
        2: ['C4', 'E4'],
        3: ['C4', 'E4', 'G4'],
        4: ['C4', 'E4', 'G4', 'B4'],
        5: ['C4', 'D4', 'E4', 'G4', 'A4'],
        // Add more mappings for different finger counts
    };

    let chord = chordMap[fingerCount];
    if (chord) {
        polySynth.triggerAttackRelease(chord, '1n');
    }
}

// MediaPipe Hands integration
const hands = new Hands({ /* ... MediaPipe Hands configuration ... */ });
hands.onResults(results => {
    if (results.multiHandLandmarks) {
        for (const landmarks of results.multiHandLandmarks) {
            let fingerCount = countExtendedFingers(landmarks);
            playChord(fingerCount);
        }
    }
});

// Initialize the MediaPipe Hands and other necessary components
// ...



// more code is coming
