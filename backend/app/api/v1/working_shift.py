from flask import Blueprint, json, request
from app.enums import CREATE,UPDATE,DELETE
from app.utils import send_result, send_error, notification
from app.extensions import client
from bson import ObjectId
from datetime import datetime,timedelta
import os
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('working_shift', __name__)


@api.route('/create', methods=['POST'])
@jwt_required
def post():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        WorkingShiftCode = json_data.get('WorkingShiftCode').upper()
        WorkingShiftName = json_data.get('WorkingShiftName')
        StartTime = json_data.get('StartTime', None)
        EndTime = json_data.get('EndTime', None)
        CheckStartTime = json_data.get('CheckStartTime', None)
        CheckEndTime = json_data.get('CheckEndTime', None)
        StartTimeInFrom = json_data.get('StartTimeInFrom', None)
        StartTimeInTo = json_data.get('StartTimeInTo', None)
        EndTimeInFrom = json_data.get('EndTimeInFrom')
        EndTimeInTo = json_data.get('EndTimeInTo', None)
        WorkingHour = json_data.get('WorkingHour', None)
        WorkingDate = json_data.get('WorkingDate', None)
        WorkingRateWeekday = json_data.get('WorkingRateWeekday', None),
        WorkingRateWeekend = json_data.get('WorkingRateWeekend', None),
        WorkingRateHoliday = json_data.get('WorkingRateHoliday', None),
        IsShowWithoutCheckin = json_data.get('IsShowWithoutCheckin', None)
        WorkingHourWithoutCheckin = json_data.get('WorkingHourWithoutCheckin', None)
        WorkingDayWithoutCheckin = json_data.get('WorkingDayWithoutCheckin', None)
        IsShowWithoutCheckOut = json_data.get('IsShowWithoutCheckOut', None)
        WorkingHourWithoutCheckOut = json_data.get('WorkingHourWithoutCheckOut', None)
        WorkingDayWithoutCheckOut = json_data.get('WorkingDayWithoutCheckOut', None)

    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    _id = str(ObjectId())
    working_shift = {
        '_id': _id,
        'WorkingShiftCode': WorkingShiftCode,
        'WorkingShiftName': WorkingShiftName,
        'StartTime': StartTime,
        'EndTime': EndTime,
        'CheckStartTime': CheckStartTime,
        'CheckEndTime': CheckEndTime,
        'StartTimeInFrom': StartTimeInFrom,
        'StartTimeInTo': StartTimeInTo,
        'EndTimeInFrom': EndTimeInFrom,
        'EndTimeInTo': EndTimeInTo,
        'WorkingHour':WorkingHour,
        'WorkingDate':WorkingDate,
        'WorkingRateWeekday':float(WorkingRateWeekday[0]),
        'WorkingRateWeekend':float(WorkingRateWeekend[0]),
        'WorkingRateHoliday':float(WorkingRateHoliday[0]),
        'IsShowWithoutCheckin': IsShowWithoutCheckin,
        'WorkingHourWithoutCheckin': WorkingHourWithoutCheckin,
        'WorkingDayWithoutCheckin':WorkingDayWithoutCheckin,
        'IsShowWithoutCheckOut':IsShowWithoutCheckOut,
        'WorkingHourWithoutCheckOut':WorkingHourWithoutCheckOut,
        'WorkingDayWithoutCheckOut':WorkingDayWithoutCheckOut,
        'CreateDate':datetime.now(),
        'CreateBy':claims['full_name']
    }
    try:
        client.db.working_shift.insert_one(working_shift)
        notif = notification(content=claims['full_name']+" đã thêm ca lam viec " + WorkingShiftName + " thành công", user_id=user_curr_id, type=CREATE)
        client.db.history.insert_one(notif)
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ xảy ra')
    print(working_shift)
    return send_result(message="Tạo user thành công ", data=working_shift)


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
        WorkingShift_id = json_data.get('_id', None)
        WorkingShiftCode = json_data.get('WorkingShiftCode').upper()
        WorkingShiftName = json_data.get('WorkingShiftName')
        StartTime = json_data.get('StartTime', None)
        EndTime = json_data.get('EndTime', None)
        CheckStartTime = json_data.get('CheckStartTime', None)
        CheckEndTime = json_data.get('CheckEndTime', None)
        StartTimeInFrom = json_data.get('StartTimeInFrom', None)
        StartTimeInTo = json_data.get('StartTimeInTo', None)
        EndTimeInFrom = json_data.get('EndTimeInFrom')
        EndTimeInTo = json_data.get('EndTimeInTo', None)
        WorkingHour = json_data.get('WorkingHour', None)
        WorkingDate = json_data.get('WorkingDate', None)
        WorkingRateWeekday = json_data.get('WorkingRateWeekday', None),
        WorkingRateWeekend = json_data.get('WorkingRateWeekend', None),
        WorkingRateHoliday = json_data.get('WorkingRateHoliday', None),
        IsShowWithoutCheckin = json_data.get('IsShowWithoutCheckin', None)
        WorkingHourWithoutCheckin = json_data.get('WorkingHourWithoutCheckin', None)
        WorkingDayWithoutCheckin = json_data.get('WorkingDayWithoutCheckin', None)
        IsShowWithoutCheckOut = json_data.get('IsShowWithoutCheckOut', None)
        WorkingHourWithoutCheckOut = json_data.get('WorkingHourWithoutCheckOut', None)
        WorkingDayWithoutCheckOut = json_data.get('WorkingDayWithoutCheckOut', None)

    except Exception as e:
        print(e)
        return send_error(message='Lỗi dữ liệu đầu vào')

    working_shift = client.db.working_shift.find_one({'_id': WorkingShift_id})
    if working_shift is None:
        return send_error(message='Không tìm thay ca lam viec.')
    new_working_shift = {
        '$set': {
        'WorkingShiftCode': WorkingShiftCode,
        'WorkingShiftName': WorkingShiftName,
        'StartTime': StartTime,
        'EndTime': EndTime,
        'CheckStartTime': CheckStartTime,
        'CheckEndTime': CheckEndTime,
        'StartTimeInFrom': StartTimeInFrom,
        'StartTimeInTo': StartTimeInTo,
        'EndTimeInFrom': EndTimeInFrom,
        'EndTimeInTo': EndTimeInTo,
        'WorkingHour':WorkingHour,
        'WorkingDate':WorkingDate,
        'WorkingRateWeekday':float(WorkingRateWeekday[0]),
        'WorkingRateWeekend':float(WorkingRateWeekend[0]),
        'WorkingRateHoliday':float(WorkingRateHoliday[0]),
        'IsShowWithoutCheckin': IsShowWithoutCheckin,
        'WorkingHourWithoutCheckin': WorkingHourWithoutCheckin,
        'WorkingDayWithoutCheckin':WorkingDayWithoutCheckin,
        'IsShowWithoutCheckOut':IsShowWithoutCheckOut,
        'WorkingHourWithoutCheckOut':WorkingHourWithoutCheckOut,
        'WorkingDayWithoutCheckOut':WorkingDayWithoutCheckOut
        }}
    try:
        client.db.working_shift.update_one({'_id': WorkingShift_id}, new_working_shift)
        notif = notification(content=claims['full_name']+" đã sửa ca lam viec " + WorkingShiftName + " thành công", user_id=user_curr_id, type=UPDATE)
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
    working_shift_id = json_data['_id']
    working_shift = client.db.working_shift.find_one({'_id': working_shift_id})
    if working_shift is None:
        return send_error(message="Không tìm thấy dự liệu đầu vào trong cơ sở dữ liệu")
    try:
        client.db.working_shift.delete_one({'_id': working_shift_id})
        notif = notification(content=claims['full_name']+" đã xóa ca lam " + working_shift['WorkingShiftName'] + " thành công", user_id=user_curr_id,type=DELETE)
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
    working_shifts = client.db.working_shift.find(query_filter)
        
    totals = working_shifts.count()
    if skips:
        working_shifts = working_shifts.skip(skips).limit(int(page_size))
    '''end list'''
    list_working_shift = list(working_shifts)
    '''Make a request'''
    data = {
        'totals': totals,
        'results': list_working_shift
    }
    return send_result(data=data)