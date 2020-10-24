import json
from typing import Tuple, Union

from flask import g
from sqlalchemy import and_

from hatributeApp import Users, db, app
from hatributeApp.util import crypto_util

# Gets the current users data represented as dict
def get_user_data():
    g.data["user"] = user_to_dict(g.user)


def get_user_by_id(user_id):
    return Users.query.filter_by(id=user_id).first()


# Returns a dict containing some of the attributes of the specified user.
def user_to_dict(user : Users, extended_data=False) -> dict:
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
            "stay_logged_in": g.session_db_object.StayLoggedIn
        }
    return  {
        "id" : user.id,
        "name": str(user.Username),
        "role": user.Role,
        "points" : user.Points,
        "stay_logged_in": g.session_db_object.StayLoggedIn
    }


# Resets a user by setting the password to None and removing all courses from that user
def reset_account_for_user(user : Users):
    app.logger.info(f"Account is being reset for User with name '{user.Username}'")
    user.HashedPwd = None
    db.session.commit()
    remove_all_courses_from_user(user)


# Resets the current user
def reset_account():
    reset_account_for_user(g.user)


# Tries to remove a account, but only if it has no set password.
def remove_deactivated_account(user_id : int) -> int:
    user = get_user_by_id(user_id) # type: Users
    if user:
        if user.HashedPwd == None:
            db.session.delete(user)
            db.session.commit()
        else:
            return 403  # Account is not deactivated
    else:
        return 404


# Generates a 200 long string and sets that as the sign in token.
def generate_new_first_time_sign_in_toke_for_user(user : Users):
    user.FirstTimeSignInToken = crypto_util.random_string(200)
    db.session.commit()
    return user.FirstTimeSignInToken


# Creates a deactivated user bound to a specific school
def setup_user(user_name : str, school_name : str, use_g_data=True) -> Tuple[int, Union[dict, None]]:
    school = get_school_by_name(school_name)
    if school:
        if Users.query.filter_by(Username=user_name).first() == None:
            new_user = Users(Username=user_name, SchoolId=school.id)
            db.session.add(new_user)
            data = {
                "new_first_time_sign_in_token": generate_new_first_time_sign_in_toke_for_user(new_user),
                "new_user_id": new_user.id
            }
            if use_g_data:
                g.data = data
                return 200, None
            return 200, data
        data = {"user_already_exists" : True}
        if use_g_data:
            g.data = data
            return 200, None
        return 200, data
    else:
        return 404, None


# Activates a deactivated user.
def create_user(user_name: str, school_name: str, password: str, first_time_sign_in_token: str) -> Tuple[str, int]:
    school = get_school_by_name(school_name)
    name_and_not_active = Users.query.filter(and_(Users.Username == user_name, Users.HashedPwd == None, Users.FirstTimeSignInToken == first_time_sign_in_token)).first()  # type: Users

    if not len(password) > 6:
        return "Forbidden Password must be at least 7 characters long", 403

    # check if school is set (you need to set this before you can create a account)
    # check if the name is already set up (you need to set this before you can create a account)
    if school != None and name_and_not_active != None and password != None:
        name_and_not_active.FirstTimeSignInToken = None
        hashed_password = crypto_util.hash_pwd(password)
        name_and_not_active.HashedPwd = hashed_password
        name_and_not_active.StayLoggedIn = False
        if name_and_not_active.Role != -1 and name_and_not_active.Role != 4:
            name_and_not_active.Role = 0
            name_and_not_active.Points = 20
        add_default_courses_to_user(name_and_not_active)
        db.session.commit()
        app.logger.info(f"Account was created for user with the name '{user_name}'")
        return json.dumps({"User-created" : True}), 200
    else:
        app.logger.info(f"Account was not setup, because the account information was not valid")
        return "Forbidden", 403

from .db_school import get_school_by_name
from .db_course import add_default_courses_to_user, remove_all_courses_from_user