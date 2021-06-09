from flask import Blueprint, json, request
from app.enums import CREATE,UPDATE,DELETE
from app.utils import send_result, send_error,notification
from app.extensions import client
from bson import ObjectId
from datetime import datetime,timedelta
import os
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('shift_plan', __name__)


@api.route('/create', methods=['POST'])
@jwt_required
def post():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        ShiftPlanName = json_data.get('ShiftPlanName').lower()
        WorkingShiftIDs = json_data.get('WorkingShiftIDs')
        WorkingShiftNames = json_data.get('WorkingShiftNames', None)
        DateApplyType = json_data.get('DateApplyType', None)
        FromDate = json_data.get('FromDate', None)
        ToDate = json_data.get('ToDate', None)
        RepeatType = json_data.get('RepeatType', None)
        RepeatConfig = json_data.get('RepeatConfig', None)
        ObjectType = json_data.get('ObjectType')
        OrganizationUnitIDs = json_data.get('OrganizationUnitIDs', None)
        OrganizationUnitName = json_data.get('OrganizationUnitName', None)
        user_id = json_data.get('user_id', None)
        user_fullname = json_data.get('user_fullname', None)

    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    _id = str(ObjectId())
    shift_plan = {
        '_id': _id,
        'ShiftPlanName': ShiftPlanName,
        'WorkingShiftIDs': WorkingShiftIDs,
        'WorkingShiftNames': WorkingShiftNames,
        'DateApplyType': DateApplyType,
        'FromDate': FromDate,
        'ToDate': ToDate,
        'RepeatType': RepeatType,
        'RepeatConfig': RepeatConfig,
        'ObjectType': ObjectType,
        'OrganizationUnitIDs': OrganizationUnitIDs,
        'OrganizationUnitName': OrganizationUnitName,
        'user_id': user_id,
        'user_fullname': user_fullname,
        'ModifiedDate': "",
        'ModifiedBy':'',
        'CreateDate': datetime.today(),
        'CreateBy': claims['full_name']
    }
    try:
        client.db.shift_plan.insert_one(shift_plan)
        notif = notification(content=claims['full_name']+" đã thêm ca lam viec " + WorkingShiftNames + " thành công", user_id=user_curr_id, type=CREATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ xảy ra')

    return send_result(message="Tạo user thành công ")


@api.route('/update', methods=['POST'])
@jwt_required
def put():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        Shift_plan_id = json_data.get('_id', None)
        ShiftPlanName = json_data.get('ShiftPlanName').lower()
        WorkingShiftIDs = json_data.get('WorkingShiftIDs')
        WorkingShiftNames = json_data.get('WorkingShiftNames', None)
        DateApplyType = json_data.get('DateApplyType', None)
        FromDate = json_data.get('FromDate', None)
        ToDate = json_data.get('ToDate', None)
        RepeatType = json_data.get('RepeatType', None)
        RepeatConfig = json_data.get('RepeatConfig', None)
        ObjectType = json_data.get('ObjectType')
        OrganizationUnitIDs = json_data.get('OrganizationUnitIDs', None)
        OrganizationUnitName = json_data.get('OrganizationUnitName', None)
        user_id = json_data.get('user_id', None)
        user_fullname = json_data.get('user_fullname', None)
        CreateDate = json_data.get('CreateDate', None)
        CreateBy = json_data.get('CreateBy', None)

    except Exception as e:
        print(e)
        return send_error(message='Lỗi dữ liệu đầu vào')

    shift_plan = client.db.shift_plan.find_one({'_id': Shift_plan_id})
    if shift_plan is None:
        return send_error(message='Không tìm thay ca lam viec.')
    new_shift_plan = {
        '$set': {
            'ShiftPlanName': ShiftPlanName,
            'WorkingShiftIDs': WorkingShiftIDs,
            'WorkingShiftNames': WorkingShiftNames,
            'DateApplyType': DateApplyType,
            'FromDate': FromDate,
            'ToDate': ToDate,
            'RepeatType': RepeatType,
            'RepeatConfig': RepeatConfig,
            'ObjectType': ObjectType,
            'OrganizationUnitIDs': OrganizationUnitIDs,
            'OrganizationUnitName': OrganizationUnitName,
            'user_id': user_id,
            'user_fullname': user_fullname,
            'CreateDate': CreateDate,
            'CreateBy': CreateBy,
            'ModifiedDate': datetime.today(),
            'ModifiedBy': claims['full_name']
        }}
    try:
        client.db.shift_plan.update_one({'_id': Shift_plan_id}, new_shift_plan)
        notif = notification(content=claims['full_name']+" đã sửa ca lam viec " + ShiftPlanName + " thành công", user_id=user_curr_id, type=UPDATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ sảy ra')
    return send_result(message="Cập nhật thành công")


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
    shift_plan_id = json_data['_id']
    shift_plan = client.db.shift_plan.find_one({'_id': shift_plan_id})
    if shift_plan is None:
        return send_error(message="Không tìm thấy dự liệu đầu vào trong cơ sở dữ liệu")
    try:
        client.db.shift_plan.delete_one({'_id': shift_plan_id})
        notif = notification(content=claims['full_name']+" đã xóa ca lam " + shift_plan['ShiftPlanName'] + " thành công", user_id=user_curr_id,type=DELETE)
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
    page_size = request.args.get('page_size', None)
    page_number = request.args.get('page_number', None)
    query_filter = request.args.get('query_filter', '')
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
    shift_plans = client.db.shift_plan.find(query_filter)
        
    totals = shift_plans.count()
    if skips:
        shift_plan = shift_plans.skip(skips).limit(int(page_size))
    '''end list'''
    list_shift_plan = list(shift_plan)
    '''Make a request'''
    data = {
        'totals': totals,
        'results': list_shift_plan
    }
    return send_result(data=data)