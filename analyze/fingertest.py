#https://techvidvan.com/tutorials/hand-gesture-recognition-tensorflow-opencv/
#idea is to create something which recognizes which fingers are used with which notes with the midi file.  
#similar to analyze, but just testing if we can do this.  
#interesting cant use this while OBS is running for some reason.  
#anyway dont worry about real time for now.  
#looks like it will still display partial fingers?  Have to check with a MKV.  
#ok, seems ok, but Needed to add a little more space at the bottom of the piano.  
#I think thats fine.  This has some difficulty checking the thumb.  
#so check perhaps after some newer videos.  
#doesnt work great.  Really needs the arm it seems from this model.  
#so for us work back from the midi, and try to determine which finger it was.  
#maybe we can use this?  Yeah dont want to do this work myself so use something like this. 
#just combine intelligently with detection of the keys themselves, and correlate with midi.  
#what time was the button pressed?  Which finger was there at that time?  
#can we detect from the video pressed or not?  
#not sure if it is worth it if the midi timing is precise enough.  
#thumb detection is bad with low confidence.  
#check after some more videos.  


#maybe it is an exclusive stream?  
#pip install mediapipe
#pip install tensorflow


import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model

# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.2)
mpDraw = mp.solutions.drawing_utils

# Load the gesture recognizer model
model = load_model('mp_hand_gesture')

# Load class names
f = open('./mp_hand_gesture/gesture.names', 'r')
classNames = f.read().split('\n')
f.close()
print(classNames)


# Initialize the webcam
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("C:\\Users\\devin\\Videos\\2023-08-03 15-38-56.mkv")


while True:
    # Read each frame from the webcam
    ret, frame = cap.read()

    x, y, c = frame.shape

    # Flip the frame vertically
#    frame = cv2.flip(frame, 1)
    keys = frame[780:x, 0:y]
    framergb = cv2.cvtColor(keys, cv2.COLOR_BGR2RGB)

    # Get hand landmark prediction
    result = hands.process(framergb)

    # print(result)
    
    className = ''

    # post process the result
    if result.multi_hand_landmarks:
        landmarks = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                # print(id, lm)
                lmx = int(lm.x * x)
                lmy = int(lm.y * y)

                landmarks.append([lmx, lmy])

            # Drawing landmarks on frames
            mpDraw.draw_landmarks(keys, handslms, mpHands.HAND_CONNECTIONS)

            # Predict gesture
#            prediction = model.predict([landmarks])
            # print(prediction)
#            classID = np.argmax(prediction)
#            className = classNames[classID]

    # show the prediction on the frame
    cv2.putText(keys, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (0,0,255), 2, cv2.LINE_AA)

    # Show the final output
#    keys = frame[780:x, 0:y]
    cv2.imshow("Output", keys) 

    if cv2.waitKey(1) == ord('q'):
        break

# release the webcam and destroy all active windows
cap.release()

cv2.destroyAllWindows()

