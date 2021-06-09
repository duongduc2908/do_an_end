from flask import Blueprint, request
from app.enums import USER_ACTIVATED, USER_DEACTIVATED, STATUS_USER,CREATE,UPDATE,DELETE
from app.utils import parse_req, FieldString, send_result, send_error, hash_password, set_auto_MaNV, notification
from app.extensions import client
from bson import ObjectId
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity)

api = Blueprint('subsystem_permission', __name__)


@api.route('/get_all_sub_items', methods=['GET'])
@jwt_required
def get_all_sub_items():
    text_search = request.args.get('text_search', '')
    page_size = request.args.get('page_size', '25')
    page_number = request.args.get('page_number', '0')
    skips = int(page_size) * int(page_number)
    '''Give list after filtering'''
    query ={'$or': [
                {'subsystem_code': {'$regex': text_search, '$options': "$i"}},
                {'subsystem_name': {'$regex': text_search, '$options': "$i"}},
                {'permission_code': {'$regex': text_search, '$options': "$i"}}
            ]}
        
    sub_items = client.db.subsystem_permission.find(query)
    list_sub_items = list(sub_items)
    return send_result(data=list_sub_items)

