from flask import request, g
from sqlalchemy.orm.exc import ObjectDeletedError

import traceback
import operator
from datetime import datetime, timedelta
from typing import Tuple, Union

from hatributeApp import db, app
from hatributeApp.util import crypto_util
from hatributeApp.models import Users, Sessions


# Tries to find a matching user with username and password and if it finds one creates a session and sets the session.
def login(user_name: str, password: str, stay_logged_in: bool):
    user = Users.query.filter_by(Username=user_name).first()
    if user == None:
        app.logger.info(f"Provided user with name : '{user_name}' does not exist")
        return {"right": False}, 401
    original_hash_pwd = user.HashedPwd
    if crypto_util.check_pwd(password, original_hash_pwd):
        app.logger.info(f"Right password for user with name : '{user_name}'")
        user.StayLoggedIn = stay_logged_in
        session, expires, _ = gen_new_session(user, stay_logged_in)
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
        app.logger.info(f"Wrong password for user with name : '{user_name}'")
        return {"right": False}, 401


# Generates a completely new session or renews a given session.
def gen_new_session(user: Users, stay_logged_in: bool, old_session: Sessions = None) -> Tuple[int, str, Sessions]:
    app.logger.debug(f"Generating new session")
    if old_session:
        try:
            old_session_actions = old_session.Actions
            app.logger.debug(f"Old session is : {old_session.id}")
        except ObjectDeletedError:
            old_session = None

    current_active_sessions = len(user.ActiveSessions)
    if old_session == None:  # if not renewing a session delete one more then normal to account for session that is going to be created
        current_active_sessions += 1

    # Pop sessions until the amount of sessions is at the maximum
    while current_active_sessions > app.config["SESSION_PER_USER_LIMIT"]:
        current_active_sessions = len(user.ActiveSessions)
        next_session = None
        for s in sorted(user.ActiveSessions, key=operator.attrgetter("Actions")):
            next_session = s
            break
        if next_session:
            pop_session(next_session)

    actions = 0
    if old_session:
        actions = old_session_actions
        pop_session(old_session)

    new_session = Sessions(UserId=user.id, Actions=actions, StayLoggedIn=stay_logged_in)  # Create new session and inherit UserId and actions
    session_id = crypto_util.random_string(60)
    expires = save_session(new_session, crypto_util.hash_sha512(session_id), app.config["SESSION_EXPIRE_TIME_MINUTES"], stay_logged_in)
    return session_id, expires, new_session


# Saves a session and returns the expiration date
def save_session(session: Sessions, sessionHash: str, expires: float, stay_logged_in: bool) -> str:
    session.HashedSessionID = sessionHash
    if not stay_logged_in:
        session.SessionExpires = str(datetime.now() + timedelta(minutes=expires))
    else:
        session.SessionExpires = str(datetime.now() + timedelta(days=app.config["SESSION_EXPIRE_TIME_STAY_LOGGED_IN_DAYS"]))
    db.session.add(session)
    db.session.commit()
    app.logger.debug(f"New session was Generated with id : {session.id}")
    return session.SessionExpires


# Pops the currently used session
def logout():
    session = Sessions.query.filter_by(id=g.session_db_object.id).first()
    pop_session(session)


# Tries to pop all sessions that are over the expiration date.
def delete_all_old_sessions():
    app.logger.debug(f"Deleting all old sessions")
    sessions = Sessions.query.all()
    now = datetime.now()
    for session in sessions:
        try:
            expires = datetime.strptime(session.SessionExpires, '%Y-%m-%d %H:%M:%S.%f')
            if now >= expires:
                pop_session(session)
        except ObjectDeletedError:
            pass


# Adds one to the action count of the specified session.
def register_action(session: Sessions):
    try:
        session.Actions += 1
        db.session.commit()
    except Exception:
        app.logger.error(traceback.format_exc())


# Uses a session id and determines if it is valid or not + Auto renews session if it is about to expire.
def check_session(session_id: int) -> Tuple[Union[Users, None], dict, Union[Sessions, None]]:
    delete_all_old_sessions()

    # Hash the session id with sha512
    hashed_session_id = crypto_util.hash_sha512(session_id)

    # Search for user with that hashed session id
    found_session = Sessions.query.filter_by(HashedSessionID=hashed_session_id).first()  # type: Sessions
    if found_session:
        if found_session.SessionExpires:
            user = found_session.user

            expires = datetime.strptime(found_session.SessionExpires, '%Y-%m-%d %H:%M:%S.%f')  # Parse session expire date
            now = datetime.now()
            if now >= expires:  # Check if session expired. Technically not needed, because delete_all_old_sessions() will delete the session before this check
                pop_session(found_session)
                app.logger.info(f"Session expired for user : {user.Email}")
                return None, {"session": {"right": False}}, None
            else:
                data = {
                    'session': {
                        'right': True
                    }
                }
                register_action(found_session)
                # Check if session is about to expire and if it is, create a new session and update the expiration date
                if now >= (expires - timedelta(hours=0, minutes=app.config["SESSION_EXPIRE_TIME_MINUTES"] / 2)) or (found_session.StayLoggedIn and now >= (expires - (timedelta(days=app.config["SESSION_EXPIRE_TIME_STAY_LOGGED_IN_DAYS"]) - timedelta(minutes=app.config["SESSION_EXPIRE_TIME_MINUTES"] / 2)))):
                    new_session_id, new_expire_time, new_session = gen_new_session(user, found_session.StayLoggedIn, found_session)
                    data["session"]["session"] = new_session_id
                    data["session"]["expires"] = new_expire_time
                else:
                    new_session = found_session
                return user, data, new_session
    else:
        app.logger.info(f"Session was not found")
        return None, {"session": {"right": False}}, None


# Removes the specified session.
def pop_session(session: Sessions):
    # db.session.delete(session)
    # ^ this dose not work so we have to do this but that's stupid
    app.logger.debug(f"Popping session : {session.id}")
    Sessions.query.filter_by(id=session.id).delete(synchronize_session="fetch")
    db.session.commit()
    g.session_db_object = None


# Pops all sessions of the specified user.
def pop_all_user_sessions(user: Users):
    sessions = user.ActiveSessions
    for session in sessions:
        pop_session(session)


# Gets session id from data checks if session is valid and sets global context variables.
def handel_session_request(data: dict):
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
