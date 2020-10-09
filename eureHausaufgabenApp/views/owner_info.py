import os
import json

from flask import Blueprint, request, g
from eureHausaufgabenApp.util.decorators import only_json_request

owner_info = Blueprint('owner_info', __name__)

@owner_info.route("/get_owner_info", methods=["POST"])
@only_json_request
def get_owner_info(data: dict):
    if not "this_should_prevent_this_route_being_found_by_some_tools_also_if_you_read_this_dont_go_to_my_house_please_btw_i_hate_this_german_nosense_system" in data:
        return "Not Found", 404
    if os.path.exists(app.config["OWNER_INFO_PATH"]):
        return open(app.config["OWNER_INFO_PATH"], mode="r", encoding="utf-8").read(), 200
    else:
        return "File not found", 404



from eureHausaufgabenApp import app