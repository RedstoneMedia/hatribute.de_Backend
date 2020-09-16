import json

from flask import g
from sqlalchemy import and_

from eureHausaufgabenApp import Users, db, app
from eureHausaufgabenApp.util import crypto_util


def get_user_data():
    user = g.user
    session_data = g.data
    session_data["user"] = user_to_dict(user)
    g.data = session_data


def get_user_by_id(user_id):
    return Users.query.filter_by(id=user_id).first()


def user_to_dict(user : Users, extended_data=False):
    if user == None:
        return {
            "id" : None,
            "name": None,
            "role": None,
            "points" : None,
            "stay_logged_in" : None
        }
    if extended_data:
        return {
            "id": user.id,
            "name": str(user.Username),
            "role": user.Role,
            "points": user.Points,
            "school_id": user.SchoolId,
            "is_active": user.HashedPwd != None,
            "stay_logged_in": user.StayLoggedIn
        }
    return  {
        "id" : user.id,
        "name": str(user.Username),
        "role": user.Role,
        "points" : user.Points,
        "stay_logged_in": user.StayLoggedIn
    }

def reset_account_for_user(user : Users):
    app.logger.info(f"Account is being reset for User with email '{user.Email}' and name '{user.Username}'")
    user.Email = None
    user.HashedPwd = None
    db.session.commit()
    remove_all_courses_from_user(user)


def reset_account():
    reset_account_for_user(g.user)


def remove_deactivated_account(user_id : int):
    user = get_user_by_id(user_id)
    if user:
        if user.HashedPwd == None:
            db.session.delete(user)
            db.session.commit()
        else:
            return 403
    else:
        return 404


def generate_new_first_time_sign_in_toke_for_user(user : Users):
    user.FirstTimeSignInToken = crypto_util.random_string(200)
    db.session.commit()
    return user.FirstTimeSignInToken


def setup_user(user_name : str, school_name : str):
    school = get_school_by_name(school_name)
    if school:
        new_user = Users(Username=user_name, SchoolId=school.id)
        db.session.add(new_user)
        g.data["new_first_time_sign_in_token"] = generate_new_first_time_sign_in_toke_for_user(new_user)
        g.data["new_user_id"] = new_user.id
    else:
        return 404


def create_user(email, name, school_name, password, first_time_sign_in_token):
    school = get_school_by_name(school_name)
    email_already_used = Users.query.filter_by(Email=email).first()
    name_and_not_active = Users.query.filter(and_(Users.Username == name, Users.HashedPwd == None, Users.FirstTimeSignInToken == first_time_sign_in_token)).first()  # type: Users

    if not len(password) > 6:
        return "Forbidden Password must be at least 7 characters long", 403

    # check if school is set (you need to set this before you can create a account)
    # check if the email has not been used yet
    # check if the name is already set up (you need to set this before you can create a account)
    if school != None and email_already_used == None and name_and_not_active != None and password != None:
        name_and_not_active.Email = email
        name_and_not_active.FirstTimeSignInToken = None
        hashed_password = crypto_util.hash_pwd(password)
        name_and_not_active.HashedPwd = hashed_password
        name_and_not_active.StayLoggedIn = False
        if name_and_not_active.Role != -1:
            name_and_not_active.Role = 0
            name_and_not_active.Points = 20
        add_default_courses_to_user(name_and_not_active)
        db.session.commit()
        app.logger.info(f"Account was created for user with the name '{name}' with email '{email}'")
        return json.dumps({"User-created" : True}), 200
    else:
        app.logger.info(f"Account was not setup because the account information was not right")
        return "Forbidden", 403

from .db_school import get_school_by_name
from .db_course import add_default_courses_to_user, remove_all_courses_from_user