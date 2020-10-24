from flask import g

from hatributeApp import db
from hatributeApp.models import Users, Courses
from .db_user import reset_account_for_user, generate_new_first_time_sign_in_toke_for_user, setup_user, remove_deactivated_account


# Writes dict containing changes for the specified user id.
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


# Writes dict containing changes for the specified course id.
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


# Writes dict containing changes for the specified school id.
def write_school_changes(school_changed_data : dict) -> int:
    if g.user.Role >= 3:
        school_id = school_changed_data["id"]
        if school_id == None:
            return 400
        school_to_modify = db_school.get_school_by_id(school_id) # type: Courses

        if school_name := school_changed_data["name"]:
            school_to_modify.Name = str(school_name)
        db.session.commit()
        return 200
    return 401


# Generates a fresh new first time sign in toke for a deactivated user.
def generate_new_token_for_deactivated_user(user_id : int) -> int:
    if g.user.Role >= 3:
        user_to_modify = Users.query.filter_by(id=user_id).first()  # type: Users
        if user_to_modify.HashedPwd == None:
            g.data["new_first_time_sign_in_token"] = generate_new_first_time_sign_in_toke_for_user(user_to_modify)
            return 200
        else:
            return 403
    return 401


# Checks if user is a admin and then sets up the user with the specified name and school name
def setup_new_user(user_name : str, school_name : str) -> int:
    if g.user.Role >= 3:
        error_code = setup_user(user_name, school_name)[0]
        if error_code == 404:
            return 200
        return error_code
    return 401


# Checks if user is admin and then calls "remove_deactivated_account"
def remove_deactivated_user(user_id : int) -> int:
    if g.user.Role >= 3:
        return remove_deactivated_account(user_id)
    return 401


# Checks if user is admin and then calls "get_all_schools"
def get_all_schools() -> int:
    if g.user.Role >= 3:
        g.data["schools"] = db_school.get_all_schools()
        return 200
    return 401


# Checks if user is admin and then calls "add_school"
def add_school(school_name : str) -> int:
    if g.user.Role >= 3:
        db_school.add_school(school_name)
        return 200
    return 401


# Checks if user is admin and then calls "remove_school_by_id"
def remove_school(school_id : int) -> int:
    if g.user.Role >= 3:
        db_school.remove_school_by_id(school_id)
        return 200
    return 401

from hatributeApp.DB import db_school