from flask import Blueprint, request, g
from eureHausaufgabenApp.DB import db_auth
from eureHausaufgabenApp import app
import json

authentication = Blueprint('authentication', __name__)

@authentication.route("/get_salt", methods=['POST'])
def get_salt():
    if request.is_json:
        try:
            data = request.get_json()
            before_request(data)
            email = str(data["email"])
            res, error_code = db_auth.get_salt_by_email(email)
            return json.dumps(res), error_code

        except Exception as e:
            print("get_salt : " + str(e))
            return "Bad Request", 400

    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@authentication.route("/login", methods=['POST'])
def login():
    if request.is_json:
        try:
            data = request.get_json()
            before_request(data)
            email = str(data["email"])
            hashed_pwd = str(data["hashedpwd"])
            res, error_code = db_auth.login(email, hashed_pwd, app.config["secret-key"])
            return json.dumps(res), error_code

        except Exception as e:
            print("Login : " + str(e))
            return "Bad Request", 400

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
            hashed_password = str(data["hashedpwd"])
            salt = str(data["salt"])
            res, error_code = db_auth.create_user(email, name, school, school_class, hashed_password, salt)

            return str(res), error_code
        except Exception as e:
            raise e
            print("Sign in : " + str(e))
            return "Bad Request", 400
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@authentication.route("/check_session", methods=['POST'])
def check_session():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            return_data, error_code = json.dumps(g.session_data), 200
        else:
            return_data, error_code = json.dumps(g.session_data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406


@authentication.route("/get_data", methods=['POST'])
def get_data():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            db_auth.get_user_data()
            return_data, error_code = json.dumps(g.session_data), 200
        else:
            return_data, error_code = json.dumps(g.session_data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406

def before_request(data):
    try:
        session = data["session"]
        other, s_data, user_when_expired = db_auth.check_session(app.config["secret-key"], session)
    except Exception as e:
        g.user = None
        g.session_data = None
        return False
    g.session_data = s_data
    if other:
        print("right session data : " + str(other.Email))
        g.user = other
    else:
        if user_when_expired:
            db_auth.pop_session(user_when_expired)
            print("session expired")
            g.user = None
        else:
            print("session wrong")
            g.user = None
