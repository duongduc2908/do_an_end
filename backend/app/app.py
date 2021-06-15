# -*- coding: utf-8 -*-
import logging
import traceback
from time import sleep, strftime, time
from typing_extensions import runtime
from flask import Flask
from pytz import HOUR
from app.api import v1 as api_v1
from app.api import stream as api_stream
from app.extensions import jwt, client, app_log_handler, socketio, load_frame_from_redis, red,scheduler
from .settings import ProdConfig
from flask import Flask, session, request
from flask_cors import CORS
from app import check_func

# from apscheduler.events import (
#     EVENT_JOB_ADDED,
#     EVENT_JOB_ERROR,
#     EVENT_JOB_EXECUTED,
#     EVENT_JOB_MISSED,
#     EVENT_JOB_REMOVED,
#     EVENT_JOB_SUBMITTED,
# )


# def job_missed(event):
#     """Job missed event."""
#     with scheduler.app.app_context():
#         print(event)  # noqa: T001


# def job_error(event):
#     """Job error event."""
#     with scheduler.app.app_context():
#         print(event)  # noqa: T001


# def job_executed(event):
#     """Job executed event."""
#     with scheduler.app.app_context():
#         print(event)  # noqa: T001


# def job_added(event):
#     """Job added event."""
#     with scheduler.app.app_context():
#         print(event)  # noqa: T001


# def job_removed(event):
#     """Job removed event."""
#     with scheduler.app.app_context():
#         print(event)  # noqa: T001


# def job_submitted(event):
#     """Job scheduled to run event."""
#     with scheduler.app.app_context():
#         print(event)  # noqa: T001


# scheduler.add_listener(job_missed, EVENT_JOB_MISSED)
# scheduler.add_listener(job_error, EVENT_JOB_ERROR)
# scheduler.add_listener(job_executed, EVENT_JOB_EXECUTED)
# scheduler.add_listener(job_added, EVENT_JOB_ADDED)
# scheduler.add_listener(job_removed, EVENT_JOB_REMOVED)
# scheduler.add_listener(job_submitted, EVENT_JOB_SUBMITTED)

users = {}

def create_app(config_object=ProdConfig, content='app'):
    """
    Init App
    :param config_object:
    :param content:
    :return:
    """
    app = Flask(__name__, static_url_path="", static_folder="./template", template_folder="./template")
    app.config.from_object(config_object)
    register_extensions(app, content, config_object)
    register_blueprints(app)
    CORS(app)
    return app


def register_extensions(app, content, config_object):
    """
    Init extension
    :param app:
    :param content:
    :return:
    """
    client.app = app
    client.init_app(app)
    scheduler.init_app(app)
    socketio.init_app(app)
    # don't start extensions if content != app
    if content == 'app':
        jwt.init_app(app)
    # logger
    logger = logging.getLogger('api')
    logger.setLevel(logging.ERROR)
    logger.addHandler(app_log_handler)

    @app.after_request
    def after_request(response):
        # This IF avoids the duplication of registry in the log,
        # since that 500 is already logged via @app.errorhandler.
        if response.status_code != 500:
            ts = strftime('[%Y-%b-%d %H:%M]')
            logger.error('%s %s %s %s %s %s',
                         ts,
                         request.remote_addr,
                         request.method,
                         request.scheme,
                         request.full_path,
                         response.status)
        return response

    @app.errorhandler(Exception)
    def exceptions(e):
        ts = strftime('[%Y-%b-%d %H:%M]')
        tb = traceback.format_exc()
        error = '{} {} {} {} {} 5xx INTERNAL SERVER ERROR\n{}'.format \
                (
                ts,
                request.remote_addr,
                request.method,
                request.scheme,
                request.full_path,
                tb
            )

        logger.error(error)

        return "Internal Server Error", 500


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    user = client.db.user.find_one({'_id': identity})
    if user['group_role_id'] == '1':
        return {'is_admin': True, 'is_phuong': False, 'is_benh_vien': False, 'full_name': user['full_name']}
    elif user['group_role_id'] == '2':
        return {'is_admin': False, 'is_phuong': True, 'is_benh_vien': False, 'full_name': user['full_name']}
    else:
        return {'is_admin': False, 'is_phuong': False, 'is_benh_vien': True, 'full_name': user['full_name']}


def register_blueprints(app):
    """
    Init blueprint for api url
    :param app:
    :return:
    """
    app.register_blueprint(api_v1.auth.api, url_prefix='/api/v1/auth')
    app.register_blueprint(api_v1.user.api, url_prefix='/api/v1/user')
    app.register_blueprint(api_v1.history.api, url_prefix='/api/v1/history')
    app.register_blueprint(api_v1.upload_file.api, url_prefix='/api/v1/file')
    app.register_blueprint(api_stream.api_camera.api, url_prefix='/api/stream/connection_api')
    app.register_blueprint(api_v1.import_json.api, url_prefix='/api/v1/import_json')
    app.register_blueprint(api_v1.camera.api, url_prefix='/api/v1/camera')
    app.register_blueprint(api_v1.camera_data.api, url_prefix='/api/v1/camera_data')
    app.register_blueprint(api_v1.subsystem_permission.api, url_prefix='/api/v1/subsystem_permission')
    app.register_blueprint(api_v1.organization_unit.api, url_prefix='/api/v1/organization_unit')
    app.register_blueprint(api_v1.job_position.api, url_prefix='/api/v1/job_position')
    app.register_blueprint(api_v1.role_permission.api, url_prefix='/api/v1/role_permission')
    app.register_blueprint(api_v1.working_shift.api, url_prefix='/api/v1/working_shift')
    app.register_blueprint(api_v1.shift_plan.api, url_prefix='/api/v1/shift_plan')
    app.register_blueprint(api_v1.shift_plan_employee.api, url_prefix='/api/v1/shift_plan_employee')


@socketio.on('connect')
def connect():
    scheduler.remove_all_jobs()
    # scheduler.add_job(func=check_func.check_shift_plan, id='apscheduler_add',trigger='cron',day=10,month=6,year=2021,hour=2, minute=9, replace_existing=True,timezone='UTC')
    # scheduler.add_job(func=check_func.check_shift_plan, id='apscheduler_add',trigger='cron',day="*",day_of_week="0-4",hour="6")
    # scheduler.add_job(func=check_func.check_shift_plan, id='apscheduler_add',trigger='interval',seconds=5)


    @socketio.on('new_frame_event')
    def send_new_frame(message):
         # global fake_detection
        # Message interface includes three keys: frame, detection, room.
        session['receive_count'] = session.get('receive_count', 0) + 1
        room = False

        detection = message['detection']
        # detection = fake_detection

        frame_key = message['frame']
        frame_dict = load_frame_from_redis(red, frame_key)
        image_data = frame_dict["frame"]

        socketio.emit('imageConversionByClient', {
            'buffer': image_data,
            'timestamp': detection['timestamp'],
            'boxes': detection['boxes'],
            'scores': detection['scores'],
            'classes': detection['classes']
        })
        logging.info("Emit new frame of timestamp {} to frontends at {}")


    @socketio.on('new_box_to_client')
    def new_box_to_client(message):

        img_path = message['img_path']
        # detection = fake_detection
        socketio.emit('imageBoxToClient', {
            'img_path': img_path
        })
        logging.info("Emit new frame of timestamp {} to frontends at {}")


    @socketio.on('disconnect')
    def disconnect():
        logging.debug('Client disconnected {}'.format(request.sid))



    

