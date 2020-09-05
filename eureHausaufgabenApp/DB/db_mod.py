from flask import g
from sqlalchemy import and_

from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import ClassReports
from eureHausaufgabenApp.models import Users
from eureHausaufgabenApp.models import SubHomeworkLists
from eureHausaufgabenApp.models import SchoolClasses


def delete_reports(sub_homework: SubHomeworkLists):
    reports = sub_homework.Reports
    for i in reports:
        db.session.delete(i)
    db.session.commit()


def sub_homework_report_execution_remove_points_and_delete(report, reportedUser, sub_homework, role):
    if report.Type == 0:  # wrong content
        if get_report_type_count(report, 0) >= 2 or role >= 2:
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 1:  # no homework
        if get_report_type_count(report, 1) >= 4 or role >= 2:
            reportedUser.Points -= 15
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 2:  # violence
        if get_report_type_count(report, 2) >= 4 or role >= 2:
            reportedUser.Points = -999  # instant ban
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 3:  # porn
        if get_report_type_count(report, 3) >= 4 or role >= 2:
            reportedUser.Points = -999  # instant ban
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 4:  # both violence and porn
        if get_report_type_count(report, 4) >= 4 or role >= 2:
            reportedUser.Points = -999  # instant ban
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)

    if -30 >= reportedUser.Points: # ban user if under or equal to -30 Points
        reportedUser.Role = -1
        viewed_homework = get_viewed_homework_by_user(reportedUser)
        for i in viewed_homework:
            db.session.delete(i)
    db.session.commit()


def get_most_important_report(sub_homework: SubHomeworkLists):
    reports = sub_homework.Reports
    most_important_reports = None
    for report in reports:
        if not most_important_reports:
            most_important_reports = report
        elif report.Type > most_important_reports.Type:
            most_important_reports = report
    return most_important_reports


def sub_homework_report_execution(sub_homework):
    most_important_report = get_most_important_report(sub_homework)
    user = get_user_by_id(sub_homework.UserId)
    if most_important_report:
        role = Users.query.filter_by(id=most_important_report.ByUserId).first().Role
        sub_homework_report_execution_remove_points_and_delete(most_important_report, user, sub_homework, role)


def report_sub_homework(sub_homework_id, type):
    sub_homework = get_sub_homework_from_id(sub_homework_id)
    if sub_homework:
        if g.user.Role == -1:  # if user is banned
            return 200 # fuck of
        school_class = get_school_class_by_user()
        if school_class:
            report = ClassReports(Type=type, ByUserId=g.user.id, SchoolClassId=school_class.id, SubHomeworkId=sub_homework_id)
            db.session.add(report)
            db.session.commit()
            sub_homework_report_execution(sub_homework)
            return 200
        return 401
    return 401


def get_report_type_count(report, type):
    reports = ClassReports.query.filter(and_(ClassReports.Type==type, ClassReports.SubHomeworkId==report.SubHomeworkId))
    return reports.count()


def has_reported_sub_homework(sub_homework):
    report = ClassReports.query.filter(and_(ClassReports.SubHomeworkId == sub_homework.id, ClassReports.ByUserId == g.user.id)).first()
    if report:
        return True
    return False


def report_type_to_string(report):
    if report.Type == 0:
        return "Falsch"
    elif report.Type == 1:
        return "Keine Hausaufgabe"
    elif report.Type == 2:
        return "Gewallt"
    elif report.Type == 3:
        return "Pornographie"
    elif report.Type == 4:
        return "Gewallt und Pornographie"


def get_report_as_dict(report):
    report = {
        "type" : report_type_to_string(report),
        "reportCreator" : user_to_dict(get_user_by_id(report.ByUserId)),
        "reportedUser" : user_to_dict(get_user_by_id(get_sub_homework_from_id(report.SubHomeworkId).UserId)),
        "reportSubHomeworkId" : report.SubHomeworkId
    }
    return report


def get_reports():
    if g.user.Role < 2:
        return 401
    school_class = get_school_class_by_user()  # type: SchoolClasses
    if school_class:
        reports = school_class.Reports
        reports_dict = []
        for report in reports:
            reports_dict.append(get_report_as_dict(report))
        g.data["reports"] = reports_dict
        return 200
    return 401


def reset_sub_homework_from_mod(subHomeworkId):
    if not g.user.Role >= 2:
        return 401
    sub_homework = get_sub_homework_from_id(subHomeworkId)
    if sub_homework:
        user = get_user_by_id(sub_homework.UserId)
        most_important_report = get_most_important_report(sub_homework)
        if most_important_report:
            sub_homework_report_execution_remove_points_and_delete(most_important_report, user, sub_homework, g.user.Role)
            return 200
        return 400
    return 401


def get_users_data():
    if not g.user.Role >= 2:
        return 401
    users = Users.query.filter_by(SchoolClassId=g.user.SchoolClassId)
    users_dict_list = []
    for user in users:
        if user.id != g.user.id and user.HashedPwd != None:
            users_dict_list.append(user_to_dict(user))
    g.data["users"] = users_dict_list
    return 200


def remove_points(user_id, points):
    if not g.user.Role >= 2:
        return 401

    user_to_remove_points_from = get_user_by_id(user_id)
    if user_to_remove_points_from.id == g.user.id:
        return 401
    if is_user_in_users_school(g.user, user_to_remove_points_from):
        user_to_remove_points_from.Points -= int(points)
        if -30 >= user_to_remove_points_from.Points:  # ban user if under or equal to -30 Points
            user_to_remove_points_from.Role = -1
            viewed_homework = get_viewed_homework_by_user(user_to_remove_points_from)
            for i in viewed_homework:
                db.session.delete(i)
        elif user_to_remove_points_from.Role == -1:  # un ban user if above -30 points
            user_to_remove_points_from.Role = 0
        db.session.commit()
        return 200
    return 401


from .db_homework import reset_sub_homework, get_sub_homework_from_id, get_viewed_homework_by_user
from .db_school import get_school_class_by_user, is_user_in_users_school
from .db_user import user_to_dict, get_user_by_id