from flask import Blueprint, json, request
from app.enums import USER_ACTIVATED, USER_DEACTIVATED, STATUS_USER,CREATE,UPDATE,DELETE,PATH_IMAGE_AVATAR
from app.utils import check_email, check_phone_number, send_result, send_error, hash_password, set_auto_MaNV, notification
from app.extensions import client
from bson import ObjectId
from datetime import datetime,timedelta
import os
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('user', __name__)

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
    try:
        json_data = request.get_json()
        user_name = json_data.get('user_name').lower()
        full_name = json_data.get('full_name')
        email = json_data.get('email', None)
        OrganizationUnitID = json_data.get('OrganizationUnitID', None)
        OrganizationUnitName = json_data.get('OrganizationUnitName', None)
        JobPositionID = json_data.get('JobPositionID', None)
        JobPositionName = json_data.get('JobPositionName', None)
        HireDate = json_data.get('HireDate', None)
        ReceiveDate = json_data.get('ReceiveDate', None)
        Mobile = json_data.get('Mobile')
        NumberOfLeaveDay = json_data.get('NumberOfLeaveDay', None)
        Avatar = json_data.get('Avatar', None)
        Gender = json_data.get('Gender', None)
        BirthDay = json_data.get('BirthDay', None)
        Address = json_data.get('Address', None)
        group_role_id = json_data.get('group_role_id', None)
        IsTrain = json_data.get('IsTrain', None)
        list_roles = json_data.get('list_roles', None)
        password = "123456a@"

    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    '''check'''
    if email:
        check_email(email)
    if Mobile:
        check_phone_number(Mobile)

    '''end check'''

    _id = str(ObjectId())
    user = {
        '_id': _id,
        'full_name': full_name,
        'user_name': user_name,
        'MaNV': set_auto_MaNV(),
        'password': hash_password(password),
        'email': email,
        'OrganizationUnitID': OrganizationUnitID,
        'OrganizationUnitName': OrganizationUnitName,
        'JobPositionID': JobPositionID,
        'JobPositionName': JobPositionName,
        'HireDate': HireDate,
        'ReceiveDate': ReceiveDate,
        'Mobile': Mobile,
        'NumberOfLeaveDay': NumberOfLeaveDay,
        'Avatar': Avatar,
        'Gender': Gender,
        'BirthDay': BirthDay,
        'Address': Address,
        'CreateDate': datetime.now(),
        'CreateBy': claims['full_name'],
        'ModifiedDate': '',
        'ModifiedBy':'',
        'status':1,
        'group_role_id':group_role_id,
        'IsTrain': IsTrain
    }
    try:
        client.db.user.insert_one(user)
        notif = notification(content=claims['full_name']+" đã thêm nhân viên " + full_name + " thành công", user_id=user_curr_id, type=CREATE)
        client.db.history.insert_one(notif)
        if list_roles:
            for role in list_roles:
                user_role_id = str(ObjectId())
                user_role = {
                    '_id': user_role_id,
                    'user_id': _id,
                    'role_id': role,
                }
                client.db.user_role.insert_one(user_role)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ xảy ra')

    return send_result(message="Tạo user thành công ", data=user)


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
    try:
        json_data = request.get_json()
        user_id = json_data.get('_id', None)
        user_name = json_data.get('user_name', None).lower()
        full_name = json_data.get('full_name', None)
        email = json_data.get('email', None)
        OrganizationUnitID = json_data.get('OrganizationUnitID', None)
        OrganizationUnitName = json_data.get('OrganizationUnitName', None)
        JobPositionID = json_data.get('JobPositionID', None)
        JobPositionName = json_data.get('JobPositionName', None)
        HireDate = json_data.get('HireDate', None)
        ReceiveDate = json_data.get('ReceiveDate', None)
        Mobile = json_data.get('Mobile', None)
        NumberOfLeaveDay = json_data.get('NumberOfLeaveDay', None)
        Avatar = json_data.get('Avatar', None)
        Gender = json_data.get('Gender', None)
        BirthDay = json_data.get('BirthDay', None)
        Address = json_data.get('Address', None)
        group_role_id = json_data.get('group_role_id', None)
        ModifiedDate = datetime.now()
        ModifiedBy = claims['full_name']
        status = json_data.get('status', 1)
        link_Avatar_old = json_data.get('link_Avatar_old', "None")
        IsTrain = json_data.get('IsTrain', None)
        list_roles = json_data.get('list_roles', None)
    except Exception as e:
        print(e)
        return send_error(message='Lỗi dữ liệu đầu vào')

    user = client.db.user.find_one({'_id': user_id})
    if user is None:
        return send_error(message='Không tìm thấy người dùng.')
    if link_Avatar_old != "None" and link_Avatar_old != None:
        path_file = os.path.join(PATH_IMAGE_AVATAR, link_Avatar_old.split("/")[-1])
        os.remove(path_file)
    new_user = {
        '$set': {
            'full_name': full_name,
            'user_name': user_name,
            'MaNV': user['MaNV'],
            'password': user['password'],
            'email': email,
            'OrganizationUnitID': OrganizationUnitID,
            'OrganizationUnitName': OrganizationUnitName,
            'JobPositionName': JobPositionID,
            'JobPositionName': JobPositionName,
            'HireDate': HireDate,
            'ReceiveDate': ReceiveDate,
            'Mobile': Mobile,
            'NumberOfLeaveDay': NumberOfLeaveDay,
            'Avatar': Avatar,
            'Gender': Gender,
            'BirthDay': BirthDay,
            'Address': Address,
            'CreateDate': user['CreateDate'],
            'CreateBy': user['CreateBy'],
            'ModifiedDate': ModifiedDate,
            'ModifiedBy':ModifiedBy,
            'status':status,
            'group_role_id':group_role_id,
            'IsTrain':IsTrain
        }}
    try:
        client.db.user.update_one({'_id': user_id}, new_user)
        client.db.user_role.delete_many({'user_id': user_id})
        if list_roles:
            for role in list_roles:
                user_role_id = str(ObjectId())
                user_role = {
                    '_id': user_role_id,
                    'user_id': user_id,
                    'role_id': role,
                }
                client.db.user_role.insert_one(user_role)
        notif = notification(content=claims['full_name']+" đã sửa nhân viên " + full_name + " thành công", user_id=user_curr_id, type=UPDATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ sảy ra')
    return send_result(message="Cập nhật thành công", data=client.db.user.find_one({'_id':user_id}))


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
    user_id = json_data['_id']
    user = client.db.user.find_one({'_id': user_id})
    if user is None:
        return send_error(message="Không tìm thấy dự liệu đầu vào trong cơ sở dữ liệu")
    try:
        client.db.user.delete_one({'_id': user_id})
        if user['Avatar'] != "None" and user['Avatar'] != None and user['Avatar'] != '':
            path_file = os.path.join(PATH_IMAGE_AVATAR, user['Avatar'].split("/")[-1])
            os.remove(path_file)

        client.db.user_role.delete_many({'user_id':user_id})
        notif = notification(content=claims['full_name']+" đã xóa nhân viên " + user['full_name'] + " thành công", user_id=user_curr_id,type=DELETE)
        client.db.history.insert_one(notif)
    except Exception as e:
        print(e)
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
    page_size = request.args.get('page_size', None)
    page_number = request.args.get('page_number', None)
    query_filter = request.args.get('query_filter', '{"$and":[]}')
    if page_size and page_number:
        skips = int(page_size) * (int(page_number)-1)
    else:
        skips = None
    start_date = request.args.get('start_date')
    to_date = request.args.get('to_date')
    '''Give list after filtering'''
    
    query_filter = json.loads(query_filter)
    if start_date and to_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
        to_date = to_date + timedelta(days=1)
        query_filter['$and'].append({ 'CreateDate': {"$lte": to_date , "$gte": start_date } })
    if len(query_filter["$and"])==0:
        query_filter={}
    print(query_filter)
    users = client.db.user.find(query_filter)
        
    totals = users.count()
    if skips:
        users = users.skip(skips).limit(int(page_size))
    '''end list'''
    list_user = list(users)
    '''Make a request'''

    for i in list_user:
        list_roles = client.db.user_role.find({"user_id":i["_id"]})
        list_res = []
        if list_roles:
            for role in list(list_roles):
                list_res.append(role["role_id"])
            i['list_roles'] = list_res
        else:
            i['list_roles'] = ""
        if int(i['status']) == USER_ACTIVATED:
            i['status_name'] = STATUS_USER[USER_ACTIVATED]
        if int(i['status']) == USER_DEACTIVATED:
            i['status_name'] = STATUS_USER[USER_DEACTIVATED]
    '''end request'''
    data = {
        'totals': totals,
        'results': list_user
    }
    return send_result(data=data)


@api.route('/get_info', methods=['GET'])
@jwt_required
def get_info():
    user_curr_id = get_jwt_identity()
    users = client.db.user.find_one({'_id': user_curr_id})
    if not users:
        return send_error(message="Không tìm thấy bản ghi")
    if users['group_role_id'] == '1':
        role = 'admin'
    else:
        role = 'editor'
    list_roles = list(client.db.user_role.find({'user_id': user_curr_id}))
    if len(list_roles):
        for roles in list_roles:
            role_permissions = list(client.db.role_permission.find({'role_id': roles['role_id']}))
            data = {
                'results': users,
                "role": [role],
                'role_permissions':role_permissions
            }
    return send_result(data)
