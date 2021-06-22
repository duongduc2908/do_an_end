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
    days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        TimeSheetName = json_data.get('TimeSheetName')
        OrganizationUnitID = json_data.get('OrganizationUnitID')
        JobPositionIDs = json_data.get('JobPositionIDs', "")
        FromDate = json_data.get('FromDate', "")
        ToDate = json_data.get('ToDate', "")
        WorkCalculator = json_data.get('WorkCalculator', "")
    
    except Exception as ex:
        print(ex)
        return send_error(message='Lỗi dữ liệu đầu vào')
    og = client.db.organization_unit.find_one({"_id":OrganizationUnitID})
    JobPositionNames=[]
    for jb in JobPositionIDs:
        jp = client.db.job_position.find_one({"_id":jb})
        JobPositionNames.append(jp["JobPositionName"])
    _id = str(ObjectId())
    time_sheet = {
        '_id': _id,
        'TimeSheetName': TimeSheetName,
        'OrganizationUnitID': OrganizationUnitID,
        'OrganizationUnitName': og["OrganizationUnitName"],
        'JobPositionIDs': JobPositionIDs,
        'JobPositionNames': JobPositionNames,
        'FromDate': FromDate,
        'ToDate': ToDate,
        'WorkCalculator': WorkCalculator,
        'ModifiedDate': "",
        'ModifiedBy':'',
        'CreateDate': datetime.today(),
        'CreateBy': claims['full_name']
    }
    # try:
    
    FromDate = datetime.strptime(FromDate, '%Y-%m-%d')
    ToDate = datetime.strptime(ToDate, '%Y-%m-%d')
    ToDate = ToDate + timedelta(days=1)
    
    day_type = ''
    str_fillter_user = {"$and":[{ "JobPositionID": { "$in": JobPositionIDs } },{'OrganizationUnitID':OrganizationUnitID},{'ShiftPlanDay':{"$gte": FromDate , "$lt": ToDate }}]}
    list_user_plan = list(client.db.shift_plan_employee.find(str_fillter_user))
    
    
    if len(list_user_plan) >0:
        list_user_check = []
        list_plan_day = {}
        for us in list_user_plan:
            if us["user_id"] not in list_user_check:
                list_user_check.append(us["user_id"])
                list_plan_day[us["user_id"]] = [{"ShiftPlanDay":us["ShiftPlanDay"],"WorkingShiftIDs":us["WorkingShiftIDs"]} ]
            else:list_plan_day[us["user_id"]].append({"ShiftPlanDay":us["ShiftPlanDay"],"WorkingShiftIDs":us["WorkingShiftIDs"]})
        for us_plan in list_user_check:
            totals_plan_day = 0
            totals_check_days = 0
            item = {}
            us_check =client.db.user.find_one({"_id":us_plan})
            item["_id"] = str(ObjectId())
            item["TimeSheetID"] = _id
            item["TimeSheetName"] = TimeSheetName
            item["user_id"] = us_check["_id"]
            item["user_fullname"] = us_check["full_name"]
            item["MaNV"] = us_check["MaNV"]
            item["OrganizationUnitID"] = us_check["OrganizationUnitID"]
            item["OrganizationUnitName"] = us_check["OrganizationUnitName"]
            item["JobPositionID"] = us_check["JobPositionID"]
            item["JobPositionName"] = us_check["JobPositionName"]
            for i in range(0,int((ToDate-FromDate).days)):
                item["Day{}".format(i+1)] = []
                date_check = FromDate+timedelta(i)
                date_check_end = FromDate+timedelta(i+1)
                for plan_day in list_plan_day[us_plan]:
                    date_plan = plan_day["ShiftPlanDay"].date()
                    if not(date_plan == date_check.date()):
                        continue
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
                    
                    str_fillter_user = {"$and":[{ "_id": { "$in": plan_day["WorkingShiftIDs"] } }]}
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
                        str_fillter_user = {"$and":[{ "EmployeeID": us_check["_id"] },{ "OrganizationUnitID": us_check["OrganizationUnitID"] },{ "JobPositionID": us_check["JobPositionID"] },{"CheckTime":{"$gte": start_check_in , "$lte": end_check_in }}]}
                        us_data_check_in = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",1).limit(1)
                        if us_data_check_in.count()==0:
                            if wk["CheckStartTime"] and wk["IsShowWithoutCheckin"]:
                                number_penalty_day_in = wk["WorkingDayWithoutCheckin"]
                                number_penalty_hour_in = wk["WorkingHourWithoutCheckin"]
                            str_fillter_user = {"$and":[{ "EmployeeID": us_check["_id"] },{ "OrganizationUnitID": us_check["OrganizationUnitID"] },{ "JobPositionID": us_check["JobPositionID"] },{"CheckTime":{"$gte": date_check , "$lt": date_check_end }}]}
                            us_data_check_in = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",1)
                            if us_data_check_in.count()>0:
                                us_data_check_in = list(us_data_check_in)[0]["CheckTime"]
                            else:us_data_check_in = None
                        else:
                            us_data_check_in = list(us_data_check_in)[0]["CheckTime"]
                        
                        t_start = datetime.strptime(wk["EndTimeInFrom"], '%I:%M %p')
                        t_end = datetime.strptime(wk["EndTimeInTo"], '%I:%M %p')
                        start_check_out = date_check +timedelta(hours=t_start.hour,minutes=t_start.minute)
                        end_check_out = date_check +timedelta(hours=t_end.hour,minutes=t_end.minute)

                        str_fillter_user = {"$and":[{ "EmployeeID": us_check["_id"] },{ "OrganizationUnitID": us_check["OrganizationUnitID"] },{ "JobPositionID": us_check["JobPositionID"] },{"CheckTime":{"$gte": start_check_out , "$lte": end_check_out }}]}
                        us_data_check_out = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",-1).limit(1)
                        if us_data_check_out.count()==0:
                            if wk["CheckStartTime"] and wk["IsShowWithoutCheckOut"]:
                                number_penalty_day_out = wk["WorkingDayWithoutCheckOut"]
                                number_penalty_hour_out = wk["WorkingHourWithoutCheckOut"]
                            str_fillter_user = {"$and":[{ "EmployeeID": us_check["_id"] },{ "OrganizationUnitID": us_check["OrganizationUnitID"] },{ "JobPositionID": us_check["JobPositionID"] },{"CheckTime":{"$gte": date_check , "$lt": date_check_end }}]}
                            us_data_check_out = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",-1)
                            if us_data_check_out.count()>0:
                                us_data_check_out = list(us_data_check_out)[0]["CheckTime"]
                            else:us_data_check_out = None
                        else:
                            us_data_check_out = list(us_data_check_out)[0]["CheckTime"]

                            
                        if us_data_check_out == None and us_data_check_in==None:
                            number_penalty_day_out = number_penalty_day_in = float(wk["WorkingDate"])/2
                            number_penalty_hour_out = number_penalty_hour_in = float(wk["WorkingHour"])/2
                        total_working_day = float(wk["WorkingDate"])*float(number_rate)-float(number_penalty_day_in)-float(number_penalty_day_out)
                        total_working_hour = float(wk["WorkingHour"])*float(number_rate)-float(number_penalty_hour_in)-float(number_penalty_hour_out)
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
                            "thu":days[date_check.weekday()],
                            "check_in_date":date_check,
                            "penalty_day_in":float(number_penalty_day_in),
                            "penalty_day_out":float(number_penalty_day_out),
                            "penalty_hour_in":float(number_penalty_hour_in),
                            "penalty_hour_out":float(number_penalty_hour_out)
                            
                        })
                        totals_plan_day += float(wk["WorkingDate"])*float(number_rate)
                        totals_check_days+=total_working_day
            item["totals_check_day"] = totals_check_days
            item["totals_plan_day"] = totals_plan_day
            client.db.time_sheet_detail.insert_one(item)
    client.db.time_sheet.insert_one(time_sheet)
    
    return send_result(data = '',message="Tạo user thành công ")




@api.route('/update', methods=['POST'])
@jwt_required
def Update():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        _id = json_data.get('_id')
        TimeSheetName = json_data.get('TimeSheetName')
        OrganizationUnitID = json_data.get('OrganizationUnitID')
        JobPositionIDs = json_data.get('JobPositionIDs', "")
        FromDate = json_data.get('FromDate', "")
        ToDate = json_data.get('ToDate', "")
        WorkCalculator = json_data.get('WorkCalculator', "")
    except Exception as ex:
        print(ex)
        return send_error()
    client.db.time_sheet.delete_one({'_id': _id})
    client.db.time_sheet_detail.delete_many({'TimeSheetID': _id})
    og = client.db.organization_unit.find_one({"_id":OrganizationUnitID})
    JobPositionNames=[]
    for jb in JobPositionIDs:
        jp = client.db.job_position.find_one({"_id":jb})
        JobPositionNames.append(jp["JobPositionName"])
    _id = str(ObjectId())
    time_sheet = {
        '_id': _id,
        'TimeSheetName': TimeSheetName,
        'OrganizationUnitID': OrganizationUnitID,
        'OrganizationUnitName': og["OrganizationUnitName"],
        'JobPositionIDs': JobPositionIDs,
        'JobPositionNames': JobPositionNames,
        'FromDate': FromDate,
        'ToDate': ToDate,
        'WorkCalculator': WorkCalculator,
        'ModifiedDate': "",
        'ModifiedBy':'',
        'CreateDate': datetime.today(),
        'CreateBy': claims['full_name']
    }
    # try:
    
    FromDate = datetime.strptime(FromDate, '%Y-%m-%d')
    ToDate = datetime.strptime(ToDate, '%Y-%m-%d')
    ToDate = ToDate + timedelta(days=1)
    
    day_type = ''
    str_fillter_user = {"$and":[{ "JobPositionID": { "$in": JobPositionIDs } },{'OrganizationUnitID':OrganizationUnitID},{'ShiftPlanDay':{"$gte": FromDate , "$lt": ToDate }}]}
    list_user_plan = list(client.db.shift_plan_employee.find(str_fillter_user))
    
    
    if len(list_user_plan) >0:
        list_user_check = []
        list_plan_day = {}
        for us in list_user_plan:
            if us["user_id"] not in list_user_check:
                list_user_check.append(us["user_id"])
                list_plan_day[us["user_id"]] = [{"ShiftPlanDay":us["ShiftPlanDay"],"WorkingShiftIDs":us["WorkingShiftIDs"]} ]
            else:list_plan_day[us["user_id"]].append({"ShiftPlanDay":us["ShiftPlanDay"],"WorkingShiftIDs":us["WorkingShiftIDs"]})
        for us_plan in list_user_check:
            totals_plan_day = 0
            totals_check_days = 0
            item = {}
            us_check =client.db.user.find_one({"_id":us_plan})
            item["_id"] = str(ObjectId())
            item["TimeSheetID"] = _id
            item["TimeSheetName"] = TimeSheetName
            item["user_id"] = us_check["_id"]
            item["user_fullname"] = us_check["full_name"]
            item["MaNV"] = us_check["MaNV"]
            item["OrganizationUnitID"] = us_check["OrganizationUnitID"]
            item["OrganizationUnitName"] = us_check["OrganizationUnitName"]
            item["JobPositionID"] = us_check["JobPositionID"]
            item["JobPositionName"] = us_check["JobPositionName"]
            for i in range(0,int((ToDate-FromDate).days)):
                item["Day{}".format(i+1)] = []
                date_check = FromDate+timedelta(i)
                date_check_end = FromDate+timedelta(i+1)
                for plan_day in list_plan_day[us_plan]:
                    date_plan = plan_day["ShiftPlanDay"].date()
                    if not(date_plan == date_check.date()):
                        continue
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
                    
                    str_fillter_user = {"$and":[{ "_id": { "$in": plan_day["WorkingShiftIDs"] } }]}
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
                        str_fillter_user = {"$and":[{ "EmployeeID": us_check["_id"] },{ "OrganizationUnitID": us_check["OrganizationUnitID"] },{ "JobPositionID": us_check["JobPositionID"] },{"CheckTime":{"$gte": start_check_in , "$lte": end_check_in }}]}
                        us_data_check_in = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",1).limit(1)
                        if us_data_check_in.count()==0:
                            if wk["CheckStartTime"] and wk["IsShowWithoutCheckin"]:
                                number_penalty_day_in = wk["WorkingDayWithoutCheckin"]
                                number_penalty_hour_in = wk["WorkingHourWithoutCheckin"]
                            str_fillter_user = {"$and":[{ "EmployeeID": us_check["_id"] },{ "OrganizationUnitID": us_check["OrganizationUnitID"] },{ "JobPositionID": us_check["JobPositionID"] },{"CheckTime":{"$gte": date_check , "$lt": date_check_end }}]}
                            us_data_check_in = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",1)
                            if us_data_check_in.count()>0:
                                us_data_check_in = list(us_data_check_in)[0]["CheckTime"]
                            else:us_data_check_in = None
                        else:
                            us_data_check_in = list(us_data_check_in)[0]["CheckTime"]
                        
                        t_start = datetime.strptime(wk["EndTimeInFrom"], '%I:%M %p')
                        t_end = datetime.strptime(wk["EndTimeInTo"], '%I:%M %p')
                        start_check_out = date_check +timedelta(hours=t_start.hour,minutes=t_start.minute)
                        end_check_out = date_check +timedelta(hours=t_end.hour,minutes=t_end.minute)

                        str_fillter_user = {"$and":[{ "EmployeeID": us_check["_id"] },{ "OrganizationUnitID": us_check["OrganizationUnitID"] },{ "JobPositionID": us_check["JobPositionID"] },{"CheckTime":{"$gte": start_check_out , "$lte": end_check_out }}]}
                        us_data_check_out = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",-1).limit(1)
                        if us_data_check_out.count()==0:
                            if wk["CheckStartTime"] and wk["IsShowWithoutCheckOut"]:
                                number_penalty_day_out = wk["WorkingDayWithoutCheckOut"]
                                number_penalty_hour_out = wk["WorkingHourWithoutCheckOut"]
                            str_fillter_user = {"$and":[{ "EmployeeID": us_check["_id"] },{ "OrganizationUnitID": us_check["OrganizationUnitID"] },{ "JobPositionID": us_check["JobPositionID"] },{"CheckTime":{"$gte": date_check , "$lt": date_check_end }}]}
                            us_data_check_out = client.db.timekeeper_data.find(str_fillter_user).sort("CheckTime",-1)
                            if us_data_check_out.count()>0:
                                us_data_check_out = list(us_data_check_out)[0]["CheckTime"]
                            else:us_data_check_out = None
                        else:
                            us_data_check_out = list(us_data_check_out)[0]["CheckTime"]

                            
                        if us_data_check_out == None and us_data_check_in==None:
                            number_penalty_day_out = number_penalty_day_in = float(wk["WorkingDate"])/2
                            number_penalty_hour_out = number_penalty_hour_in = float(wk["WorkingHour"])/2
                        total_working_day = float(wk["WorkingDate"])*float(number_rate)-float(number_penalty_day_in)-float(number_penalty_day_out)
                        total_working_hour = float(wk["WorkingHour"])*float(number_rate)-float(number_penalty_hour_in)-float(number_penalty_hour_out)
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
                            "thu":days[date_check.weekday()],
                            "check_in_date":date_check,
                            "penalty_day_in":float(number_penalty_day_in),
                            "penalty_day_out":float(number_penalty_day_out),
                            "penalty_hour_in":float(number_penalty_hour_in),
                            "penalty_hour_out":float(number_penalty_hour_out)
                            
                        })
                        totals_plan_day += float(wk["WorkingDate"])*float(number_rate)
                        totals_check_days+=total_working_day
            item["totals_check_day"] = totals_check_days
            item["totals_plan_day"] = totals_plan_day
            client.db.time_sheet_detail.insert_one(item)
    client.db.time_sheet.insert_one(time_sheet)
    
    return send_result(data = '',message="Sua bang luong thành công ")
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
    time_sheets = client.db.time_sheet.find(query_filter)
        
    totals = time_sheets.count()
    if skips:
        time_sheets = time_sheets.skip(skips).limit(int(page_size))
    '''end list'''
    list_time_sheet = list(time_sheets)
    '''Make a request'''
    data = {
        'totals': totals,
        'results': list_time_sheet
    }
    return send_result(data=data)


@api.route('/delete', methods=['POST'])
@jwt_required
def Delete():
    user_curr_id = get_jwt_identity()
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")
    try:
        json_data = request.get_json()
        _id = json_data.get('_id')
    except Exception as ex:
        print(ex)
        return send_error()
    client.db.time_sheet.delete_one({'_id': _id})
    client.db.time_sheet_detail.delete_many({'TimeSheetID': _id})
    return send_result()
