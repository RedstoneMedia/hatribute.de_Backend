from flask import g

from eureHausaufgabenApp.util import crypto_util
from eureHausaufgabenApp import db
from eureHausaufgabenApp.models import Users, Courses
from .db_user import reset_account_for_user, generate_new_first_time_sign_in_toke_for_user, setup_user, remove_deactivated_account


def write_user_changes(user_changed_data : dict) -> int:
    if g.user.Role >= 3:
        user_id = user_changed_data["id"]
        if user_id == None:
            return 400
        user_to_modify = Users.query.filter_by(id=user_id).first()  # type: Users

        if username := user_changed_data["name"]:
            user_to_modify.Username = str(username)
        if school_id := user_changed_data["school_id"]:
            user_to_modify.SchoolId = int(school_id)
        if role := user_changed_data["role"]:
            user_to_modify.Role = int(role)
        if points := user_changed_data["points"]:
            user_to_modify.Points = int(points)
        if stay_logged_in := user_changed_data["stay_logged_in"]:
            user_to_modify.StayLoggedIn = bool(stay_logged_in)

        if bool(user_changed_data["is_active"]) == False:
            reset_account_for_user(user_to_modify)
        db.session.commit()
        return 200
    return 401


def write_course_changes(course_changed_data : dict) -> int:
    if g.user.Role >= 3:
        course_id = course_changed_data["CourseId"]
        if course_id == None:
            return 400
        course_to_modify = Courses.query.filter_by(id=course_id).first()  # type: Courses

        if course_name := course_changed_data["CourseName"]:
            course_to_modify.CourseName = str(course_name)
        if school_id := course_changed_data["SchoolId"]:
            course_to_modify.SchoolId = int(school_id)
        if is_default_course := course_changed_data["IsDefaultCourse"]:
            course_to_modify.IsDefaultCourse = bool(is_default_course)
        db.session.commit()
        return 200
    return 401


def generate_new_token_for_deactivated_user(user_id : int):
    if g.user.Role >= 3:
        user_to_modify = Users.query.filter_by(id=user_id).first()  # type: Users
        if user_to_modify.HashedPwd == None:
            g.data["new_first_time_sign_in_token"] = generate_new_first_time_sign_in_toke_for_user(user_to_modify)
            return 200
        else:
            return 403
    return 401


def setup_new_user(user_name : str, school_name : str):
    if g.user.Role >= 3:
        error_code = setup_user(user_name, school_name)
        if error_code == 404:
            return 200
        return error_code
    return 401


def remove_deactivated_user(user_id : int):
    if g.user.Role >= 3:
        return remove_deactivated_account(user_id)
    return 401