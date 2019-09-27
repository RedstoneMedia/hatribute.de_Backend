from flask import Blueprint, request, g
import json

from eureHausaufgabenApp.DB.db_auth import before_request
from eureHausaufgabenApp.DB import db_mod

modDashboard = Blueprint('modDashboard', __name__)

@modDashboard.route("/get_reports", methods=['POST'])
def get_reports():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_mod.get_reports()
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@modDashboard.route("/reset_sub_homework", methods=['POST'])
def reset_sub_homework():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_mod.reset_sub_homework_from_mod(data["homework_id"], data["sub_homework_id"])
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@modDashboard.route("/get_users_data", methods=['POST'])
def get_users_data():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_mod.get_users_data()
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@modDashboard.route("/remove_points", methods=['POST'])
def remove_points():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_mod.remove_points(data["user_id"], data["points"])
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406