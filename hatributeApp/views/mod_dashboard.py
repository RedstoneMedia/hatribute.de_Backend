import json

from flask import Blueprint, request, g

from hatributeApp.util.decorators import only_with_session
from hatributeApp.DB import db_mod

mod_dashboard = Blueprint('mod_dashboard', __name__)

@mod_dashboard.route("/get_reports", methods=['POST'])
@only_with_session
def get_reports(data: dict):
    error_code = db_mod.get_reports()
    return json.dumps(g.data), error_code


@mod_dashboard.route("/reset_sub_homework", methods=['POST'])
@only_with_session
def reset_sub_homework(data: dict):
    error_code = db_mod.reset_sub_homework_from_mod(data["sub_homework_id"])
    return json.dumps(g.data), error_code


@mod_dashboard.route("/get_users_data", methods=['POST'])
@only_with_session
def get_users_data(data: dict):
    error_code = db_mod.get_users_data()
    return json.dumps(g.data), error_code


@mod_dashboard.route("/remove_points", methods=['POST'])
@only_with_session
def remove_points(data: dict):
    error_code = db_mod.remove_points(data["user_id"], data["points"])
    return json.dumps(g.data), error_code


@mod_dashboard.route("/remove_false_report", methods=['POST'])
@only_with_session
def remove_false_report(data: dict):
    error_code = db_mod.remove_false_report_from_mod(data["sub_homework_id"])
    return json.dumps(g.data), error_code