from flask import Blueprint, request, g
import json

from eureHausaufgabenApp.DB.db_auth import before_request
from eureHausaufgabenApp.DB import db_knowledge

knowledge = Blueprint('knowledge', __name__)

@knowledge.route("/get_knowledge_sources", methods=['POST'])
def get_knowledge_sources():
    if request.is_json:
        data = request.get_json()
        before_request(data)
        if g.user:
            error_code = db_knowledge.get_knowledge_sources()
            return_data = json.dumps(g.data)
        else:
            return_data, error_code = json.dumps(g.data), 400
        return str(return_data), error_code
    else:
        return str("Unsupported Media Type ! Forgot mime type application/json header ?"), 406