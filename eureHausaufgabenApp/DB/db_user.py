import json

from flask import g

from eureHausaufgabenApp import Users, db
from eureHausaufgabenApp.models import Schools
from eureHausaufgabenApp.models import SchoolClasses
from eureHausaufgabenApp.util import crypto_util


def get_user_data():
    user = g.user
    session_data = g.data
    session_data["user"] = user_to_dict(user)
    g.data = session_data


def user_to_dict(user):
    if user == None:
        return {
            "id" : None,
            "name": None,
            "role": None,
            "points" : None
        }
    return  {
        "id" : user.id,
        "name": str(user.Username),
        "role": user.Role,
        "points" : user.Points
    }


def create_user(email, name, school_name, school_class_name, hashed_pwd, salt):
    school = Schools.query.filter_by(Name=school_name).first()
    school_class = SchoolClasses.query.filter_by(ClassName=school_class_name).first()
    email_allready_used = Users.query.filter_by(Email=email).first()
    name_allready_used = Users.query.filter_by(Username=name).first()

    if school != None and school_class != None and email_allready_used == None and name_allready_used == None and crypto_util.check_if_hash(hashed_pwd):
        user = Users(Email=email, HashedPwd=hashed_pwd, Username=name, SchoolId=school.id, SchoolClassId=school_class.id, Salt=salt, Role=0, Points=20)
        db.session.add(user)
        db.session.commit()
        return json.dumps({"User-created" : True}), 200
    else:
        return "Forbidden", 403