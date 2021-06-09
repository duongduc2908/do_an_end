from datetime import datetime
from flask import Blueprint, request
from app.enums import CREATE,UPDATE,DELETE,CAMERA_ACTIVATE,PATH_CAMERA
from app.utils import FieldNumber, parse_req, FieldString, send_result, send_error, notification
from app.extensions import client
import os
from bson import ObjectId
from marshmallow import fields
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('camera', __name__)

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
        'instruction': FieldString(requirement=False),
        'link_image': FieldString(requirement=False),
        'link_stream': FieldString(requirement=False),
        'name': FieldString(requirement=False),
        'name_image': FieldString(requirement=False),
        'isActive': fields.Boolean(),
        'state': fields.Int()
    }

    try:
        json_data = parse_req(params)
        instruction = json_data.get('instruction', "")
        link_image = json_data.get('link_image', "")
        link_stream = json_data.get('link_stream', "")
        name = json_data.get('name', "")
        name_image = json_data.get('name_image', "")
    except Exception as ex: 
        print(ex)
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


@api.route('/update', methods=['POST'])
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
        'link_image_old': FieldString(),
        'name': FieldString(requirement=True),
        'link_stream': FieldString(requirement=True),
        'name_image': FieldString(requirement=True),
        'isActive': fields.Boolean(),
        'create_date': FieldString(),
        'create_by': FieldString(),
        "state":fields.Int(),
        "update_by":FieldString()
    }

    try:
        json_data = parse_req(params)
        _id = json_data.get('_id')
        instruction = json_data.get('instruction', "None")
        link_image_old = json_data.get('link_image_old', "None")
        link_image = json_data.get('link_image',)
        name = json_data.get('name')
        link_stream = json_data.get('link_stream')
        name_image = json_data.get('name_image')
        isActive = json_data.get('isActive')
    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    '''Check '''
    if link_image_old != "None":
        path_file = os.path.join(PATH_CAMERA, link_image_old.split("/")[-1])
        os.remove(path_file)
    camera = client.db.camera.find_one({'_id': _id})
    if camera is None:
        return send_error(message='Không tìm camera.')
    '''End check'''
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
    return send_result(message="Cập nhật thành công", data=client.db.camera.find_one({'_id': _id}))


"""
Function: Update user's profile - Admin right required
Input: user_id
Output: Success / Error Message
"""


@api.route('/delete', methods=['POST'])
@jwt_required
def delete():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    json_data = request.get_json();
    camera_id = json_data['_id']
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
    page_number = request.args.get('page_number', '1')
    isActive = request.args.get('isActive','')
    skips = int(page_size) * (int(page_number)-1)
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
