from flask import g
from sqlalchemy import and_

from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import ClassReports
from eureHausaufgabenApp.models import Users
from eureHausaufgabenApp.models import UserCoursesLists
from eureHausaufgabenApp.models import SubHomeworkLists
from eureHausaufgabenApp.models import Courses


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
        if role > user.Role:
            sub_homework_report_execution_remove_points_and_delete(most_important_report, user, sub_homework, role)


def report_sub_homework(sub_homework_id, type):
    sub_homework = get_sub_homework_from_id(sub_homework_id)  #type: SubHomeworkLists
    if sub_homework:
        if g.user.Role == -1:  # if user is banned
            return 200 # fuck off
        user_courses = get_user_courses_by_user()
        if user_courses:
            report = ClassReports(Type=type, ByUserId=g.user.id, CourseId=sub_homework.homework_list.course.id, SubHomeworkId=sub_homework_id)
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
    user_courses = get_user_courses_by_user()
    if user_courses:
        reports = []
        for course in user_courses: #type: Courses
            reports.extend(course.Reports)
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
        if user.Role < g.user.Role:
            most_important_report = get_most_important_report(sub_homework)
            if most_important_report:
                sub_homework_report_execution_remove_points_and_delete(most_important_report, user, sub_homework, g.user.Role)
                return 200
            return 400
        return 401
    return 401


def get_users_data():
    if not g.user.Role >= 2:
        return 401


    if (user_courses := get_user_courses_by_user()) and g.user.Role == 2:
        users = []
        for course in user_courses: #type: Courses
            for usersCourseList in UserCoursesLists.query.filter_by(CourseId=course.id):  #type: UserCoursesLists
                users.append(usersCourseList.user)
        users_dict_list = []
        for user in users: # type: Users
            if user.id != g.user.id and user.HashedPwd != None:
                users_dict_list.append(user_to_dict(user))
        g.data["users"] = users_dict_list
        return 200
    elif g.user.Role >= 3:
        users = Users.query.all()
        users_dict_list = []
        for user in users:  # type: Users
            if user.id != g.user.id:
                users_dict_list.append(user_to_dict(user, extended_data=True))
        g.data["users"] = users_dict_list
        return 200
    return 403


def remove_points(user_id, points):
    if not g.user.Role >= 2:
        return 401

    user_to_remove_points_from = None
    if user_courses := get_user_courses_by_user():
        for course in user_courses:  # type: Courses
            if user_courses_list_entry := UserCoursesLists.query.filter_by(CourseId=course.id, UserId=user_id).first(): #type: UserCoursesLists
                if user_courses_list_entry.user.Role < g.user.Role:
                    user_to_remove_points_from = user_courses_list_entry.user
                    break
    if not user_to_remove_points_from:
        return 403
    if user_to_remove_points_from.id == g.user.id:
        return 401
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


from .db_homework import reset_sub_homework, get_sub_homework_from_id, get_viewed_homework_by_user
from .db_course import get_user_courses_by_user
from .db_user import user_to_dict, get_user_by_id