from datetime import datetime
from flask import Blueprint, request
from app.enums import CREATE,UPDATE,DELETE,PATH_CAMERA
from app.utils import create_new_role_id, parse_req, FieldString, send_result, send_error, notification
from app.extensions import client
import os
from bson import ObjectId
from marshmallow import fields
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('role_permission', __name__)


@api.route('/create', methods=['POST'])
@jwt_required
def post():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")

    try:
        json_data = request.get_json()
        role_name = json_data.get('role_name', "")
        role_description = json_data.get('role_description', "")
        list_permission = json_data.get('list_permission', "")
        # list_users = json_data.get('list_users', "")
    except Exception as ex: 
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    
    role_id = create_new_role_id()
    for permission in list_permission:
        _id = str(ObjectId())
        role_permission = {
            '_id': _id,
            "role_id":role_id,
            "role_description":role_description,
            'role_name': role_name,
            'parent_code': permission["parent_code"],
            'parent_name': permission["parent_name"],
            'permission_code': permission["permission_code"],
            'subsystem_code': permission["subsystem_code"],
            'subsystem_name': permission["subsystem_name"],
            'create_date': datetime.now(),
            'create_by': claims['full_name'],

        }
        try:
            client.db.role_permission.insert_one(role_permission)
        except Exception as ex:
            print(ex)
            return send_error(message='có lỗi ngoại lệ xảy ra')
    # for us in list_users:
    #     _id = str(ObjectId())
    #     user_role = {
    #         '_id': _id,
    #         "role_id":role_id,
    #         "user_id":us['value']
    #     }
    #     client.db.user_role.insert_one(user_role)
    
    notif = notification(content=claims['full_name']+" đã thêm quyen " + role_name + " thành công", user_id=user_curr_id, type=CREATE)
    client.db.history.insert_one(notif)
    return send_result(message="Tạo camera thành công ", data=role_permission)


@api.route('/update', methods=['POST'])
@jwt_required
def put():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")

    try:
        json_data = request.get_json()
        role_id = json_data.get('role_id')
        role_name = json_data.get('role_name', "")
        role_description = json_data.get('role_description', "")
        list_permission = json_data.get('list_permission', "")
        crate_date = json_data.get('create_date',"")
        crate_by = json_data.get('create_by',"")
        # list_users = json_data.get('list_users', "")
    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')
    client.db.role_permission.delete_many({ "role_id" : role_id})
    # client.db.user_role.delete_many({'role_id': role_id})

    for permission in list_permission:
        _id = str(ObjectId())
        role_permission = {
            '_id': _id,
            "role_id":role_id,
            "role_description":role_description,
            'role_name': role_name,
            'parent_code': permission["parent_code"],
            'parent_name': permission["parent_name"],
            'permission_code': permission["permission_code"],
            'subsystem_code': permission["subsystem_code"],
            'subsystem_name': permission["subsystem_name"],
            'create_date': crate_date,
            'create_by': crate_by,

        }
        try:
            client.db.role_permission.insert_one(role_permission)
            
        except Exception as ex:
            print(ex)
            return send_error(message='có lỗi ngoại lệ xảy ra')
    # for us in list_users:
    #     _id = str(ObjectId())
    #     user_role = {
    #         '_id': _id,
    #         "role_id":role_id,
    #         "user_id":us['value']
    #     }
    #     client.db.user_role.insert_one(user_role)
    notif = notification(content=claims['full_name']+" đã sửa role permission " + role_name + " thành công", user_id=user_curr_id, type=UPDATE)
    client.db.history.insert_one(notif)
    return send_result(message="Cập nhật thành công")


@api.route('/delete', methods=['POST'])
@jwt_required
def delete():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    json_data = request.get_json();
    role_id = json_data.get('role_id')
    role_name = json_data.get('role_name', "")

    client.db.role_permission.delete_many({'role_id': role_id})
    # client.db.user_role.delete_many({'role_id': role_id})
    notif = notification(content=claims['full_name']+" đã xóa role permission " + role_name + " thành công", user_id=user_curr_id,type=DELETE)
    client.db.history.insert_one(notif)

    return send_result(message="Xóa thành công")


@api.route('/get_all_page_search', methods=['GET'])
@jwt_required
def get_all_page_search():
    text_search = request.args.get('text_search', '')
    page_size = request.args.get('page_size', '25')
    page_number = request.args.get('page_number', '1')
    skips = int(page_size) * (int(page_number)-1)
    '''Give list after filtering'''
    query = \
        {'$and': [
            #{'isActive': isActive},
            {'$or': [
                {'role_name': {'$regex': text_search, '$options': "$i"}},
                {'role_id': {'$regex': text_search, '$options': "$i"}},
                {'subsystem_name': {'$regex': text_search, '$options': "$i"}}
            ]}
        ]}
    role_permission = client.db.role_permission.find(query)
    totals = role_permission.count()
    role_permission =  role_permission.skip(skips).limit(int(page_size))
    '''end list'''
    list_role_permission= list(role_permission)
    '''Make a request'''
    list_roles=[]
    # list_users=[]
    added = set()
    list_permission = []
    for i in list_role_permission:
        if not i['role_id'] in added:
            list_permission=[]
            # list_users=[]
            list_permission.append({
                "subsystem_code":i['subsystem_code'],
                "subsystem_name":i['subsystem_name'],
                "permission_code":i['permission_code'],
                "parent_code":i['parent_code'],
                "parent_name":i['parent_name']
            })
            role_dict = {
                "role_id":i['role_id'],
                "role_name":i['role_name'],
                "role_description":i["role_description"],
                "create_date":i["create_date"],
                "create_by":i["create_by"]
                # "list_users":list_users
            }
            added.add(i['role_id'])
            list_roles.append(role_dict)
            
           
            
        else:
             list_permission.append({
                "subsystem_code":i['subsystem_code'],
                "subsystem_name":i['subsystem_name'],
                "permission_code":i['permission_code'],
                "parent_code":i['parent_code'],
                "parent_name":i['parent_name']
            })
        role_dict.update({"list_permission":list_permission})
        
    data = {
        'totals': totals,
        'roles':list_roles
    }

    return send_result(data=data)

@api.route('/get_all', methods=['GET'])
@jwt_required
def get_all():
    role_permission = client.db.role_permission.find()
    return send_result(data=list(role_permission))