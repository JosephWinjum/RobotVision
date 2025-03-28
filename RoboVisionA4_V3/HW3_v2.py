import pyrealsense2 as rs
import numpy as np
import cv2
from   picamera2 import Preview
import time
from maestro import Controller
import tkinter as tk
import pickle
import os
import threading


move_forward = False

move_backward = False

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

def move_forwards():
    start_time = time.time()
    while (time.time() - start_time < 2):
        t.Tango.setTarget(0, 5200)

    t.Tango.setTarget(0, 6000)
    global move_forward 
    move_forward = False
   

def move_backwards():
    start_time = time.time()
    while (time.time() - start_time < 2):
        t.Tango.setTarget(0, 6800)
    t.Tango.setTarget(0,6000)
    global move_backward 
    move_backward = False
   
 


###########
root = tk.Tk()
root.title("Face Recognizer")
display_text = tk.StringVar(value="No face detected")
display_label = tk.Label(root, textvariable=display_text, font=("Times New Roman", 24))
display_label.pack()


class Tango:
    def __init__(self):
        self.Tango = Controller()


# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
t = Tango()
t.Tango.setTarget(0, 5200)
t.Tango.setTarget(1, 5200)
t.Tango.setTarget(0, 6000)
t.Tango.setTarget(1, 6000)
time.sleep(1)





# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)


try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', color_image)
        cv2.waitKey(1)

        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
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
                move_forwards()
            else:
                text = "Stranger Danger"
                display_text.set("Stranger Danger")
                move_backwards()

            # rectangel around face
            cv2.rectangle(color_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(color_image, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        cv2.imshow("Face Recognition", color_image)
        root.update_idletasks()
        root.update()

        # q to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    exit(0)

finally:
    pipeline.stop()

