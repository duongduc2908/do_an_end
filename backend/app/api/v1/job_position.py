from flask import Blueprint, request
from app.enums import CREATE,UPDATE,DELETE
from app.utils import  send_result, send_error, notification
from app.extensions import client
from bson import ObjectId
import json
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('job_position', __name__)


@api.route('/create', methods=['POST'])
@jwt_required
def post():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        JobPositionName = json_data.get('JobPositionName', "")
        JobPositionCode = json_data.get('JobPositionCode', "")
        OrganizationUnitID = json_data.get('OrganizationUnitID', "")
    except Exception as ex: 
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    _id = str(ObjectId())
    OrganizationUnitName=[]
    for og in OrganizationUnitID:
        og_name = client.db.organization_unit.find_one({"_id":og})
        OrganizationUnitName.append(og_name["OrganizationUnitName"])
    job_position = {
        '_id': _id,
        'JobPositionName': JobPositionName,
        'JobPositionCode': JobPositionCode,
        'OrganizationUnitID': OrganizationUnitID,
        'OrganizationUnitName': OrganizationUnitName
    }
    try:
        client.db.job_position.insert_one(job_position)
        notif = notification(content=claims['full_name']+" đã thêm job position " + JobPositionName + " thành công", user_id=user_curr_id, type=CREATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ xảy ra')

    return send_result(message="Tạo job_position thành công ", data=job_position)


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
        JobPositionName = json_data.get('JobPositionName', "None")
        JobPositionCode = json_data.get('JobPositionCode', "None")
        OrganizationUnitID = json_data.get('OrganizationUnitID',)
    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    '''Check '''
    job_position = client.db.job_position.find_one({'_id': _id})
    if job_position is None:
        return send_error(message='Không tìm camera.')
    '''End check'''
    OrganizationUnitName=[]
    for og in OrganizationUnitID:
        og_name = client.db.organization_unit.find_one({"_id":og})
        OrganizationUnitName.append(og_name["OrganizationUnitName"])
    new_job_position = {
        '$set': {
            'JobPositionName': JobPositionName,
            'JobPositionCode': JobPositionCode,
            'OrganizationUnitID': OrganizationUnitID,
            'OrganizationUnitName': OrganizationUnitName
        }}
    try:
        client.db.job_position.update_one({'_id': _id}, new_job_position)
        notif = notification(content=claims['full_name']+" đã sửa job_position " + JobPositionName + " thành công", user_id=user_curr_id, type=UPDATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ sảy ra')
    return send_result(message="Cập nhật thành công", data=client.db.job_position.find_one({'_id': _id}))


@api.route('/delete', methods=['POST'])
@jwt_required
def delete():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    json_data = request.get_json();
    job_pos_id = json_data['_id']
    job_position = client.db.job_position.find_one({'_id': job_pos_id})
    if job_position is None:
        return send_error(message="Không tìm thấy dự liệu đầu vào trong cơ sở dữ liệu")
    try:
        client.db.job_position.delete_one({'_id': job_pos_id})
        notif = notification(content=claims['full_name']+" đã xóa job position " + job_position['JobPositionName'] + " thành công", user_id=user_curr_id,type=DELETE)
        client.db.history.insert_one(notif)
    except Exception:
        return send_error(message="Lỗi xóa không thành công")

    return send_result(message="Xóa thành công")


@api.route('/get_all_page_search', methods=['GET'])
@jwt_required
def get_all_page_search():
    query_filter = json.loads(request.args.get('query_filter', '{}'))
    page_size = request.args.get('page_size', '25')
    page_number = request.args.get('page_number', '1')
    skips = int(page_size) * (int(page_number)-1)
    print(query_filter)
    if len(query_filter["$and"])==0:
        query_filter={}
    job_position = client.db.job_position.find(query_filter)
    totals = job_position.count()
    job_position = job_position.skip(skips).limit(int(page_size))
    '''end list'''
    list_job_position= list(job_position)
    '''Make a request'''
    data = {
        'totals': totals,
        'results': list_job_position
    }

    return send_result(data=data)


@api.route('/get_by_og', methods=['GET'])
@jwt_required
def get_by_og():
    OrganizationUnitID = request.args.get('OrganizationUnitID', '')
    list_position = list(client.db.job_position.find({},{"_id":1,"JobPositionName":1,"OrganizationUnitID":1}))
    list_results=[]
    for po in list_position:
        if OrganizationUnitID in po["OrganizationUnitID"]:
            list_results.append({
            "key":po["_id"],
            "display_name":po["JobPositionName"]
        })
    return send_result(data=list_results)