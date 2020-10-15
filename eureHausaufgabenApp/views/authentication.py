from flask import Blueprint, request, g

from eureHausaufgabenApp.DB import db_auth, db_user
from eureHausaufgabenApp import app
import json

from eureHausaufgabenApp.DB.db_auth import handel_session_request
from eureHausaufgabenApp.util.decorators import only_with_session, only_json_request

authentication = Blueprint('authentication', __name__)

@authentication.route("/login", methods=['POST'])
@only_json_request
def login(data : dict):
    handel_session_request(data)
    user_name = str(data["user_name"])
    password = str(data["password"])
    stay_logged_in = bool(data["stay_logged_in"])
    res, error_code = db_auth.login(user_name, password, stay_logged_in)
    return json.dumps(res), error_code


@authentication.route("/sign-in", methods=['POST'])
@only_json_request
def sign_in(data: dict):
    handel_session_request(data)
    user_name = str(data["user_name"])
    school = str(data["school"]).lower().replace(" ", "-").replace("_", "-")
    password = str(data["password"])
    first_time_sign_in_token = str(data["first_time_sign_in_token"])
    res, error_code = db_user.create_user(user_name, school, password, first_time_sign_in_token)
    return res, error_code


@authentication.route("/logout", methods=['POST'])
@only_with_session
def logout(data : dict):
    db_auth.logout()
    return json.dumps(g.data), 200


@authentication.route("/delete_account", methods=['POST'])
@only_with_session
def delete_account(data : dict):
    db_user.reset_account()
    return json.dumps(g.data), 200


@authentication.route("/check_session", methods=['POST'])
@only_with_session
def check_session(data : dict):
    return json.dumps(g.data), 200


@authentication.route("/get_data", methods=['POST'])
@only_with_session
def get_data(data : dict):
    db_user.get_user_data()
    return json.dumps(g.data), 200