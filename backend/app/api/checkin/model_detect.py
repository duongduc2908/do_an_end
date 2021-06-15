import json
from time import sleep, time
from numpy.lib.type_check import imag
import paho.mqtt.client as mqtt
from datetime import datetime
from utils_pro.utils import load_stack_from_redis,load_bytes_from_redis,set_key, r
from utils_pro.config import DroneDetectionConfig as cf
from utils_pro.face_goodness_score import angle_score
from flask_jwt_extended import (
                    get_jwt_claims,
                    get_jwt_identity)
import sys
sys.path.append("/home/ducdv10/Downloads/do_an_end/backend/")
from app.utils import notification
import logging
import pickle
import cv2
from app.extensions import client as database
from bson import ObjectId
import os
from feature_extraction.extractor import FaceVector
from face_detection.face_detection import detect_face


face_vector = FaceVector()

svm_file='models/face_model.pkl'
svm = pickle.load(open(svm_file, 'rb'))
name_file='models/name_model.pkl'
name_model = pickle.load(open(name_file, 'rb'))
font = cv2.FONT_HERSHEY_SIMPLEX


local_image = [None,None,None,None,None] # return True if have image ['CENTER', 'LEFT','RIGHT','BOTTOM','UP']
logging.basicConfig(format=cf.LOGGING_FORMAT, datefmt=cf.LOGGING_DATEFMT, level=cf.LOGGING_LEVEL)
call = 0


def backend_to_model_stack_frame(client, user, message):
    flag_wait = True
    global call
    global local_image
    # Help to release all the stack retained in queue before more than 0.1s ago (or should be than 1/fps)
    json_payload = json.loads(message.payload)
    pub_timestamp = json_payload["timestamp"]
    now = datetime.now().timestamp()
    time_check = now - pub_timestamp
    if time_check > 0.1:
        logging.debug("[S-{}] Detect new stack. (skipped)".format(pub_timestamp))
        return None

    logging.debug("[S-{}] Detect new stack".format(pub_timestamp))
    flag_dict = load_bytes_from_redis(r,cf.FLAG_REDIS_KEY).decode('utf-8')
    print("========FLAG============= {}".format(flag_dict))
    names = []
    if flag_dict == "TEST":
        local_image = [None,None,None,None,None]
        stack_dict = load_stack_from_redis(r, cf.NEW_STACK_REDIS_KEY)
        if stack_dict:
            result = stack_dict["stack"]
            image = result[2,:,:,:]
            bbs, points = detect_face(image)
            scores = []
            str_date = datetime.now().strftime("%Y_%m_%d") 

            path_save = "/home/ducdv10/Downloads/do_an_end/backend/app/template/image/camera/{}".format(str_date)
            if not os.path.isdir(path_save):
                os.makedirs(path_save)

            # user_curr_id = get_jwt_identity()
            # claims = get_jwt_claims()

            for bb, point in zip(bbs, points):
                (l,t,r1,b)=bb
                emb=face_vector.get_vector(image, bb,point)		
                y_pred,label = svm.predict([[emb]])
                name=name_model.inverse_transform(label)
                
                if y_pred[0]>1:
                    name=['']
                img = image.copy()
                if len(name[0])>0:
                    cv2.rectangle(img,(l, t), (r1, b), (255, 0, 0), 2)
                else:
                    cv2.rectangle(img,(l, t), (r1, b), (255, 255, 0), 2)
                if t>30:		
                    cv2.putText(img,name[0],(l-6*(len(name[0])-4),t-10), font, 0.8,(0,255,0),2) 
                else:		
                    cv2.putText(img,name[0],(l-6*(len(name[0])-4),b+20), font, 0.8,(0,255,0),2)
                now = datetime.now()
                t = datetime.timestamp(now)
                cv2.imwrite(path_save+"/{}_{}.jpg".format(name[0],t),img)

                PATH_IMAGE_CAMERA_SEVER = "http://localhost:4321/image/camera"
                path_server = os.path.join(PATH_IMAGE_CAMERA_SEVER+"/{}".format(str_date), "{}_{}.jpg".format(name[0],t))
                detection_payload = json.dumps({"img_path": path_server})

                # user = client.db.user.find_one({'MaNV': name})
                # _id = str(ObjectId())
                # camera_data = {
                #     '_id': _id,
                #     'EmployeeID': "",
                #     'EmployeeCode': "",
                #     'EmployeeName': "",
                #     'OrganizationUnitID': "",
                #     'OrganizationUnitName': "",
                #     'CheckTime': "",
                #     'TimeKeeperID': "",
                #     'TimeKeeperName': "",
                #     'TenantID':"",
                #     "ModifiedDate":"",
                #     "ModifiedBy":"",
                #     "CreateDate":"",
                #     "CreateBy":"",
                #     "JobPositionID":"",
                #     "JobPositionName":"",
                #     "WorkAddress":"",
                #     "TimeKeeperDataCode":""
                # }
                # try:
                #     database.db.camera_data.insert_one(camera_data)
                #     notif = notification(content=claims['full_name']+" đã thêm camera " + name + " thành công", user_id=user_curr_id, type=CREATE)
                #     client.db.history.insert_one(notif)
                # except Exception as ex:
                #     print(ex)

                client_sub.publish(topic=cf.UPDATE_BOXES_TOPIC, payload=detection_payload)
                logging.info("[D-{}] Publish new detection.".format(now))                
    elif flag_dict == "TRAINING":
        call+=1
        if call==1:
            local_image = [None,None,None,None,None]
            client_sub.publish(topic=cf.UPDATE_TRAINING)
            set_key(r,"TEST")
    elif flag_dict:
        if None in local_image:
            stack_dict = load_stack_from_redis(r, cf.NEW_STACK_REDIS_KEY)
            if stack_dict:
                name_folder = flag_dict
                str_date = datetime.now().strftime("%Y_%m_%d") 
                path_save = "/home/ducdv10/Downloads/do_an_end/backend/app/template/image/training/{}/{}".format(str_date,name_folder)
                if not os.path.isdir(path_save):
                    os.makedirs(path_save)
                    
                result = stack_dict["stack"]
                # Predict on stacked image
                # TODO: swap labels: 0:personal, 1:unknown
                image = result[2,:,:,:]
                bbs, points = detect_face(image)
                for bb, point in zip(bbs, points):
                    (l,t,r1,b)=bb
                    local = angle_score(points.tolist())
                    PATH_IMAGE_CAMERA_SEVER = "http://localhost:4321/image/training"
                    if local[0] == 'CENTER' and not local_image[0] :
                        cv2.rectangle(image,(l, t), (r1, b), (255, 0, 0), 2)
                        cv2.putText(image,"CENTER",(l-6*(len("CENTER")-4),t-10), font, 0.8,(0,255,0),2)

                        cv2.imwrite(path_save+"/{}_{}.jpg".format("center",t),image)
                        path_server = os.path.join(PATH_IMAGE_CAMERA_SEVER+"/{}/{}".format(str_date,name_folder), "{}_{}.jpg".format("center",t))
                        detection_payload = json.dumps({"img_path": path_server})
                        client_sub.publish(topic=cf.UPDATE_BOXES_TOPIC, payload=detection_payload)
                        local_image[0] = True

                    if local[0] == 'LEFT' and not local_image[1]:
                        cv2.rectangle(image,(l, t), (r1, b), (255, 0, 0), 2)
                        cv2.putText(image,"LEFT",(l-6*(len("LEFT")-4),t-10), font, 0.8,(0,255,0),2)

                        cv2.imwrite(path_save+"/{}_{}.jpg".format("left",t),image)
                        path_server = os.path.join(PATH_IMAGE_CAMERA_SEVER+"/{}/{}".format(str_date,name_folder), "{}_{}.jpg".format("left",t))
                        detection_payload = json.dumps({"img_path": path_server})
                        client_sub.publish(topic=cf.UPDATE_BOXES_TOPIC, payload=detection_payload)

                        local_image[1] = True
                    
                    if local[0] == 'RIGHT' and not local_image[2]:
                        cv2.rectangle(image,(l, t), (r1, b), (255, 0, 0), 2)
                        cv2.putText(image,"RIGHT",(l-6*(len("RIGHT")-4),t-10), font, 0.8,(0,255,0),2)

                        cv2.imwrite(path_save+"/{}_{}.jpg".format("right",t),image)
                        path_server = os.path.join(PATH_IMAGE_CAMERA_SEVER+"/{}/{}".format(str_date,name_folder), "{}_{}.jpg".format("right",t))
                        detection_payload = json.dumps({"img_path": path_server})
                        client_sub.publish(topic=cf.UPDATE_BOXES_TOPIC, payload=detection_payload)

                        local_image[2] = True
                    
                    if local[0] == 'BOTTOM' and not local_image[3]:
                        cv2.rectangle(image,(l, t), (r1, b), (255, 0, 0), 2)
                        cv2.putText(image,"BOTTOM",(l-6*(len("BOTTOM")-4),t-10), font, 0.8,(0,255,0),2)

                        cv2.imwrite(path_save+"/{}_{}.jpg".format("bottom",t),image)
                        path_server = os.path.join(PATH_IMAGE_CAMERA_SEVER+"/{}/{}".format(str_date,name_folder), "{}_{}.jpg".format("bottom",t))
                        detection_payload = json.dumps({"img_path": path_server})
                        client_sub.publish(topic=cf.UPDATE_BOXES_TOPIC, payload=detection_payload)

                        local_image[3] = True

                    if local[0] == 'UP' and not local_image[4]:
                        cv2.rectangle(image,(l, t), (r1, b), (255, 0, 0), 2)
                        cv2.putText(image,"UP",(l-6*(len("UP")-4),t-10), font, 0.8,(0,255,0),2)

                        cv2.imwrite(path_save+"/{}_{}.jpg".format("up",t),image)
                        path_server = os.path.join(PATH_IMAGE_CAMERA_SEVER+"/{}/{}".format(str_date,name_folder), "{}_{}.jpg".format("up",t))
                        detection_payload = json.dumps({"img_path": path_server})
                        client_sub.publish(topic=cf.UPDATE_BOXES_TOPIC, payload=detection_payload)

                        local_image[4] = True       

def load_model(client, user, message):
    svm_file='models/face_model.pkl'
    global svm 
    svm = pickle.load(open(svm_file, 'rb'))
    name_file='models/name_model.pkl'
    global name_model 
    name_model = pickle.load(open(name_file, 'rb'))
    print("done")
    


client_sub = mqtt.Client("model_handler")
client_sub.connect(host=cf.BROKER_HOST, port=cf.BROKER_PORT)
client_sub.subscribe(cf.UPDATE_STACK_TOPIC, qos=0)
client_sub.message_callback_add(cf.UPDATE_STACK_TOPIC, backend_to_model_stack_frame)

client_sub.subscribe(cf.UPDATE_MODEL, qos=0)
client_sub.message_callback_add(cf.UPDATE_MODEL, load_model)
client_sub.loop_forever()

