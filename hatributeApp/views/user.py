from flask import Blueprint, request, g

from hatributeApp.DB import db_user
from hatributeApp import app
import json

from hatributeApp.util.decorators import only_with_session

user = Blueprint('user', __name__)

@user.route("/delete_account", methods=['POST'])
@only_with_session
def delete_account(data : dict):
    db_user.reset_account()
    return json.dumps(g.data), 200


@user.route("/get_data", methods=['POST'])
@only_with_session
def get_data(data : dict):
    db_user.get_user_data()
    return json.dumps(g.data), 200