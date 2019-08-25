from flask import Blueprint, request, g, send_from_directory
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
            error_code = db_homework.add_homework(data["exercise"], data["subject"], data["subExercises"])
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


@homework.route("/get_sub_homework_image_count", methods=['POST'])
def get_sub_homework_image_count():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_homework.get_sub_homework_image_count(data["homework_id"], data["sub_homework_id"])
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@homework.route("/get_sub_homework_image",  methods=['GET'])
def get_sub_homework_image():
    try:
        data = request.args
        image_dir = db_homework.get_homework_image_dir(data["sub_homework_id"])
        return send_from_directory(image_dir, "{}.png".format(data["image_count"]), mimetype='png'), 200
    except Exception as e:
        print("Exception in get_image() : " + str(e))
        return "Bad Request", 400
