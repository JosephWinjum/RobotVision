import os

import cv2
import numpy as np
import pickle
#bc looking in wrong location
os.environ['TCL_LIBRARY'] = r'C:\Users\Josep\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\Josep\AppData\Local\Programs\Python\Python313\tcl\tk8.6'
import tkinter as tk
import time
import pyrealsense2 as rs
from picamera2 import Preview
from maestro import Controller


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

with open("labels.pickle", "rb") as f:
    label_ids = pickle.load(f)
# map id to label
id_to_label = {}
for label_name, numeric_id in label_ids.items():
    id_to_label[numeric_id] = label_name


#initialization
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#it was reading me as fairlyh well at like 60% confidence, so adjust as needed
CONFIDENCE_THRESHOLD = 65

def move_forward(distance):
    print(f"Moving forward {distance} feet...")
    time.sleep(1)

def move_backward(distance):
    print(f"Moving backward {distance} feet...")
    time.sleep(1)

###########
root = tk.Tk()
root.title("Face Recognizer")
display_text = tk.StringVar(value="No face detected")
display_label = tk.Label(root, textvariable=display_text, font=("Times New Roman", 24))
display_label.pack()

# realsense stuff
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

#my webcam
#cap = cv2.VideoCapture(0)
class Tango:
    def __init__(self):
        self.Tango = Controller()

t = Tango()

while True:
    ret, frame = pipeline.read()
    if not ret:
        print("Failed frame grab")
        break


    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        #same as training, region of interest
        roi_gray = gray[y:y+h, x:x+w]

        # this changes slightly between training batches, also more pictures better, if bad detection add more pictures
        # and its better to look at camera directly in pictures + less background stuff
        id_pred, confidence = recognizer.predict(roi_gray)
        # lower is better (inverted)
        if confidence < CONFIDENCE_THRESHOLD:
            name = id_to_label.get(id_pred, "UNKNOWN")
            text = f"{name} ({round(confidence,2)})"
            display_text.set(name)
            #move forward code
        else:
            text = "Stranger Danger"
            display_text.set("Stranger Danger")
            # move backward code

        # rectangel around face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    cv2.imshow("Face Recognition", frame)
    root.update_idletasks()
    root.update()

    # q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
root.destroy()


