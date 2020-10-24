import json

from flask import Blueprint, request, g
from hatributeApp.DB import db_sub_homework

from hatributeApp.util.decorators import only_with_session

sub_homework = Blueprint('sub_homework', __name__)


@sub_homework.route("/register_for_sub_homework", methods=['POST'])
@only_with_session
def register_for_sub_homework(data : dict):
    error_code = db_sub_homework.register_user_for_sub_homework(data["sub_homework_id"])
    return json.dumps(g.data), error_code


@sub_homework.route("/de_register_for_sub_homework", methods=['POST'])
@only_with_session
def de_register_for_sub_homework(data : dict):
    error_code = db_sub_homework.de_register_user_for_sub_homework(data["sub_homework_id"])
    return json.dumps(g.data), error_code


@sub_homework.route("/upload_sub_homework", methods=['POST'])
@only_with_session
def upload_sub_homework(data : dict):
    error_code = db_sub_homework.upload_sub_homework(data["sub_homework_id"], data["base64Files"])
    return json.dumps(g.data), error_code


@sub_homework.route("/get_sub_homework_images_url",  methods=['POST'])
@only_with_session
def get_sub_homework_images_url(data : dict):
    error_code = db_sub_homework.get_sub_homework_images_url(data["sub_homework_id"])
    return json.dumps(g.data), error_code


@sub_homework.route("/get_sub_homework_base64_images",  methods=['POST'])
@only_with_session
def get_sub_homework_base64_images(data : dict):
    error_code = db_sub_homework.get_sub_homework_base64_images(data["sub_homework_id"])
    return json.dumps(g.data), error_code