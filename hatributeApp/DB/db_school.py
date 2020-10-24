from flask import g
from hatributeApp.models import Schools, Users, Courses
from typing import List
from hatributeApp import db

def get_school_by_user():
    return g.user.school

def get_school_by_id(school_id : int) -> Schools:
    return Schools.query.filter_by(id=school_id).first()

def get_school_by_name(school_name : str) -> Schools:
    return Schools.query.filter_by(Name=school_name).first()

# Returns the specified schools name and id in a dict
def school_to_dict(school : Schools) -> dict:
    return {
        "id" : school.id,
        "name" : school.Name
    }

# Returns a List of dicts representing all schools
def get_all_schools() -> List[dict]:
    schools = []
    for school in Schools.query.all():
        schools.append(school_to_dict(school))
    return schools


# Tries to remove a school. This will remove all courses and users that are bound to that school
def remove_school_by_id(school_id: int) -> int:
    school = get_school_by_id(school_id)
    if school:
        for user in school.Users: # type: Users
            if user.HashedPwd != None:
                reset_account_for_user(user)
            remove_deactivated_account(user.id)
        for course in school.Courses: # type: Courses
            if course:
                db.session.delete(course)
                db.session.commit()
                return 200
            return 404
        Schools.query.filter_by(id=school_id).delete(synchronize_session="fetch")
        db.session.commit()


# Tries to add a school with a specified name.
def add_school(school_name: str):
    if get_school_by_name(school_name) == None:
        db.session.add(Schools(Name=school_name))
        db.session.commit()


from hatributeApp.DB.db_user import reset_account_for_user, remove_deactivated_account