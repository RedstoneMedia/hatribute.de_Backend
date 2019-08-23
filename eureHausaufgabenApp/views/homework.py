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