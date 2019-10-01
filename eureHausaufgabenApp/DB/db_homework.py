from flask import g
from datetime import date
from datetime import datetime

from eureHausaufgabenApp.util import file_util
from eureHausaufgabenApp.util.crypto_util import random_string

from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import SubHomeworkLists
from eureHausaufgabenApp.models import HomeworkLists
from eureHausaufgabenApp.models import Users
from eureHausaufgabenApp.models import UserViewedHomework
from eureHausaufgabenApp.models import ClassReports



def get_school_class_data():
    school_class_dict = get_school_class_dict_by_user()
    if g.user.Role == -1:
        g.data["school_class"] = school_class_dict
        return 200
    remove_past_homework()
    if school_class_dict:
        g.data["school_class"] = school_class_dict
        return 200
    else:
        return 401


def check_if_homework_creator(homework):
    if g.user.id == homework.CreatorId:
        return True
    return False


def get_due_string(date : date):
    if g.user.Role == -1:
        return str(date)
    now = datetime.now().date()
    weeks_between = date.isocalendar()[1] - now.isocalendar()[1]
    if weeks_between == 0:
        days_between = (date - now).days
        if -2 <= days_between <= 2:
            if days_between == -2:
                return "Vorgestern"
            elif days_between == -1:
                return "Gestern"
            elif days_between == 0:
                return "Heute"
            elif days_between == 1:
                return "Morgen"
            elif days_between == 2:
                return "Übermorgen"
    elif weeks_between <= 1:
        day_string = ""
        if weeks_between == 1:
            day_string = "Nächste Woche "

        if date.weekday() == 0:
            day_string += "Montag"
        elif date.weekday() == 1:
            day_string += "Dienstag"
        elif date.weekday() == 2:
            day_string += "Mittwoch"
        elif date.weekday() == 3:
            day_string += "Donnerstag"
        elif date.weekday() == 4:
            day_string += "Freitag"
        elif date.weekday() == 5:
            day_string += "Sammstag ?"
        elif date.weekday() == 6:
            day_string += "Sonntag ?"
        return day_string
    else:
        return str(date)


def remove_past_homework():
    school_class = get_school_class_by_user()
    homework_list = HomeworkLists.query.filter_by(SchoolClassId=school_class.id)
    now = datetime.now().date()
    for homework in homework_list:
        if 0 > (homework.Due-now).days:
            remove_homework(homework)


def remove_sub_homework(sub_homework):
    sub_folder = "{}-{}".format(sub_homework.HomeworkListId, sub_homework.id)
    count = file_util.get_image_count_in_sub_folder(sub_folder)
    if count > 0:
        file_util.remove_sub_folder(sub_folder)
    db.session.delete(sub_homework)
    db.session.commit()

def remove_homework(homework):
    sub_homeworks = SubHomeworkLists.query.filter_by(HomeworkListId=homework.id)
    for sub_homework in sub_homeworks:
        remove_sub_homework(sub_homework)
    view_homework = UserViewedHomework.query.filter_by(HomeworkListId=homework.id)
    for i in view_homework:
        db.session.delete(i)
    reports = ClassReports.query.filter_by(HomeworkListId=homework.id)
    for i in reports:
        delete_reports(i)
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
        "Due" : get_due_string(homework.Due),
        "Subject" : homework.Subject,
        "SubHomework" : [],
        "CreatorId" : homework.CreatorId,
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
        "id" : sub_homework.id,
        "reported" : has_reported_sub_homework(sub_homework)
    }


def add_homework(exercise, subject, sub_exercises, due_date):
    school_class = get_school_class_by_user()
    if school_class.id:
        user_school = get_school_by_user()
        due_date = datetime.strptime(due_date, "%Y-%m-%d")
        new_homework_entry = HomeworkLists(Exercise=exercise, DonePercentage=0, Subject=subject, SchoolClassId=school_class.id, Due=due_date, CreatorId=g.user.id)
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


def get_viewed_homework_by_user(user):
    return UserViewedHomework.query.filter_by(UserId=user.id)


def get_sub_homework_from_id(homework_id, sub_homework_id):
    homework = HomeworkLists.query.filter_by(id=homework_id).first()
    if homework.SchoolClassId == get_school_class_by_user().id:  # check if user is in right class
        sub_homework = SubHomeworkLists.query.filter_by(id=sub_homework_id).first()
        if sub_homework.HomeworkListId == homework.id:
            return sub_homework


def register_user_for_sub_homework(homework_id, sub_homework_id):
    sub_homework = get_sub_homework_from_id(homework_id, sub_homework_id)
    if sub_homework:
        sub_homework.UserId = g.user.id
        db.session.commit()
        return 200
    return 401


def de_register_user_for_sub_homework(homework_id, sub_homework_id):
    sub_homework = get_sub_homework_from_id(homework_id, sub_homework_id)
    if sub_homework:
        if sub_homework.Done:
            g.user.Points -= get_sub_homework_add_points()
            db.session.commit()
        reset_sub_homework(sub_homework)
        return 200
    return 401


def get_all_sub_homework_by_sub_homework(sub_homework):
    return SubHomeworkLists.query.filter_by(HomeworkListId=sub_homework.HomeworkListId)


def get_sub_homework_add_points():
    points = 0
    if g.user.Role == 0:
        points = 10
    elif g.user.Role >= 1:
        points = 15
    return points

def update_homework_done(homework):
    done_count = 0
    items_count = 0
    sub_homework_items = get_all_sub_homework_by_sub_homework(SubHomeworkLists.query.filter_by(HomeworkListId=homework.id).first())
    for i in sub_homework_items:
        items_count += 1
        if i.Done:
            done_count += 1
    homework.DonePercentage = round((done_count / items_count) * 100)
    db.session.commit()


def upload_sub_homework(homework_id, sub_homework_id, files):
    sub_homework = get_sub_homework_from_id(homework_id, sub_homework_id)
    if sub_homework:
        if len(files) > 10:
            return 403
        file_util.save_images_in_sub_folder(files, "{}-{}".format(homework_id, sub_homework.id))
        sub_homework.Done = True
        homework = HomeworkLists.query.filter_by(id=homework_id).first()
        update_homework_done(homework)
        g.user.Points += get_sub_homework_add_points()
        db.session.commit()
        return 200
    return 401


def view_homework(homework_id):
    if g.user.Role == -1:
        return False
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


def get_sub_homework_images_url(homework_id, sub_homework_id):
    sub_homework = get_sub_homework_from_id(homework_id, sub_homework_id)
    if sub_homework:
        viewed_homework = get_viewed_homework_by_homework_id(homework_id)
        if not view_homework(homework_id):
            if not viewed_homework:
                return 403
        sub_folder = "{}-{}".format(sub_homework.HomeworkListId, sub_homework.id)
        random_folder_string = "{0:s}{1:s}".format(sub_folder, random_string(10))
        copy_to_folder = "C:\\xampp\\htdocs\\assets\\{0:s}".format(random_folder_string)
        file_util.copy_sub_images(sub_folder, copy_to_folder)
        image_count_total = file_util.get_image_count_in_sub_folder(sub_folder)
        file_util.delete_temp_sub_image_folder(max(min(image_count_total/4, 30), 10), copy_to_folder) # start thread that waits 10 seconds and then deletes the temp folder
        g.data["images_url"] = "assets\\{0:s}".format(random_folder_string)
        g.data["images_total"] = image_count_total
        return 200
    return 401


def delete_homework(homework_id):
    homework = HomeworkLists.query.filter_by(id=homework_id).first()
    if homework:
        if g.user.Role >= 2:
            remove_homework(homework)
            g.data["success"] = True
            return 200
        elif homework.SchoolClassId == g.user.SchoolClassId:
            if check_if_homework_creator(homework):
                sub_homeworks = SubHomeworkLists.query.filter_by(HomeworkListId=homework.id)
                for sub_homework in sub_homeworks:
                    if sub_homework.Done:
                        g.data["success"] = False
                        return 200
                remove_homework(homework)
                g.data["success"] = True
                return 200
            return 401
        return 403
    return 403


def reset_sub_homework(sub_homework):
    sub_homework.Done = False
    sub_homework.UserId = None
    homework = HomeworkLists.query.filter_by(id=sub_homework.HomeworkListId).first()
    update_homework_done(homework)
    sub_folder = "{}-{}".format(sub_homework.HomeworkListId, sub_homework.id)
    count = file_util.get_image_count_in_sub_folder(sub_folder)
    if count > 0:
        file_util.remove_sub_folder(sub_folder)
    db.session.commit()


from .db_school import get_school_class_by_user, school_class_to_dict, get_school_by_user
from .db_mod import has_reported_sub_homework, delete_reports
from .db_user import user_to_dict