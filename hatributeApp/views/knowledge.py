import json

from flask import Blueprint, request, g

from hatributeApp.util.decorators import only_with_session
from hatributeApp.DB import db_knowledge

knowledge = Blueprint('knowledge', __name__)


@knowledge.route("/get_knowledge_sources", methods=['POST'])
@only_with_session
def get_knowledge_sources(data : dict):
    error_code = db_knowledge.get_knowledge_sources()
    return json.dumps(g.data), error_code
