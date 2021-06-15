from flask import Blueprint, request
import subprocess
import os
from subprocess import Popen
from app.config import DroneDetectionConfig as cf
import time
from app.utils import send_result, send_error
from app.extensions import set_key,red
import logging
from app.extensions import client
from flask_jwt_extended import (
    jwt_required,get_jwt_claims)

logging.basicConfig(format=cf.LOGGING_FORMAT, datefmt=cf.LOGGING_DATEFMT, level=cf.LOGGING_LEVEL)

api = Blueprint('connection_api', __name__)
RUN_RTSP_DAEMON_PROCESS = None


def _run_daemon(command, env):
    global RUN_RTSP_DAEMON_PROCESS
    RUN_RTSP_DAEMON_PROCESS = Popen(command, env=env)


def _stop_rtsp_daemon():
    global RUN_RTSP_DAEMON_PROCESS
    RUN_RTSP_DAEMON_PROCESS.kill()
    time.sleep(1)
    RUN_RTSP_DAEMON_PROCESS = None


def _is_rtsp_daemon_running():
    global RUN_RTSP_DAEMON_PROCESS
    if RUN_RTSP_DAEMON_PROCESS is not None:
        return True
    else:
        return False


def _form_rtsp_link(params):
    if params["username"] == "" or params['password'] == "":
        return params["rtsp_link"]
    else:
        return "rtsp://" + params["username"] + ":" + params["password"] + "@" + \
               params["rtsp_link"][7:len(params["rtsp_link"])]


@api.route('/connect', methods=['GET'])
@jwt_required
def check_connect():
    global RUN_RTSP_DAEMON_PROCESS
    response_fail = {
        'status': False,
        'msg': "Connect to rtsp link fail"
    }
    response_true = {
        'status': True,
        'msg': "Connect to rtsp link successfully"
    }
    params = {
        "rtsp_link": request.args.get('rtsp_link'),
        "username": request.args.get('username'),
        "password": request.args.get('password'),
        "protocol_id": int(request.args.get('selectedProtocol'))
    }
    _id = request.args.get('_id')
    camera = client.db.camera.find_one({'_id': _id})
    if camera is None:
        return send_error(message='Không tìm camera.')
    claims = get_jwt_claims()
    new_camera = {
        '$set': {
            'instruction': camera["instruction"],
            'link_image': camera["link_image"],
            'name': camera["name"],
            'link_stream': camera["link_stream"],
            'name_image': camera["name_image"],
            'isActive': False,
            'create_date': camera['create_date'],
            'create_by': camera['create_by'],
            'update_by': claims['full_name']
        }}
    
    if not _is_rtsp_daemon_running():
        try:
            my_env = os.environ.copy()
            my_env['PYTHONPATH'] ="/home/ducdv10/Downloads/do_an_end/backend/"
            protocol_id = params["protocol_id"]
            if protocol_id == 1:  # RTSP/TCP
                link = _form_rtsp_link(params)
                logging.info("Connect to RTSP/TCP camera at {}".format(link))
                my_env.pop('OPENCV_FFMPEG_CAPTURE_OPTIONS', None)
                print("Load rtsp daemon")
                compeleted_process = subprocess.run(['python', 'app/api/stream/rtsp_tcp_daemon.py', '--link', link, '--mode', '1'],env=my_env         )
                if compeleted_process.returncode:
                    logging.info("FAIL to connect to RTSP/TCP camera at {}".format(link))
                    return send_error(data=response_fail ,code=400)
                client.db.camera.update_one({'_id': _id}, new_camera)
                _run_daemon(['python', 'app/api/stream/rtsp_tcp_daemon.py', '--link', link, '--mode', '0'], my_env)
            else:
                logging.info("FAIL Not supported protocol")
                return send_error(data=response_fail ,code=400)
            return send_result(data=response_true,code=200)
        except Exception as e:
            logging.exception("Neglect connection.")
            return send_error(data=response_fail ,code=400)
    logging.info("FAIL to connect because another camera connection existed, please disconnect it and retry.")
    return send_error(data=response_fail ,code=400)


@api.route('/disconnect', methods=['GET'])
@jwt_required
def disconnect():
    response_true = {
        'status': True,
        'msg': "Disconnect rtsp link successfully"
    }
    logging.info("Disconnect to camera.")
    if RUN_RTSP_DAEMON_PROCESS is not None:
        _stop_rtsp_daemon()
    _id = request.args.get('_id')
    camera = client.db.camera.find_one({'_id': _id})
    if camera is None:
        return send_error(message='Không tìm camera.')
    claims = get_jwt_claims()
    new_camera = {
        '$set': {
            'instruction': camera["instruction"],
            'link_image': camera["link_image"],
            'name': camera["name"],
            'link_stream': camera["link_stream"],
            'name_image': camera["name_image"],
            'isActive':True,
            'create_date': camera['create_date'],
            'create_by': camera['create_by'],
            'update_by': claims['full_name']
        }}
    client.db.camera.update_one({'_id': _id}, new_camera)
    return send_result(data=response_true,code=200)


@api.route('/begin_train',methods=['GET'])
def begin_train():
    MaNV = request.args.get('MaNV')
    set_key(red,MaNV)
    response_true = {
        'status': True,
        'msg': "Disconnect rtsp link successfully"
    }
    return send_result(data=response_true,code=200)

@api.route('/changeFlag',methods=['GET'])
def changeFlag():
    set_key(red,"TEST")
    response_true = {
        'status': True,
        'msg': "Disconnect rtsp link successfully"
    }
    return send_result(data=response_true,code=200)


@api.route('/train',methods=['POST'])
def train_new():
    # try:2
        import json
        set_key(red,"TRAINING")
        # client_sub = mqtt.Client("model_handler")
        # client_sub.connect(host=cf.BROKER_HOST, port=cf.BROKER_PORT)
        # client_sub.subscribe(cf.UPDATE_TRAINING, qos=0)
        # client_sub.publish(topic=cf.UPDATE_TRAINING)
        response_true = {
            'status': True,
            'msg': "Disconnect rtsp link successfully"
        }
        
        return send_result(data=response_true,code=200)
    # except:
    #     # print(except)
    #     return send_error(code=404)
