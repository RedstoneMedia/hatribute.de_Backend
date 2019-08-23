from flask import request, g
from datetime import date
import json
from eureHausaufgabenApp import db, app
from .db_homework import homework_to_dict
from eureHausaufgabenApp.models import Schools
from eureHausaufgabenApp.models import SchoolClasses
from eureHausaufgabenApp.models import HomeworkLists

def get_school_by_user():
    school = Schools.query.filter_by(Name=g.user.School).first()
    return school

def get_school_class_by_user():
    school = get_school_by_user()
    if not school:
        return

    school_class = SchoolClasses.query.filter_by(ClassName=g.user.SchoolClass).first()
    if school_class.SchoolId == school.id:
        return school_class


def school_class_to_dict(school_class):
    homework_list = HomeworkLists.query.filter_by(SchoolClassId=school_class.id)
    school_class_return = {
        "ClassName" : school_class.ClassName,
        "homework" : []
    }
    for h in homework_list:
        school_class_return["homework"].append(homework_to_dict(h))
    return school_class_return
