from datetime import datetime
from flask import Blueprint, request
from app.enums import CREATE, UPDATE, DELETE, CAMERA_ACTIVATE
from app.utils import parse_req, FieldString, send_result, send_error, notification
from app.extensions import client
from bson import ObjectId
import json
import paho.mqtt.client as mqtt
from app.config import DroneDetectionConfig as cf
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('camera_data', __name__)

"""
Function: User registration - Admin right required
Input: user_name, password, email, fullname, group_role_id
Output: Success / Error Message
"""


@api.route('/create', methods=['POST'])
@jwt_required
def post():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")

    params = {
        'instruction': FieldString(requirement=True),
        'link_image': FieldString(requirement=True),
        'link_stream': FieldString(requirement=True),
        'name': FieldString(requirement=True),
        'name_image': FieldString(requirement=True)
    }

    try:
        json_data = parse_req(params)
        instruction = json_data.get('instruction', None)
        link_image = json_data.get('link_image', None)
        link_stream = json_data.get('link_stream', None)
        name = json_data.get('name', None)
        name_image = json_data.get('name_image', None)
    except Exception:
        return send_error(message='Lỗi dữ liệu đầu vào')

    _id = str(ObjectId())
    camera = {
        '_id': _id,
        'instruction': instruction,
        'link_image': link_image,
        'name': name,
        'link_stream': link_stream,
        'name_image': name_image,
        'isActive': CAMERA_ACTIVATE,
        'create_date': datetime.now(),
        'create_by': claims['full_name'],
        'update_by':""
    }
    try:
        client.db.camera.insert_one(camera)
        notif = notification(content=claims['full_name']+" đã thêm camera " + name + " thành công", user_id=user_curr_id, type=CREATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ xảy ra')

    return send_result(message="Tạo camera thành công ", data=camera)


"""
Function: Update user's profile - Admin right required
Input: user_id
Output: Success / Error Message
"""


@api.route('/update', methods=['PUT'])
@jwt_required
def put():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")

    params = {
        '_id': FieldString(requirement=True),
        'instruction': FieldString(requirement=True),
        'link_image': FieldString(requirement=True),
        'name': FieldString(requirement=True),
        'link_stream': FieldString(requirement=True),
        'name_image': FieldString(requirement=True),
        'isActive': FieldString(requirement=True),
        'create_date': FieldString(),
        'create_by': FieldString(),
    }

    try:
        json_data = parse_req(params)
        _id = json_data.get('_id')
        instruction = json_data.get('instruction', None)
        link_image = json_data.get('link_image',)
        name = json_data.get('name')
        link_stream = json_data.get('link_stream')
        name_image = json_data.get('name_image')
        isActive = json_data.get('isActive')


    except Exception:
        return send_error(message='Lỗi dữ liệu đầu vào')

    '''Check '''
    camera = client.db.camera.find_one({'_id': _id})
    if camera is None:
        return send_error(message='Không tìm camera.')
    '''End check'''

    _id = str(ObjectId())
    new_camera = {
        '$set': {
            'instruction': instruction,
            'link_image': link_image,
            'name': name,
            'link_stream': link_stream,
            'name_image': name_image,
            'isActive': isActive,
            'create_date': camera['create_date'],
            'create_by': camera['create_by'],
            'update_by': claims['full_name']
        }}
    try:
        client.db.camera.update_one({'_id': _id}, new_camera)
        notif = notification(content=claims['full_name']+" đã sửa camera " + name + " thành công", user_id=user_curr_id, type=UPDATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ sảy ra')
    return send_result(message="Cập nhật thành công", data=new_camera)


"""
Function: Update user's profile - Admin right required
Input: user_id
Output: Success / Error Message
"""


@api.route('/delete', methods=['DELETE'])
@jwt_required
def delete():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    camera_id = request.args.get('_id')
    camera = client.db.camera.find_one({'_id': camera_id})
    if camera is None:
        return send_error(message="Không tìm thấy dự liệu đầu vào trong cơ sở dữ liệu")
    try:
        client.db.camera.delete_one({'_id': camera_id})
        notif = notification(content=claims['full_name']+" đã xóa camera " + camera['name'] + " thành công", user_id=user_curr_id,type=DELETE)
        client.db.history.insert_one(notif)
    except Exception:
        return send_error(message="Lỗi xóa không thành công")

    return send_result(message="Xóa thành công")


"""
Function: Get all page
Input: 
Output: Success / Error Message
"""


@api.route('/get_all_page_search', methods=['GET'])
@jwt_required
def get_all_page_search():
    text_search = request.args.get('text_search', '')
    page_size = request.args.get('page_size', '25')
    page_number = request.args.get('page_number', '0')
    isActive = request.args.get('isActive','')
    skips = int(page_size) * int(page_number)
    '''Give list after filtering'''
    query = \
        {'$and': [
            #{'isActive': isActive},
            {'$or': [
                {'name': {'$regex': text_search, '$options': "$i"}},
                {'name_image': {'$regex': text_search, '$options': "$i"}},
                {'create_by': {'$regex': text_search, '$options': "$i"}}
            ]}
        ]}
    camera = client.db.camera.find(query)
    totals = camera.count()
    camera = camera.skip(skips).limit(int(page_size))
    '''end list'''
    list_camera = list(camera)
    '''Make a request'''
    data = {
        'totals': totals,
        'results': list_camera
    }

    return send_result(data=data)


"""
Function: Get by_ id
Input: 
Output: Success / Error Message
"""

@api.route('/get_by_id', methods=['GET'])
@jwt_required
def get_by_id():
    camera_id = request.args.get('_id')
    camera = client.db.camera.find_one({'_id': camera_id})
    if not camera:
        return send_error(message="Không tìm thấy bản ghi")
    return send_result(camera)
