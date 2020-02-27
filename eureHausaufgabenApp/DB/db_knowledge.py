from flask import g
from sqlalchemy import or_

from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import Users, KnowledgeSources

def knowledge_source_to_dict(knowledge_source):
    result = {
        "id" : knowledge_source.id,
        "Type" : knowledge_source.Type,
        "ByUser" : user_to_dict(get_user_by_id(knowledge_source.ByUserId)),
        "Data" : knowledge_source.Data,
        "Votes" : knowledge_source.Votes,
        "CreationTime" : str(knowledge_source.CreationTime),
        "LastModifiedTime" : str(knowledge_source.LastModifiedTime)
    }
    return result

def get_knowledge_sources():
    user = get_user_by_id(g.user.id)
    if user.Role == -1:
        return 403

    data = []
    available_knowledge_sources = KnowledgeSources.query.filter(or_(KnowledgeSources.SchoolClassId == -1, KnowledgeSources.SchoolClassId == user.SchoolClassId))
    for knowledge_source in available_knowledge_sources:
        data.append(knowledge_source_to_dict(knowledge_source))
    g.data["knowledge_sources"] = data
    return 200

from .db_school import get_school_class_by_user, is_user_in_users_school
from .db_user import get_user_by_id, user_to_dict