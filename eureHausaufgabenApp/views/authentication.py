from flask import Blueprint, request, g

import eureHausaufgabenApp.DB.db_user
from eureHausaufgabenApp.DB import db_auth, db_user
from eureHausaufgabenApp import app
import json
import traceback

from eureHausaufgabenApp.DB.db_auth import before_request

authentication = Blueprint('authentication', __name__)

@authentication.route("/login", methods=['POST'])
def login():
    if request.is_json:
        try:
            data = request.get_json()
            before_request(data)
            email = str(data["email"])
            password = str(data["password"])
            stay_logged_in = bool(data["stay_logged_in"])
            res, error_code = db_auth.login(email, password, stay_logged_in, app.config["secret-key"])
            return json.dumps(res), error_code

        except Exception as e:
            app.logger.error("login : " + traceback.format_exc())
            return "Bad Request", 400

    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@authentication.route("/logout", methods=['POST'])
def logout():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            db_auth.logout()
            return_data, error_code = json.dumps(g.data), 200
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@authentication.route("/delete_account", methods=['POST'])
def delete_account():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            db_user.reset_account()
            return_data, error_code = json.dumps(g.data), 200
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@authentication.route("/sign-in", methods=['POST'])
def sign_in():
    if request.is_json:
        try:
            data = request.get_json()
            name = str(data["name"])
            school = str(data["school"]).lower().replace(" ", "-").replace("_", "-")
            school_class = str(data["school_class"]).upper()
            email = str(data["email"])
            password = str(data["password"])
            res, error_code = eureHausaufgabenApp.DB.db_user.create_user(email, name, school, school_class, password)
            return str(res), error_code
        except Exception as e:
            app.logger.error("Sign in : " + traceback.format_exc())
            return "Bad Request", 400
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@authentication.route("/check_session", methods=['POST'])
def check_session():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            return_data, error_code = json.dumps(g.data), 200
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@authentication.route("/get_data", methods=['POST'])
def get_data():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            eureHausaufgabenApp.DB.db_user.get_user_data()
            return_data, error_code = json.dumps(g.data), 200
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406