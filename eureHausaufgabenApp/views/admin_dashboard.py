import json

from flask import Blueprint, g

from eureHausaufgabenApp.util.decorators import only_with_session
from eureHausaufgabenApp.DB import db_admin

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