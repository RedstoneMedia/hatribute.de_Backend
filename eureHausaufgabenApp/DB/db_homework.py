from flask import request, g
from datetime import date
import json
from datetime import datetime

from eureHausaufgabenApp.util import file_util
# from eureHausaufgabenApp.util import timetable_util

from .db_user import user_to_dict
from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import SubHomeworkLists
from eureHausaufgabenApp.models import HomeworkLists
from eureHausaufgabenApp.models import Users
from eureHausaufgabenApp.models import UserViewedHomework


def get_school_class_data():
    remove_past_homework()
    school_class_dict = get_school_class_dict_by_user()
    if school_class_dict:
        g.data["school_class"] = school_class_dict
        return 200
    else:
        return 401


def remove_past_homework():
    school_class = get_school_class_by_user()
    homework_list = HomeworkLists.query.filter_by(SchoolClassId=school_class.id)
    now = datetime.now().date()
    for homework in homework_list:
        if (homework.Due-now).days < 1:
            db.session.delete(homework)
            db.session.commit()


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
        "id" : homework.id,
        "Viewed" : False
    }
    if get_viewed_homework_by_homework_id(homework.id):
        homework_ret["Viewed"] = True
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


def add_homework(exercise, subject, sub_exercises, due_date):
    school_class = get_school_class_by_user()
    if school_class.id:
        user_school = get_school_by_user()
        due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")
        new_homework_entry = HomeworkLists(Exercise=exercise, DonePercentage=0, Subject=subject, SchoolClassId=school_class.id, Due=due_date)
        db.session.add(new_homework_entry)
        db.session.commit()
        for sub_exercise in sub_exercises:
            db.session.add(SubHomeworkLists(Exercise=sub_exercise, Done=False, HomeworkListId=new_homework_entry.id))
        db.session.commit()
        return 200
    else:
        return 401


def get_viewed_homework_by_homework_id(homework_id):
    return UserViewedHomework.query.filter_by(HomeworkListId=homework_id, UserId=g.user.id).first()


def get_sub_homework_from_ids(homework_id, sub_homework_id):
    homework = HomeworkLists.query.filter_by(id=homework_id).first()
    if homework.SchoolClassId == get_school_class_by_user().id:  # check if user is in right class
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


def get_all_sub_homework_by_sub_homework(sub_homework):
    return SubHomeworkLists.query.filter_by(HomeworkListId=sub_homework.HomeworkListId)


def upload_sub_homework(homework_id, sub_homework_id, files):
    sub_homework = get_sub_homework_from_ids(homework_id, sub_homework_id)
    if sub_homework:
        file_util.save_images_in_sub_folder(files, "{}-{}".format(homework_id, sub_homework.id))
        done_count = 0
        items_count = 0
        sub_homework.Done = True
        sub_homework_items = get_all_sub_homework_by_sub_homework(sub_homework)
        for i in sub_homework_items:
            items_count += 1
            if i.Done:
                done_count += 1
        homework = HomeworkLists.query.filter_by(id=homework_id).first()
        homework.DonePercentage = round((done_count / items_count) * 100)
        if g.user.Role == 0:
            g.user.Points += 10
        elif g.user.Role >= 1:
            g.user.Points += 15
        db.session.commit()
        return 200
    return 401


def view_homework(homework_id):
    if g.user.Points < 5:
        return False
    if g.user.Role < 0:
        return False
    viewed_homework = UserViewedHomework(UserId=g.user.id, HomeworkListId=homework_id)
    db.session.add(viewed_homework)
    if not g.user.Role >= 2:
        g.user.Points -= 5
    db.session.commit()
    return True


def get_sub_homework_images_as_base64(homework_id, sub_homework_id):
    sub_homework = get_sub_homework_from_ids(homework_id, sub_homework_id)
    if sub_homework:
        viewed_homework = get_viewed_homework_by_homework_id(homework_id)
        if not viewed_homework:
            if not view_homework(homework_id):
                return 403
        sub_folder = "Homework\\{}-{}".format(sub_homework.HomeworkListId, sub_homework.id)
        g.data["base64_images"] = file_util.get_images_in_sub_folder_as_base64(sub_folder)
        return 200
    return 401


"""
def get_time_table(units_username, units_password):
    school_class = get_school_class_by_user()
    if school_class.id:
        user_school = get_school_by_user()
        timetable_util.get_time_table(units_school_name=user_school.UnitsSchoolName, user_name=units_username, user_password=units_password, save_file="Timetables\\{}_{}.json".format(user_school.id, school_class.id))
        return 200
    else:
        return 401

def get_time_table_download_info():
    school_class = get_school_class_by_user()
    if school_class.id:
        user_school = get_school_by_user()
        info = timetable_util.get_time_table_download_info(save_file="Timetables\\{}_{}.json".format(user_school.id, school_class.id))
        if info == "DONE":
            g.user.Points += 5
            db.session.commit()
        g.data["download_info"] = info
        return 200
    else:
        return 401
"""

from .db_school import get_school_class_by_user, school_class_to_dict, get_school_by_user