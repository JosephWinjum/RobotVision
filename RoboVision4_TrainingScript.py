import os
import cv2
import numpy as np
from PIL import Image, ExifTags
import pickle
#you have to install opencv-contrib-python instead of opencv-python to get cv2.face.LBPH to work.

image_dir = r"C:\Users\Josep\Desktop\RoboVisionA4_V3\FaceTraining\images"

# Haar Cascade (cv2.data, other deprecated
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
face_cascade_eye = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
face_cascade_smile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

# LBPH face recognizer (converts to grayscale, vector feature comparisons with surrounding pixels)
recognizer = cv2.face.LBPHFaceRecognizer_create()

#  variables to hold training data and labels
current_id = 0
label_ids = {}
x_train = []
y_labels = []

#my pictures were oriented wrong as windows auto orients, this reorients correctly
def fix_image_orient(pil_image):
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break

    exif = pil_image.getexif()

    if exif is not None:
        orientation_value = exif.get(orientation, None)

        if orientation_value == 3:
            pil_image = pil_image.rotate(180, expand=True)
        elif orientation_value == 6:
            pil_image = pil_image.rotate(270, expand=True)
        elif orientation_value == 8:
            pil_image = pil_image.rotate(90, expand=True)

    if (AttributeError, KeyError, IndexError):
        print("no orient data found")

    return pil_image

#every image
for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.endswith(("png", "jpg", 'jfif')):
            path = os.path.join(root, file)
            label = os.path.basename(root).lower()
            # Manual, stable label mapping
            manual_label_ids = {
                "hunter": 1,
                "joey": 2
            }

            label = os.path.basename(root).lower()
            id = manual_label_ids[label]

            # open image convert to gray
            pil_image = Image.open(path).convert("L")
            pil_image_fixed = fix_image_orient(pil_image)
            #pil_image_fixed.show()

            size = (800,800)

            final_image = pil_image_fixed.resize(size, Image.LANCZOS)
            image_array = np.array(final_image, "uint8")

            # detect faces in the image
            faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.1, minNeighbors=5)
            #in case no face is detected to train on which might happen, I added pictures as initially there were 4 that weren't (1 of hunters)
            if len(faces) == 0:
                print(f"no face detected")

            # crop for region of interest
            for (x, y, w, h) in faces:
                roi = image_array[y:y+h, x:x+w]
                x_train.append(roi)
                y_labels.append(id)


with open("labels.pickle", "wb") as f:
    pickle.dump(manual_label_ids, f)

recognizer.train(x_train, np.array(y_labels))
recognizer.save("trainer.yml")
