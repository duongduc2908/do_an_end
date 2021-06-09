from flask import Blueprint, request
from app.enums import CREATE,UPDATE,DELETE
from app.utils import  send_result, send_error, notification
from app.extensions import client
from bson import ObjectId
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('organization_unit', __name__)


@api.route('/create', methods=['POST'])
@jwt_required
def post():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        OrganizationUnitCode = json_data.get('OrganizationUnitCode', "")
        OrganizationUnitName = json_data.get('OrganizationUnitName', "")
        ParentID = json_data.get('ParentID', "")
    except Exception as ex: 
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    _id = str(ObjectId())
    organization_unit = {
        '_id': _id,
        'OrganizationUnitCode': OrganizationUnitCode,
        'ParentID': ParentID,
        'OrganizationUnitName': OrganizationUnitName
    }
    try:
        client.db.organization_unit.insert_one(organization_unit)
        notif = notification(content=claims['full_name']+" đã thêm job position " + OrganizationUnitName + " thành công", user_id=user_curr_id, type=CREATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ xảy ra')

    return send_result(message="Tạo job_position thành công ", data=organization_unit)


@api.route('/update', methods=['POST'])
@jwt_required
def put():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")

    try:
        json_data = request.get_json()
        _id = json_data.get('_id')
        OrganizationUnitName = json_data.get('OrganizationUnitName', "None")
        ParentID = json_data.get('ParentID')
    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    '''Check '''
    organization_unit = client.db.organization_unit.find_one({'_id': _id})
    if organization_unit is None:
        return send_error(message='Không tìm camera.')
    '''End check'''
    new_organization_unit = {
        '$set': {
            'OrganizationUnitName': OrganizationUnitName,
            'OrganizationUnitCode': organization_unit["OrganizationUnitCode"],
            'ParentID': ParentID
        }}
    try:
        client.db.organization_unit.update_one({'_id': _id}, new_organization_unit)
        notif = notification(content=claims['full_name']+" đã sửa job_position " + OrganizationUnitName + " thành công", user_id=user_curr_id, type=UPDATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ sảy ra')
    return send_result(message="Cập nhật thành công", data=client.db.new_organization_unit.find_one({'_id': _id}))


@api.route('/delete', methods=['POST'])
@jwt_required
def delete():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    json_data = request.get_json();
    organization_unit_id = json_data['_id']
    organization_unit = client.db.organization_unit.find_one({'_id': organization_unit_id})
    if organization_unit is None:
        return send_error(message="Không tìm thấy dự liệu đầu vào trong cơ sở dữ liệu")
    try:
        client.db.organization_unit.delete_one({'_id': organization_unit_id})
        notif = notification(content=claims['full_name']+" đã xóa job position " + organization_unit['OrganizationUnitName'] + " thành công", user_id=user_curr_id,type=DELETE)
        client.db.history.insert_one(notif)
    except Exception:
        return send_error(message="Lỗi xóa không thành công")

    return send_result(message="Xóa thành công")


@api.route('/get_all_page_search', methods=['GET'])
@jwt_required
def get_all_page_search():
    text_search = request.args.get('text_search', '')
    OrganizationUnitCode = request.args.get('OrganizationUnitCode', '')
    page_size = request.args.get('page_size', '25')
    page_number = request.args.get('page_number', '1')
    skips = int(page_size) * (int(page_number)-1)
    '''Give list after filtering'''
    query = \
        {'$and': [
            #{'isActive': isActive},
            {'$or': [
                {'OrganizationUnitName': {'$regex': text_search, '$options': "$i"}},
                {'OrganizationUnitCode': {'$regex': OrganizationUnitCode, '$options': "$i"}}
            ]}
        ]}
    organization_unit = client.db.organization_unit.find(query)
    totals = organization_unit.count()
    organization_unit = organization_unit.skip(skips).limit(int(page_size))
    '''end list'''
    list_organization_unit= list(organization_unit)
    '''Make a request'''
    data = {
        'totals': totals,
        'results': list_organization_unit
    }

    return send_result(data=data)

