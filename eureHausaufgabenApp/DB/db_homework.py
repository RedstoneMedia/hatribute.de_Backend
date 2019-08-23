from flask import request, g
from datetime import date
import json
from .db_user import user_to_dict
from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import SubHomeworkLists
from eureHausaufgabenApp.models import Users

def get_school_class_data():
    school_class_dict = get_school_class_dict_by_user()
    if school_class_dict:
        g.data["school_class"] = school_class_dict
        return 200
    else:
        return 401

def get_school_class_dict_by_user():
    school_class = get_school_class_by_user()
    if school_class:
        return school_class_to_dict(school_class)


def homework_to_dict(homework):
    homework_ret = {
        "Exercise" : homework.Exercise,
        "DonePercentage" : homework.DonePercentage,
        "Due" : str(homework.Due),
        "SubHomework" : []
    }
    sub_homework = SubHomeworkLists.query.filter_by(HomeworkListId=homework.id)
    for i in sub_homework:
        homework_ret["SubHomework"].append(sub_homework_to_dict(i))
    return homework_ret


def sub_homework_to_dict(sub_homework):
    return {
        "Exercise" : sub_homework.Exercise,
        "Done" : sub_homework.Done,
        "User" : user_to_dict(Users.query.filter_by(id=sub_homework.UserId).first())
    }

from .db_school import get_school_class_by_user, school_class_to_dict