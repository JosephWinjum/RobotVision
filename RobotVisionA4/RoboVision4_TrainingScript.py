import os
import cv2
import numpy as np
from PIL import Image
import pickle

image_dir = r"C:\Users\Josep\Desktop\Robotest4\FaceTraining\images"

# Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
face_cascade_eye = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
face_cascade_smile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

# =LBPH face recognizer (converts to grayscale, vector feature comparisons with surrounding pixels)
recognizer = cv2.face.LBPHFaceRecognizer_create()

#  variables to hold training data and labels
current_id = 0
label_ids = {}
x_train = []
y_labels = []

#every image
for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.endswith(("png", "jpg", 'jfif')):
            path = os.path.join(root, file)
            label = os.path.basename(root).lower()
            if label not in label_ids:
                label_ids[label] = current_id
                current_id += 1
            id = label_ids[label]

            # open image convert to gray
            pil_image = Image.open(path).convert("L")

            size = (800,800)
            final_image = pil_image.resize(size, Image.LANCZOS)
            image_array = np.array(final_image, "uint8")

            # detect faces in the image
            faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.1, minNeighbors=5)

            # crop for region of interest
            for (a, b, c ,d) in faces:
                roi = image_array[a:a+c, b:b+d]
                x_train.append(roi)
                y_labels.append(id)


            final_image.show()



for i in label_ids:
    print(i)


with open("labels.pickle", "wb") as f:
    pickle.dump(label_ids, f)

recognizer.train(x_train, np.array(y_labels))
recognizer.save("trainer.yml")
