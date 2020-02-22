import json

from flask import g
from sqlalchemy import and_

from eureHausaufgabenApp import Users, db, app
from eureHausaufgabenApp.models import Schools
from eureHausaufgabenApp.models import SchoolClasses
from eureHausaufgabenApp.util import crypto_util


def get_user_data():
    user = g.user
    session_data = g.data
    session_data["user"] = user_to_dict(user)
    g.data = session_data


def get_user_by_id(user_id):
    return Users.query.filter_by(id=user_id).first()


def user_to_dict(user):
    if user == None:
        return {
            "id" : None,
            "name": None,
            "role": None,
            "points" : None,
            "stay_logged_in" : None
        }
    return  {
        "id" : user.id,
        "name": str(user.Username),
        "role": user.Role,
        "points" : user.Points,
        "stay_logged_in": user.StayLoggedIn
    }

def reset_account():
    app.logger.info(f"Account is being reset for User with email '{g.user.Email}' and name '{g.user.Username}'")
    g.user.Email = None
    g.user.HashedPwd = None
    g.user.Salt = None
    db.session.commit()



def create_user(email, name, school_name, school_class_name, hashed_pwd, salt):
    school = Schools.query.filter_by(Name=school_name).first()
    school_class = SchoolClasses.query.filter_by(ClassName=school_class_name).first()
    email_already_used = Users.query.filter_by(Email=email).first()
    name_and_not_active = Users.query.filter(and_(Users.Username == name, Users.HashedPwd == None)).first()
    # check if school and school class is set (you need to set this before you can create a account)
    # check if the email has not been used yet (so don't set it in the database when registering a new user to the system)
    # check if the name is already registered (you need to set this before you can create a account)
    # check if the hashed password is actually a hashed password and not something else
    if school != None and school_class != None and email_already_used == None and name_and_not_active != None and crypto_util.check_if_hash(hashed_pwd):
        name_and_not_active.Email = email
        name_and_not_active.HashedPwd = hashed_pwd
        name_and_not_active.Salt = salt
        name_and_not_active.StayLoggedIn = False
        if name_and_not_active.Role != -1:
            name_and_not_active.Role = 0
            name_and_not_active.Points = 20
        db.session.commit()
        app.logger.info(f"Account was setup for user with the name '{name}' with email '{email}'")
        return json.dumps({"User-created" : True}), 200
    else:
        app.logger.info(f"Account was not setup because the account information was not right")
        return "Forbidden", 403