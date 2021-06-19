import cv2
from feature_extraction.extractor import FaceVector
from face_detection.face_detection import detect_face
from utils_pro.utils import set_key ,r
from imutils import paths
import numpy as np
import pickle
import os
import pickle
from sklearn import preprocessing
from novelty_v3 import PredictModel
from datetime import datetime
from time import time
import paho.mqtt.client as mqtt
from utils_pro.config import DroneDetectionConfig as cf
import json


def train_model(client, user, message):
    face_vector = FaceVector()
    BLACK = [0, 0, 0]

    str_date = datetime.now().strftime("%Y_%m_%d") 
    imagePaths = list(paths.list_images('/home/ducdv10/Downloads/do_an_end/backend/app/template/image/training/{}'.format(str_date)))
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
        bbs, points = detect_face(image)
        if len(bbs)>0:
            emb=face_vector.get_vector(image, bbs[0])	
            labels.append(label)
            X.append(emb)
                    
    filename='data/X_train.pkl'
    pickle.dump(X, open(filename,'wb'))

    filename='data/label_train.pkl'
    pickle.dump(labels, open(filename,'wb'))

    x_train=np.asarray(X)

    label_encoder = preprocessing.LabelEncoder()
    label_encoder=label_encoder.fit(labels)
    y_train = label_encoder.transform(labels)
    filename = 'models/name_model.pkl'
    with open(filename, 'wb') as fo:  
        pickle.dump(label_encoder, fo)

    novelty_detector = PredictModel()
    novelty_detector.fit(x_train, y_train)
    filename = 'models/face_model.pkl'
    with open(filename, 'wb') as fo:  
        pickle.dump(novelty_detector, fo)
    client_sub.publish(topic=cf.UPDATE_MODEL)
    set_key(r,"TEST")


client_sub = mqtt.Client("training_handler")
client_sub.connect(host=cf.BROKER_HOST, port=cf.BROKER_PORT)
client_sub.subscribe(cf.UPDATE_MODEL, qos=0)
client_sub.subscribe(cf.UPDATE_TRAINING, qos=0)
client_sub.message_callback_add(cf.UPDATE_TRAINING, train_model)
client_sub.loop_forever()
