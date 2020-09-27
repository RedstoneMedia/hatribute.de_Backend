import json

from flask import Blueprint, request, g
from eureHausaufgabenApp.DB import db_homework
from eureHausaufgabenApp.DB import db_mod
from eureHausaufgabenApp.DB import db_course

from eureHausaufgabenApp.util.decorators import only_with_session

homework = Blueprint('homework', __name__)

@homework.route("/get_user_courses", methods=['POST'])
@only_with_session
def get_user_courses(data : dict):
    if "include_homework" in data:
        error_code = db_course.get_user_courses(include_homework=data["include_homework"])
    else:
        error_code = db_course.get_user_courses()
    return json.dumps(g.data), error_code


@homework.route("/get_all_user_school_courses", methods=['POST'])
@only_with_session
def get_all_user_school_courses(data : dict):
    error_code = db_course.get_all_user_school_courses()
    return json.dumps(g.data), error_code


@homework.route("/add_user_course", methods=['POST'])
@only_with_session
def add_user_course(data : dict):
    if "course_id" in data:
        course = db_course.get_course_by_course_id(int(data["course_id"]))
        if course == None:
            return 404
        error_code = db_course.add_course_to_user(g.user, course)
        return json.dumps(g.data), error_code
    return 400


@homework.route("/remove_user_course", methods=['POST'])
@only_with_session
def remove_user_course(data : dict):
    if "course_id" in data:
        course = db_course.get_course_by_course_id(int(data["course_id"]))
        if course == None:
            return 404
        error_code = db_course.remove_course_from_user(course, g.user)
        return json.dumps(g.data), error_code
    return 400


@homework.route("/add_homework", methods=['POST'])
@only_with_session
def add_homework(data : dict):
    error_code = db_homework.add_homework(data["exercise"], int(data["course_id"]), data["subExercises"], data["dueDate"])
    return json.dumps(g.data), error_code


@homework.route("/register_for_sub_homework", methods=['POST'])
@only_with_session
def register_for_sub_homework(data : dict):
    error_code = db_homework.register_user_for_sub_homework(data["sub_homework_id"])
    return json.dumps(g.data), error_code


@homework.route("/de_register_for_sub_homework", methods=['POST'])
@only_with_session
def de_register_for_sub_homework(data : dict):
    error_code = db_homework.de_register_user_for_sub_homework(data["sub_homework_id"])
    return json.dumps(g.data), error_code


@homework.route("/upload_sub_homework", methods=['POST'])
@only_with_session
def upload_sub_homework(data : dict):
    error_code = db_homework.upload_sub_homework(data["sub_homework_id"], data["base64Files"])
    return json.dumps(g.data), error_code


@homework.route("/get_sub_homework_images_url",  methods=['POST'])
@only_with_session
def get_sub_homework_images_url(data : dict):
    error_code = db_homework.get_sub_homework_images_url(data["sub_homework_id"])
    return json.dumps(g.data), error_code


@homework.route("/get_sub_homework_base64_images",  methods=['POST'])
@only_with_session
def get_sub_homework_base64_images(data : dict):
    error_code = db_homework.get_sub_homework_base64_images(data["sub_homework_id"])
    return json.dumps(g.data), error_code


@homework.route("/delete_homework",  methods=['POST'])
@only_with_session
def delete_homework(data : dict):
    homework_id = data["homework_id"]
    error_code = db_homework.delete_homework(homework_id)
    return json.dumps(g.data), error_code


@homework.route("/report_sub_image",  methods=['POST'])
@only_with_session
def report_sub_image(data : dict):
    error_code = db_mod.report_sub_homework(data["sub_homework_id"], data["type"])
    return json.dumps(g.data), error_code