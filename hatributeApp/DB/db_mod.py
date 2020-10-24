from flask import g
from sqlalchemy import and_

from typing import List

from hatributeApp import db, app
from hatributeApp.models import ClassReports
from hatributeApp.models import Users
from hatributeApp.models import UserCoursesLists
from hatributeApp.models import SubHomeworkLists
from hatributeApp.models import Courses


# Removes reports for the specified sub homework.
def delete_reports(sub_homework: SubHomeworkLists):
    reports = sub_homework.Reports
    for i in reports:
        db.session.delete(i)
    db.session.commit()


# Resets sub homework and faces other actions based on the report type and how often and by whom it has be reported.
def sub_homework_report_execution_remove_points_and_delete(report: ClassReports, reported_user: Users, sub_homework: SubHomeworkLists, role: int):
    if report.Type == 0:  # wrong content
        if get_report_type_count(report, 0) >= 2 or role >= 2:
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 1:  # no homework
        if get_report_type_count(report, 1) >= 4 or role >= 2:
            reported_user.Points -= 15
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 2:  # violence
        if get_report_type_count(report, 2) >= 4 or role >= 2:
            reported_user.Points = -999  # instant ban
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 3:  # porn
        if get_report_type_count(report, 3) >= 4 or role >= 2:
            reported_user.Points = -999  # instant ban
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 4:  # both violence and porn
        if get_report_type_count(report, 4) >= 4 or role >= 2:
            reported_user.Points = -999  # instant ban
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)

    if -30 >= reported_user.Points: # ban user if under or equal to -30 Points
        reported_user.Role = -1
        viewed_homework = get_viewed_homework_by_user(reported_user)
        for i in viewed_homework:
            db.session.delete(i)
    db.session.commit()


# Returns the report from the sub homework, that has the highest report type.
def get_most_important_report(sub_homework: SubHomeworkLists) -> ClassReports:
    reports = sub_homework.Reports # type: List[ClassReports]
    most_important_report = None
    for report in reports:
        if most_important_report == None:
            most_important_report = report
        elif report.Type > most_important_report.Type:
            most_important_report = report
    return most_important_report


# Faces action for most important report of specified sub homework.
def sub_homework_report_execution(sub_homework: SubHomeworkLists):
    most_important_report = get_most_important_report(sub_homework)
    user = sub_homework.user
    if most_important_report:
        role = Users.query.filter_by(id=most_important_report.ByUserId).first().Role
        if role > user.Role:
            sub_homework_report_execution_remove_points_and_delete(most_important_report, user, sub_homework, role)


# Creates a report for the specified sub homework.
def report_sub_homework(sub_homework_id: int, report_type: int) -> int:
    sub_homework = get_sub_homework_from_id(sub_homework_id)  #type: SubHomeworkLists
    if sub_homework:
        if g.user.Role == -1:  # if user is banned
            return 200 # fuck off
        user_courses = get_user_courses_by_user()
        if user_courses:
            report = ClassReports(Type=report_type, ByUserId=g.user.id, CourseId=sub_homework.homework_list.course.id, SubHomeworkId=sub_homework_id)
            db.session.add(report)
            db.session.commit()
            sub_homework_report_execution(sub_homework)
            return 200
        return 401
    return 401


# Counts how often a sub homework has been reported for the specified type.
def get_report_type_count(report: ClassReports, report_type: int) -> int:
    reports = ClassReports.query.filter(and_(ClassReports.Type==report_type, ClassReports.SubHomeworkId==report.SubHomeworkId))
    return reports.count()


# Returns if a sub homework has a report referencing it.
def has_reported_sub_homework(sub_homework: SubHomeworkLists) -> bool:
    report = ClassReports.query.filter(and_(ClassReports.SubHomeworkId == sub_homework.id, ClassReports.ByUserId == g.user.id)).first()
    if report:
        return True
    return False


# Returns string representing the type of the specified report.
def report_type_to_string(report: ClassReports) -> str:
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


# Returns dict representing the specified report as a dict.
def get_report_as_dict(report: ClassReports) -> dict:
    report = {
        "type" : report_type_to_string(report),
        "reportCreator" : user_to_dict(get_user_by_id(report.ByUserId)),
        "reportedUser" : user_to_dict(get_user_by_id(get_sub_homework_from_id(report.SubHomeworkId).UserId)),
        "reportSubHomeworkId" : report.SubHomeworkId
    }
    return report


# Gets all reports from the current users courses.
def get_reports() -> int:
    if g.user.Role < 2: # Only mods and admins can look at the reports.
        return 401

    user_courses = get_user_courses_by_user()
    if user_courses:
        reports = []
        for course in user_courses: # type: Courses
            reports.extend(course.Reports)
        reports_dict = []
        for report in reports:
            reports_dict.append(get_report_as_dict(report))
        g.data["reports"] = reports_dict
        return 200
    return 401


# Resets sub homework and faces other action if reported user has a lower role then the current user.
def reset_sub_homework_from_mod(subHomeworkId: int) -> int:
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


# Removes a false report and punishes user who created the report.
def remove_one_false_report_and_punish_user_that_reported(report : ClassReports):
    user_that_reported = report.by_user #type: Users
    if user_that_reported.Role >= g.user.Role:
        pass
    elif report.Type == 1:
        user_that_reported.Points -= 1
    elif report.Type == 2:
        user_that_reported.Points -= 5
    elif report.Type == 3:
        user_that_reported.Points -= 5
    elif report.Type == 4:
        user_that_reported.Points -= 10

    db.session.delete(report)
    db.session.commit()


# Does some checks, figures out report from the "sub_homework_id" and then calls "remove_one_false_report_and_punish_user_that_reported"
def remove_false_report_from_mod(sub_homework_id: int) -> int:
    if not g.user.Role >= 2:
        return 401
    sub_homework = get_sub_homework_from_id(sub_homework_id)
    if sub_homework:
        most_important_report = get_most_important_report(sub_homework)
        if most_important_report:
            reports = ClassReports.query.filter_by(Type=most_important_report.Type, SubHomeworkId=most_important_report.SubHomeworkId)
            for report in reports:
                remove_one_false_report_and_punish_user_that_reported(report)
            return 200
        return 404
    return 404


# Gets a list of users relevant to the current user.
def get_users_data() -> int:
    if not g.user.Role >= 2:
        return 401

    if (user_courses := get_user_courses_by_user()) and g.user.Role == 2:  # if user is mod only use users that are in the same course as the user
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
    elif g.user.Role >= 3: # if user is admin use all users
        users = Users.query.all()
        users_dict_list = []
        for user in users:  # type: Users
            if user.id != g.user.id:
                users_dict_list.append(user_to_dict(user, extended_data=True))
        g.data["users"] = users_dict_list
        return 200
    return 403


# Tries to find a user and remove any number of points from it.
def remove_points(user_id: int, points : int) -> int:
    if not g.user.Role >= 2:
        return 401

    # Find user to remove points from that is in a courses that the current user has.
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


from .db_sub_homework import reset_sub_homework, get_sub_homework_from_id
from .db_homework import get_viewed_homework_by_user
from .db_user import user_to_dict, get_user_by_id
from .db_course import get_user_courses_by_user
