from flask import Blueprint, json, request
from app.enums import CREATE,UPDATE,DELETE
from app.utils import send_result, send_error,notification
from app.extensions import client
from bson import ObjectId
from datetime import datetime,timedelta
import holidays
import os
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('time_sheet', __name__)


@api.route('/create', methods=['POST'])
@jwt_required
def post():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    days = ['Thu 2', 'Thu 3', 'Thu 4', 'Thu 5', 'Thu 6', 'Thu 7', 'Chu nhat']
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        TimeSheetName = json_data.get('TimeSheetName')
        OrganizationUnitID = json_data.get('OrganizationUnitID')
        OrganizationUnitName = json_data.get('OrganizationUnitName', None)
        JobPositionIDs = json_data.get('JobPositionIDs', None)
        JobPositionNames = json_data.get('JobPositionNames', None)
        FromDate = json_data.get('FromDate', None)
        ToDate = json_data.get('ToDate', None)
        TimeSheetType = json_data.get('TimeSheetType', None)
        IsUseBySummary = json_data.get('IsUseBySummary')
        WorkCalculator = json_data.get('WorkCalculator', None)

    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')

    _id = str(ObjectId())
    time_sheet = {
        '_id': _id,
        'TimeSheetName': TimeSheetName,
        'OrganizationUnitID': OrganizationUnitID,
        'OrganizationUnitName': OrganizationUnitName,
        'JobPositionIDs': JobPositionIDs,
        'JobPositionNames': JobPositionNames,
        'FromDate': FromDate,
        'ToDate': ToDate,
        'TimeSheetType': TimeSheetType,
        'IsUseBySummary': IsUseBySummary,
        'WorkCalculator': WorkCalculator,
        'ModifiedDate': "",
        'ModifiedBy':'',
        'CreateDate': datetime.today(),
        'CreateBy': claims['full_name']
    }
    try:
        client.db.time_sheet.insert_one(time_sheet)
        FromDate = datetime.strptime(FromDate, '%Y-%m-%d')
        ToDate = datetime.strptime(ToDate, '%Y-%m-%d')
        ToDate = ToDate + timedelta(days=1)
        
        # print(int((ToDate-FromDate).days))
        list_results = []
        day_type = ''
        str_fillter_user = {"$and":[{ "JobPositionID": { "$in": JobPositionIDs } },{'OrganizationUnitID':OrganizationUnitID},{'ShiftPlanDay':{"$gte": FromDate , "$lt": ToDate }}]}
        list_user_plan = list(client.db.shift_plan_employee.find(str_fillter_user))
        if len(list_user_plan) >0:
            for us_plan in list_user_plan:
                item = {}
                item["_id"] = str(ObjectId())
                item["TimeSheetID"] = _id
                item["TimeSheetName"] = TimeSheetName
                item["user_id"] = us_plan["user_id"]
                item["user_fullname"] = us_plan["user_fullname"]
                item["MaNV"] = us_plan["MaNV"]
                item["OrganizationUnitID"] = us_plan["OrganizationUnitID"]
                item["OrganizationUnitName"] = us_plan["OrganizationUnitName"]
                item["JobPositionID"] = us_plan["JobPositionID"]
                item["JobPositionName"] = us_plan["JobPositionName"]
                for i in range(0,int((ToDate-FromDate).days)):
                    item["Day{}".format(i+1)] = []
                    date_check = FromDate+timedelta(i)
                    date_check_end = FromDate+timedelta(i+1)
                    is_weekend = False
                    holidays_Vn = holidays.VNM() 
                    is_holiday = date_check.date() in holidays_Vn
                    if not is_holiday:
                        week_no = date_check.weekday()
                        day_type="Ngay trong tuan"
                        if week_no>5:
                            is_weekend = True
                            day_type="Ngay cuoi tuan"
                    else:
                        day_type = "Ngay le"
                    number_rate = 0
                    number_penalty_day_in = 0
                    number_penalty_hour_in = 0
                    number_penalty_day_out = 0
                    number_penalty_hour_out = 0
                    total_working_day = 0
                    
                    str_fillter_user = {"$and":[{ "_id": { "$in": us_plan["WorkingShiftIDs"] } }]}
                    working_shifts = list(client.db.working_shift.find(str_fillter_user))
                    
                    for wk in working_shifts:
                        if is_holiday:
                            number_rate = wk["WorkingRateHoliday"]
                        elif is_weekend:
                            number_rate = wk["WorkingRateWeekend"]
                        else:
                            number_rate = wk["WorkingRateWeekday"]
                            
                        t_start = datetime.strptime(wk["StartTimeInFrom"], '%I:%M %p')
                        t_end = datetime.strptime(wk["StartTimeInTo"], '%I:%M %p')
                        start_check_in = date_check +timedelta(hours=t_start.hour,minutes=t_start.minute)
                        end_check_in = date_check +timedelta(hours=t_end.hour,minutes=t_end.minute)
                        str_fillter_user = {"$and":[{ "EmployeeID": us_plan["user_id"] },{ "OrganizationUnitID": us_plan["OrganizationUnitID"] },{ "JobPositionID": us_plan["JobPositionID"] },{"CheckTime":{"$gte": start_check_in , "$lte": end_check_in }}]}
                        us_data_check_in = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",1).limit(1)
                        if us_data_check_in.count()==0:
                            if wk["CheckStartTime"] and wk["IsShowWithoutCheckin"]:
                                number_penalty_day_in = wk["WorkingDayWithoutCheckin"]
                                number_penalty_hour_in = wk["WorkingHourWithoutCheckin"]
                            str_fillter_user = {"$and":[{ "EmployeeID": us_plan["user_id"] },{ "OrganizationUnitID": us_plan["OrganizationUnitID"] },{ "JobPositionID": us_plan["JobPositionID"] },{"CheckTime":{"$gte": date_check , "$lt": date_check_end }}]}
                            us_data_check_in = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",1)
                            if us_data_check_in.count()>0:
                                us_data_check_in = list(us_data_check_in)[0]["CheckTime"]
                            else:us_data_check_in = None
                        else:
                            us_data_check_in = list(us_data_check_in)[0]["CheckTime"]
                            print(us_data_check_in)
                            print(i)
                        
                        t_start = datetime.strptime(wk["EndTimeInFrom"], '%I:%M %p')
                        t_end = datetime.strptime(wk["EndTimeInTo"], '%I:%M %p')
                        start_check_out = date_check +timedelta(hours=t_start.hour,minutes=t_start.minute)
                        end_check_out = date_check +timedelta(hours=t_end.hour,minutes=t_end.minute)
                        str_fillter_user = {"$and":[{ "EmployeeID": us_plan["user_id"] },{ "OrganizationUnitID": us_plan["OrganizationUnitID"] },{ "JobPositionID": us_plan["JobPositionID"] },{"CheckTime":{"$gte": start_check_out , "$lte": end_check_out }}]}
                        us_data_check_out = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",-1).limit(1)
                        if us_data_check_out.count()==0:
                            if wk["CheckStartTime"] and wk["IsShowWithoutCheckOut"]:
                                number_penalty_day_out = wk["WorkingDayWithoutCheckOut"]
                                number_penalty_hour_out = wk["WorkingHourWithoutCheckOut"]
                            str_fillter_user = {"$and":[{ "EmployeeID": us_plan["user_id"] },{ "OrganizationUnitID": us_plan["OrganizationUnitID"] },{ "JobPositionID": us_plan["JobPositionID"] },{"CheckTime":{"$gte": date_check , "$lt": date_check_end }}]}
                            us_data_check_out = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",-1)
                            if us_data_check_out.count()>0:
                                us_data_check_out = list(us_data_check_out)[0]["CheckTime"]
                            else:us_data_check_out = None
                        else:
                            us_data_check_out = list(us_data_check_out)[0]["CheckTime"]
                        if us_data_check_out == None and us_data_check_in==None:
                            total_working_day = 0
                            total_working_hour = 0
                        else:
                            total_working_day = (float(wk["WorkingDate"])-float(number_penalty_day_in)-float(number_penalty_day_out))*float(number_rate)
                            total_working_hour = (float(wk["WorkingHour"])-float(number_penalty_hour_in)-float(number_penalty_hour_out))*float(number_rate)
                        item["Day{}".format(i+1)].append({
                            "StartTime":wk["StartTime"],
                            "EndTime":wk["EndTime"],
                            "CheckStartTime":us_data_check_in,
                            "CheckEndTime":us_data_check_out,
                            "WorkingShiftCode":wk["WorkingShiftCode"],
                            "WorkingShiftName":wk["WorkingShiftName"],
                            "WorkingShiftID":wk["_id"],
                            "Working_days":total_working_day,
                            "Working_hours":total_working_hour,
                            "Working_plan_day": wk["WorkingDate"],
                            "Working_plan_hour": wk["WorkingHour"],
                            "day_type":day_type,
                            "day":date_check.day,
                            "thu":days[date_check.weekday()]
                        })
                client.db.time_sheet_detail.insert_one(item)
            
    except Exception as ex:
        print(ex)
        return send_error(message='có lỗi ngoại lệ xảy ra')
    
    return send_result(data = '',message="Tạo user thành công ")
        


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
        EmployeeIDs = json_data.get('EmployeeIDs', None)
        EmployeeNames = json_data.get('EmployeeNames', None)

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
            'EmployeeIDs': EmployeeIDs,
            'EmployeeNames': EmployeeNames,
            'CreateDate': shift_plan["CreateDate"],
            'CreateBy': shift_plan["CreateBy"],
            'ModifiedDate': datetime.today(),
            'ModifiedBy': claims['full_name']
        }}
    try:
        client.db.shift_plan.update_one({'_id': Shift_plan_id}, new_shift_plan)
        notif = notification(content=claims['full_name']+" đã sửa phan ca lam viec " + ShiftPlanName + " thành công", user_id=user_curr_id, type=UPDATE)
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
    shift_plans = client.db.shift_plan.find(query_filter)
        
    totals = shift_plans.count()
    if skips:
        shift_plans = shift_plans.skip(skips).limit(int(page_size))
    '''end list'''
    list_shift_plan = list(shift_plans)
    '''Make a request'''
    data = {
        'totals': totals,
        'results': list_shift_plan
    }
    return send_result(data=data)