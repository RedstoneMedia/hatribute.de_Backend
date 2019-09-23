from flask import g
from sqlalchemy import and_

from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import ClassReports
from eureHausaufgabenApp.models import Users


def delete_reports(sub_homework):
    reports = ClassReports.query.filter_by(SubHomeworkId=sub_homework.id)
    for i in reports:
        db.session.delete(i)
    db.session.commit()


def sub_homework_report_execution_remove_points_and_delete(report, reportedUser, sub_homework, role):
    if report.Type == 0:  # wrong content
        if report.Count > 4 or role >= 2:
            reportedUser.Points -= 5
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 1:  # no homework
        if report.Count > 4 or role >= 2:
            reportedUser.Points -= 15
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 2:  # violence
        if report.Count > 4 or role >= 2:
            reportedUser.Points = -999  # instant ban
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 3:  # porn
        if report.Count > 4 or role >= 2:
            reportedUser.Points = -999  # instant ban
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)
    elif report.Type == 3:  # both violence and porn
        if report.Count > 4 or role >= 2:
            reportedUser.Points = -999  # instant ban
            reset_sub_homework(sub_homework)
            delete_reports(sub_homework)

    if -30 >= reportedUser.Points: # ban user if under or equal to -30 Points
        reportedUser.Role = -1
    db.session.commit()


def get_most_important_report(sub_homework):
    reports = ClassReports.query.filter_by(SubHomeworkId=sub_homework.id)
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



def report_sub_homework(homework_id, sub_homework_id, type):
    sub_homework = get_sub_homework_from_id(homework_id, sub_homework_id)
    if sub_homework:
        if g.user.Role == -1:
            return 200 # fuck of
        report = ClassReports.query.filter(and_(ClassReports.Type == type, ClassReports.SubHomeworkId == sub_homework_id)).first()
        if report:
            if report.ByUserId != g.user.id:
                report.Count += 1
                db.session.commit()
                sub_homework_report_execution(sub_homework)
                return 200
            return 403
        school_class = get_school_class_by_user()
        if school_class:
            report = ClassReports(Type=type, Count=1, ByUserId=g.user.id, SchoolClassId=school_class.id, HomeworkListId=homework_id, SubHomeworkId=sub_homework_id)
            db.session.add(report)
            db.session.commit()
            sub_homework_report_execution(sub_homework)
            return 200
        return 401
    return 401


def has_reported_sub_homework(sub_homework):
    report = ClassReports.query.filter(and_(ClassReports.SubHomeworkId == sub_homework.id, ClassReports.ByUserId ==g.user.id)).first()
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
        "count" : report.Count,
        "reportCreator" : user_to_dict(get_user_by_id(report.ByUserId)),
        "reportedUser" : user_to_dict(get_user_by_id(get_sub_homework_from_id(report.HomeworkListId, report.SubHomeworkId).UserId)),
        "reportSubHomeworkId" : report.SubHomeworkId,
        "reportHomeworkId" : report.HomeworkListId
    }
    return report


def get_reports():
    if not g.user.Role >= 2:
        return 401
    school_class = get_school_class_by_user()
    if school_class:
        reports = ClassReports.query.filter_by(SchoolClassId=school_class.id)
        reports_dict = []
        for report in reports:
            reports_dict.append(get_report_as_dict(report))
        g.data["reports"] = reports_dict
        return 200
    return 401


def reset_sub_homework_from_mod(homeworkId, subHomeworkId):
    if not g.user.Role >= 2:
        return 401
    sub_homework = get_sub_homework_from_id(homeworkId, subHomeworkId)
    if sub_homework:
        user = get_user_by_id(sub_homework.UserId)
        most_important_report = get_most_important_report(sub_homework)
        if most_important_report:
            sub_homework_report_execution_remove_points_and_delete(most_important_report, user, sub_homework, g.user.Role)
            return 200
        return 400
    return 401


from .db_homework import get_sub_homework_from_id, reset_sub_homework
from .db_school import get_school_class_by_user
from .db_user import user_to_dict, get_user_by_id