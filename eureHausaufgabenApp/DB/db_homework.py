from flask import request, g
from datetime import date
import json

from eureHausaufgabenApp.util import file_util

from .db_user import user_to_dict
from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import SubHomeworkLists
from eureHausaufgabenApp.models import HomeworkLists
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
        "Subject" : homework.Subject,
        "SubHomework" : [],
        "id" : homework.id
    }
    sub_homework = SubHomeworkLists.query.filter_by(HomeworkListId=homework.id)
    for i in sub_homework:
        homework_ret["SubHomework"].append(sub_homework_to_dict(i))
    return homework_ret


def sub_homework_to_dict(sub_homework):
    return {
        "Exercise" : sub_homework.Exercise,
        "Done" : sub_homework.Done,
        "User" : user_to_dict(Users.query.filter_by(id=sub_homework.UserId).first()),
        "id" : sub_homework.id
    }


def add_homework(exercise, subject, sub_exercises):
    new_homework_entry = HomeworkLists(Exercise=exercise, DonePercentage=0, Subject=subject, SchoolClassId=get_school_class_by_user().id)
    db.session.add(new_homework_entry)
    db.session.commit()
    for sub_exercise in sub_exercises:
        db.session.add(SubHomeworkLists(Exercise=sub_exercise, Done=False, HomeworkListId=new_homework_entry.id))#
    db.session.commit()
    return 200


def get_sub_homework_from_ids(homework_id, sub_homework_id):
    homework = HomeworkLists.query.filter_by(id=homework_id).first()
    if homework.id == get_school_class_by_user().id:  # check if user is in right class
        sub_homework = SubHomeworkLists.query.filter_by(id=sub_homework_id).first()
        if sub_homework.HomeworkListId == homework.id:
            return sub_homework


def register_user_for_sub_homework(homework_id, sub_homework_id):
    sub_homework = get_sub_homework_from_ids(homework_id, sub_homework_id)
    if sub_homework:
        sub_homework.UserId = g.user.id
        db.session.commit()
        return 200
    return 401


def de_register_user_for_sub_homework(homework_id, sub_homework_id):
    sub_homework = get_sub_homework_from_ids(homework_id, sub_homework_id)
    if sub_homework:
        sub_homework.UserId = None
        db.session.commit()
        return 200
    return 401


def upload_sub_homework(homework_id, sub_homework_id, files):
    sub_homework = get_sub_homework_from_ids(homework_id, sub_homework_id)
    if sub_homework:
        file_util.save_images_in_sub_folder(files, "{}-{}".format(homework_id, sub_homework.id))
        sub_homework.Done = True
        db.session.commit()
        return 200
    return 401



from .db_school import get_school_class_by_user, school_class_to_dict