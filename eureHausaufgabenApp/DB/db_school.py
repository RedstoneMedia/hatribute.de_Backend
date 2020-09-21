from flask import g
from eureHausaufgabenApp.models import Schools


def get_school_by_user():
    return g.user.school

def get_school_by_id(school_id : int):
    return Schools.query.filter_by(id=school_id).first()

def get_school_by_name(school_name : str) -> Schools:
    return Schools.query.filter_by(Name=school_name).first()