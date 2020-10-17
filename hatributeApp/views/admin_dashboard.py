import json

from flask import Blueprint, g

from hatributeApp.util.decorators import only_with_session
from hatributeApp.DB import db_admin
from hatributeApp.DB import db_course

admin_dashboard = Blueprint('admin_dashboard', __name__)

@admin_dashboard.route("/write_user_changes", methods=['POST'])
@only_with_session
def write_user_changes(data : dict):
    error_code = db_admin.write_user_changes(data["user_changes"])
    return json.dumps(g.data), error_code


@admin_dashboard.route("/generate_new_token_for_deactivated_user", methods=['POST'])
@only_with_session
def generate_new_token_for_deactivated_user(data : dict):
    error_code = db_admin.generate_new_token_for_deactivated_user(int(data["user_id"]))
    return json.dumps(g.data), error_code


@admin_dashboard.route("/setup_new_user", methods=['POST'])
@only_with_session
def setup_new_user(data : dict):
    error_code = db_admin.setup_new_user(data["user_name"], data["school_name"])
    return json.dumps(g.data), error_code


@admin_dashboard.route("/remove_deactivated_account", methods=['POST'])
@only_with_session
def remove_deactivated_account(data : dict):
    error_code = db_admin.remove_deactivated_user(int(data["user_id"]))
    return json.dumps(g.data), error_code


@admin_dashboard.route("/get_all_courses", methods=['POST'])
@only_with_session
def get_all_courses(data : dict):
    error_code = db_course.get_all_courses()
    return json.dumps(g.data), error_code


@admin_dashboard.route("/write_course_changes", methods=['POST'])
@only_with_session
def write_course_changes(data : dict):
    error_code = db_admin.write_course_changes(data["course_changes"])
    return json.dumps(g.data), error_code


@admin_dashboard.route("/add_course", methods=['POST'])
@only_with_session
def add_course(data : dict):
    error_code = db_course.create_course(data["course_name"], data["school_name"], bool(data["is_default_course"]))
    return json.dumps(g.data), error_code


@admin_dashboard.route("/remove_course", methods=['POST'])
@only_with_session
def remove_course(data : dict):
    error_code = db_course.remove_course(int(data["course_id"]))
    return json.dumps(g.data), error_code


@admin_dashboard.route("/get_all_schools", methods=['POST'])
@only_with_session
def get_all_schools(data : dict):
    error_code = db_admin.get_all_schools()
    return json.dumps(g.data), error_code


@admin_dashboard.route("/write_school_changes", methods=['POST'])
@only_with_session
def write_school_changes(data : dict):
    error_code = db_admin.write_school_changes(data["school_changes"])
    return json.dumps(g.data), error_code


@admin_dashboard.route("/add_school", methods=['POST'])
@only_with_session
def add_school(data : dict):
    error_code = db_admin.add_school(data["school_name"])
    return json.dumps(g.data), error_code


@admin_dashboard.route("/remove_school", methods=['POST'])
@only_with_session
def remove_school(data : dict):
    error_code = db_admin.remove_school(data["school_id"])
    return json.dumps(g.data), error_code