from flask import Blueprint, request, g
import json
from eureHausaufgabenApp.DB import db_homework

from eureHausaufgabenApp.DB.db_auth import before_request

homework = Blueprint('homework', __name__)

@homework.route("/get_school_class", methods=['POST'])
def get_homework_data():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_homework.get_school_class_data()
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@homework.route("/add_homework", methods=['POST'])
def add_homework():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_homework.add_homework(data["exercise"], data["subject"], data["subExercises"], data["dueDate"])
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@homework.route("/register_for_sub_homework", methods=['POST'])
def register_for_sub_homework():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_homework.register_user_for_sub_homework(data["homework_id"], data["sub_homework_id"])
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@homework.route("/de_register_for_sub_homework", methods=['POST'])
def de_register_for_sub_homework():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_homework.de_register_user_for_sub_homework(data["homework_id"], data["sub_homework_id"])
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@homework.route("/upload_sub_homework", methods=['POST'])
def upload_sub_homework():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_homework.upload_sub_homework(data["homework_id"], data["sub_homework_id"], data["base64Files"])
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@homework.route("/get_sub_homework_images",  methods=['POST'])
def get_sub_homework_images():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_homework.get_sub_homework_images_as_base64(data["homework_id"], data["sub_homework_id"])
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406

"""
@homework.route("/get_time_table",  methods=['POST'])
def get_time_table():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_homework.get_time_table(data["units_username"], data["units_password"])
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406
"""

"""

@homework.route("/get_time_table_download_info",  methods=['POST'])
def get_time_table_download_info():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_homework.get_time_table_download_info()
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406
"""