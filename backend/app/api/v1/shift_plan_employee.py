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

api = Blueprint('shift_plan_employee', __name__)


@api.route('/create', methods=['POST'])
@jwt_required
def post():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        ShiftPlanDay = json_data.get('ShiftPlanDay')
        WorkingShiftIDs = json_data.get('WorkingShiftIDs',None)
        WorkingShiftNames = json_data.get('WorkingShiftNames', None)
        users = json_data.get('users',None)
    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')
    list_working_shift = []
    for i in range(len(WorkingShiftIDs)):
        list_working_shift.append({
            "WorkingShiftID":WorkingShiftIDs[i],
            "WorkingShiftName":WorkingShiftNames[i]
        })
    for us_id in users:
        if list(client.db.shift_plan_employee.find({"$and":[{"user_id":us_id},{"ShiftPlanDay":ShiftPlanDay}]})):
            continue
        user_add  = client.db.user.find_one({"_id":us_id})
        _id = str(ObjectId())
        shift_plan_employee = {
            '_id': _id,
            'ShiftPlanDay': datetime.strptime(ShiftPlanDay,"%Y-%m-%dT%H:%M:%S.%fZ"),
            'user_id':user_add['_id'],
            'MaNV':user_add['MaNV'],
            'user_fullname':user_add['full_name'],
            'OrganizationUnitID':user_add['OrganizationUnitID'],
            'OrganizationUnitName':user_add['OrganizationUnitName'],
            'JobPositionID':user_add['JobPositionID'],
            'JobPositionName':user_add['JobPositionName'],
            'WorkingShiftIDs':WorkingShiftIDs,
            'WorkingShiftNames':WorkingShiftNames,
            'WorkingShift':list_working_shift,
            'ModifiedDate':'',
            'ModifiedBy':'',
            'CreateDate': datetime.now(),
            'CreateBy':claims['full_name']
        }
        try:
            client.db.shift_plan_employee.insert_one(shift_plan_employee)
        except Exception as ex:
            return send_error(message='có lỗi ngoại lệ xảy ra')

        notif = notification(content=claims['full_name']+" đã phan ca lam viec  thành công cho "+user_add['MaNV'], user_id=user_curr_id, type=CREATE)
        client.db.history.insert_one(notif)
    return send_result(message="Tạo user thành công ")


