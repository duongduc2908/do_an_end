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

api = Blueprint('timekeeper_data', __name__)


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
    start_date = request.args.get('start_date')
    to_date = request.args.get('to_date')
    '''Give list after filtering'''
    
    query_filter = json.loads(query_filter)
    if start_date and to_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        to_date = datetime.strptime(to_date, '%Y-%m-%d %H:%M')
        to_date = to_date + timedelta(days=1)
        query_filter['$and'].append({ 'CheckTime': {"$lte": to_date , "$gte": start_date } })
    if len(query_filter["$and"])==0:
        query_filter={}
    print(query_filter)
    timekeeper_datas = client.db.timekeeper_data.find(query_filter).sort("CheckTime",-1)
        
    totals = timekeeper_datas.count()
    if skips >=0:
        timekeeper_datas = timekeeper_datas.skip(skips).limit(int(page_size))
    '''end list'''
    list_timekeeper_data= list(timekeeper_datas)
    '''Make a request'''
    data = {
        'totals': totals,
        'results': list_timekeeper_data
    }
    return send_result(data=data)