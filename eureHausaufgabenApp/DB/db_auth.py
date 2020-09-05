import hashlib
from eureHausaufgabenApp.util import crypto_util
from flask import request, g
import binascii
from datetime import datetime
from datetime import timedelta
import json
from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import Users, Sessions
import time
import traceback


def login(email, password, stay_logged_in , secret_key):
    user = Users.query.filter_by(Email=email).first()

    if user == None:
        app.logger.info(f"Provided user with email : '{email}' does not exist")
        return {"right": False}, 401

    original_hash_pwd = user.HashedPwd
    if crypto_util.check_pwd(password, original_hash_pwd):
        app.logger.info(f"Right password for user with email : '{email}'")
        user.StayLoggedIn = stay_logged_in
        session, expires, _ = gen_new_session(user)
        data = {
            'right': True,
            'session': {
                'right': True,
                'session': session,
                'expires': expires
            }
        }
        return data, 200
    else:
        app.logger.info(f"Wrong password for user with email : '{email}'")
        return {"right": False}, 401


def gen_new_session(user, old_session=None):
    # Pop sessions until the amount of sessions is at the maximum
    while Sessions.query.filter_by(UserId=user.id).count() >= app.config["SESSION_PER_USER_LIMIT"]:
        next_session = None
        # Make sure that the picked session is not the current session
        for s in Sessions.query.filter_by(UserId=user.id).order_by(Sessions.Actions):
            if s != old_session:
                next_session = s
                break
        pop_session(next_session)

    actions = 0
    if old_session:
        actions = old_session.Actions
        pop_session(old_session)  # Pop old session
    new_session = Sessions(UserId=user.id, Actions=actions)  # Create new session and inherit UserId and actions
    session_id = crypto_util.random_string(60)
    expires = save_session(user, new_session, crypto_util.hash_sha512(session_id), expires=app.config["SESSION_EXPIRE_TIME_MINUTES"])
    return session_id, expires, new_session


def save_session(user, session, sessionHash, expires):
    session.HashedSessionID = sessionHash
    if not user.StayLoggedIn:
        session.SessionExpires = str(datetime.now() + timedelta(minutes=expires))
    else:
        session.SessionExpires = str(datetime.now() + timedelta(days=app.config["SESSION_EXPIRE_TIME_STAY_LOGGED_IN_DAYS"]))
    db.session.add(session)
    db.session.commit()
    return session.SessionExpires


def logout():
    session = Sessions.query.filter_by(id=g.session_db_object.id).first()
    pop_session(session)


def delete_all_really_old_sessions():
    sessions = Sessions.query.all()
    now = datetime.now()
    for session in sessions:
        expires = datetime.strptime(session.SessionExpires, '%Y-%m-%d %H:%M:%S.%f')
        if now >= expires + timedelta(hours=0, days=app.config["REALLY_OLD_SESSIONS_DELETE_AFTER_EXPIRE_DAYS"]):
            pop_session(session)


def register_action(session):
    try:
        session.Actions += 1
        db.session.commit()
    except Exception:
        app.logger.error(traceback.format_exc())


def check_session(session_id):
    # Hash the session id with sha512
    hashed_session_id = crypto_util.hash_sha512(session_id)

    # Search for user with that hashed session id
    found_session = Sessions.query.filter_by(HashedSessionID=hashed_session_id).first()
    if found_session:
        if found_session.SessionExpires:
            user = Users.query.filter_by(id=found_session.UserId).first()  # Get user from session

            expires = datetime.strptime(found_session.SessionExpires, '%Y-%m-%d %H:%M:%S.%f')  # Parse session expire date
            now = datetime.now()
            if now >= expires:  # Check if session expired
                pop_session(found_session)
                app.logger.info(f"Session expired for user : {user.Email}")
                delete_all_really_old_sessions()
                return None, {"session": {"right": False}}, None
            else:
                data = {
                    'session': {
                        'right': True
                    }
                }
                register_action(found_session)
                # Check if session is about to expire and if it is, create a new session and update the expiration date
                if now >= (expires - timedelta(hours=0, minutes=app.config["SESSION_EXPIRE_TIME_MINUTES"] / 2)) or (user.StayLoggedIn and now >= (expires - (timedelta(days=app.config["SESSION_EXPIRE_TIME_STAY_LOGGED_IN_DAYS"]) - timedelta(minutes=app.config["SESSION_EXPIRE_TIME_MINUTES"] / 2)))):
                    new_encrypted_session, new_expire_time, new_session = gen_new_session(user, found_session)
                    data["session"]["session"] = new_encrypted_session
                    data["session"]["expires"] = new_expire_time
                else:
                    new_session = found_session
                delete_all_really_old_sessions()
                return user, data, new_session
    else:
        app.logger.info(f"Session was not found")
        return None, {"session": {"right": False}}, None


def pop_session(session):
    db.session.delete(session)
    db.session.commit()
    g.session_db_object = None


def pop_all_user_sessions(user):
    sessions = Sessions.querry.filter_by(UserId=user.id)
    for session in sessions:
        pop_session(session)


def before_request(data: dict):
    if "session" in data:
        session = data["session"]
        user, return_data, session_db_object = check_session(session)
        g.data = return_data
        if user:
            g.user = user
            g.session_db_object = session_db_object
            app.logger.info("Session was right")
        else:
            g.user = None
            g.session_db_object = None
    else:
        g.data = None
        g.user = None
        g.session_db_object = None

