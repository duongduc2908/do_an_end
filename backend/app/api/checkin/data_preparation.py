import cv2
from feature_extraction.extractor import FaceVector
from face_detection.face_detection import detect_face
from imutils import paths
import numpy as np
import pickle
import cv2
import os
import time
import pickle

face_vector = FaceVector()

BLACK = [0, 0, 0]


imagePaths = list(paths.list_images('/home/ducdv10/Downloads/do_an_end/backend/app/template/image/train'))
X = []
labels = []
if os.path.isfile("data/X_train.pkl"):
	X = pickle.load(open("data/X_train.pkl", 'rb'))
if os.path.isfile("data/label_train.pkl"):
    labels = pickle.load(open("data/label_train.pkl", 'rb'))

for imagePath in imagePaths:
	label = imagePath.split(os.path.sep)[-2]
	print(label)
	image = cv2.imread(imagePath)
	t0=time.time()
	bbs, points = detect_face(image)
	if len(bbs)>0:
		t0 = time.time()
		emb=face_vector.get_vector(image, bbs[0],points)		
		print('Embeding:',time.time() - t0)
		labels.append(label)
		X.append(emb)
				
filename='data/X_train.pkl'
pickle.dump(X, open(filename,'wb'))

filename='data/label_train.pkl'
pickle.dump(labels, open(filename,'wb'))

