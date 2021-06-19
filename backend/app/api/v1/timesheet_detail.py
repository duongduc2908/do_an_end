from flask import Blueprint, json, request
from app.enums import CREATE,UPDATE,DELETE
from app.utils import send_result, send_error,notification
from app.extensions import client
from bson import ObjectId
from flask_jwt_extended import (
    jwt_required)

api = Blueprint('timesheet_detail', __name__)

@api.route('/get_list',methods=["GET"])
@jwt_required
def get_list():
    list_time_sheet = list(client.db.time_sheet.find({},{"_id":1,"TimeSheetName":1}))
    list_resulft = []
    for time_sheet in list_time_sheet:
        list_resulft.append({
            "key":time_sheet["_id"],
            "display_name":time_sheet["TimeSheetName"]
        })
    return send_result(data=list_resulft)


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
    print("skips",skips) 
    '''Give list after filtering'''
    
    query_filter = json.loads(query_filter)
    if len(query_filter["$and"])==0:
        query_filter={}
    print(query_filter)
    timesheet_details = client.db.time_sheet_detail.find(query_filter).sort("MaNV",-1)
        
    totals = timesheet_details.count()
    if skips >=0:
        timesheet_details = timesheet_details.skip(skips).limit(int(page_size))
    '''end list'''
    list_timesheet_detail= list(timesheet_details)
    '''Make a request'''
    data = {
        'totals': totals,
        'results': list_timesheet_detail
    }
    return send_result(data=data)