from typing import Tuple, List

from flask import g
from datetime import date
from datetime import datetime

from hatributeApp import db, app
from hatributeApp.models import SubHomeworkLists
from hatributeApp.models import HomeworkLists
from hatributeApp.models import Users
from hatributeApp.models import UserViewedHomework
from hatributeApp.models import ClassReports
from hatributeApp.models import UserCoursesLists
from hatributeApp.models import Courses


# Checks if the current user is the creator of the specified homework.
def check_if_homework_creator(homework: HomeworkLists):
    if g.user.id == homework.CreatorId:
        return True
    return False


# Returns how urgent the homework needs to be finished based on the remaining days.
def get_urgent_level(days_between: int):
    if days_between < 0:
        return -1
    elif days_between == 0:
        return 4
    elif days_between == 1:
        return 3
    elif days_between == 2:
        return 2
    elif days_between == 3:
        return 1
    else:
        return 0


# Returns the formatted date to be displayed in the frontend. It also returns the urgent level
def get_due_string(date : date) -> Tuple[str, int]:
    # Users with this role shall be punished by
    if g.user.Role == -1:
        return str(date), 0

    now = datetime.now().date()
    weeks_between = date.isocalendar()[1] - now.isocalendar()[1]
    if weeks_between == 0: # Dates are not more than 1 week apart.
        days_between = (date - now).days
        urgent_level = get_urgent_level(days_between)
        if -2 <= days_between <= 2:
            if days_between == -2:
                return "Vorgestern", urgent_level
            elif days_between == -1:
                return "Gestern", urgent_level
            elif days_between == 0:
                return "Heute", urgent_level
            elif days_between == 1:
                return "Morgen", urgent_level
            elif days_between == 2:
                return "Übermorgen", urgent_level
        return "", urgent_level
    elif weeks_between <= 1: # Dates are more than one week apart.
        days_between = (date - now).days
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
            day_string += "Sammstag 😯"
        elif date.weekday() == 6:
            day_string += "Sonntag 😯"
        return day_string, get_urgent_level(days_between)
    else:
        return str(date), 0


# Removes all past homework that are in the courses of the current user
def remove_past_homework():
    courses = get_user_courses_by_user()
    for course in courses:
        homework_list = course.HomeworkList
        now = datetime.now().date()
        for homework in homework_list:
            if 0 > (homework.Due-now).days:
                remove_homework(homework)



# Removes a homework including all sub homework, reports and records that the homework has been viewed.
def remove_homework(homework: HomeworkLists):
    sub_homeworks = homework.SubHomework
    for sub_homework in sub_homeworks:
        remove_sub_homework(sub_homework)
    view_homework = homework.UserViewedHomework
    for i in view_homework:
        db.session.delete(i)
    reports = homework.Reports
    for i in reports:
        delete_reports(i)
    db.session.delete(homework)
    db.session.commit()


# Converts a homework including all sub homework into a dict.
def homework_to_dict(homework: HomeworkLists):
    due_string, urgent_level = get_due_string(homework.Due)
    homework_ret = {
        "Exercise" : homework.Exercise,
        "DonePercentage" : homework.DonePercentage,
        "Due" : due_string,
        "UrgentLevel" : urgent_level,
        "SubHomework" : [],
        "CreatorId" : homework.CreatorId,
        "CourseId": homework.CourseId,
        "id" : homework.id,
        "Viewed" : False
    }
    if get_viewed_homework_by_homework_id(homework.id):
        homework_ret["Viewed"] = True
    sub_homework = homework.SubHomework
    for i in sub_homework:
        homework_ret["SubHomework"].append(sub_homework_to_dict(i))
    return homework_ret



# Adds a homework to a specified course.
def add_homework(exercise: str, course_id: int, sub_exercises: List[str], due_date: str) -> int:
    user_course_list_item = UserCoursesLists.query.filter_by(CourseId=course_id, UserId=g.user.id).first()  # type: UserCoursesLists
    if user_course_list_item != None:
        course = user_course_list_item.course # type: Courses
        due_date = datetime.strptime(due_date, "%Y-%m-%d")
        new_homework_entry = HomeworkLists(Exercise=exercise, DonePercentage=0, CourseId=course.id, Due=due_date, CreatorId=g.user.id)
        db.session.add(new_homework_entry)
        db.session.commit()
        for sub_exercise in sub_exercises:
            db.session.add(SubHomeworkLists(Exercise=sub_exercise, Done=False, HomeworkListId=new_homework_entry.id))
        db.session.commit()
        return 200
    else:
        return 401


def get_viewed_homework_by_homework_id(homework_id: int) -> UserViewedHomework:
    return UserViewedHomework.query.filter_by(HomeworkListId=homework_id, UserId=g.user.id).first()


def get_viewed_homework_by_user(user: Users) -> List[UserViewedHomework]:
    return user.UserViewedHomework


# Updates the done percentage for the specified homework.
def update_homework_done(homework: HomeworkLists):
    done_count = 0
    items_count = 0
    sub_homework_items = homework.SubHomework
    for i in sub_homework_items:
        items_count += 1
        if i.Done:
            done_count += 1
    homework.DonePercentage = round((done_count / items_count) * 100)
    db.session.commit()



# Checks if the current user can view the specified homework.
def view_homework(homework_id : int, viewed_homework: UserViewedHomework) -> bool:
    if g.user.Role == -1: # Users with this role shall be punished by
        return False
    if g.user.Points < 5: # User has to little points to view the homework.
        return False
    if g.user.Role < 0:
        return False

    if not viewed_homework: # Homework has not been viewed by that user yet.
        # Create and add new UserViewedHomework to the database.
        viewed_homework = UserViewedHomework(UserId=g.user.id, HomeworkListId=homework_id)
        db.session.add(viewed_homework)
        if not g.user.Role >= 2:  # Admins and mods should be able to look at all images to see if they contain bad data.
            g.user.Points -= 5  # Subtract points from user for viewing homework.
        db.session.commit()
    return True


# Deletes a homework based on its id. Does some checks and then calls "remove_homework".
def delete_homework(homework_id: int) -> int:
    homework = HomeworkLists.query.filter_by(id=homework_id).first()
    if homework:
        if g.user.Role >= 2: # Mods and admins can always delete
            remove_homework(homework)
            g.data["success"] = True
            return 200
        user_courses = get_user_courses_by_user()
        if user_courses:
            if is_course_id_in_courses(user_courses, homework.CourseId):
                if check_if_homework_creator(homework):
                    sub_homeworks = homework.SubHomework

                    # Forbid user from deleting homework if anny images have been uploaded.
                    for sub_homework in sub_homeworks:
                        if sub_homework.Done:
                            g.data["success"] = False
                            return 200

                    remove_homework(homework)
                    g.data["success"] = True
                    return 200
                return 403
            return 403
        return 403
    return 400

from .db_course import is_course_id_in_courses, get_user_courses_by_user
from .db_sub_homework import remove_sub_homework, sub_homework_to_dict
from .db_mod import delete_reports