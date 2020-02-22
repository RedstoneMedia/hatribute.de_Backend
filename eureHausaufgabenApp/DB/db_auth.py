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


def login(email, hashed_pwd, stay_logged_in , secret_key):
    user = Users.query.filter_by(Email=email).first()

    if user == None:
        app.logger.info(f"Provided user with email : '{email}' does not exist")
        return {"right": False}, 401

    if crypto_util.check_if_hash(hashed_pwd) == False:
        app.logger.error("Provided password was not a hash")
        return {"right": False}, 401

    original_hash_pwd = user.HashedPwd
    check_pwd_hash = hashed_pwd
    if original_hash_pwd == check_pwd_hash:
        app.logger.info(f"Right password for user with email : '{email}'")
        user.StayLoggedIn = stay_logged_in
        session = gen_new_session(check_pwd_hash, email, secret_key, user)
        data = {
            'right': True,
            'session': {
                'right': True,
                'session': session[0],
                'expires': session[1]
            }
        }
        return data, 200
    else:
        app.logger.info(f"Wrong password for user with email : '{email}'")
        return {"right": False}, 401

def gen_new_session(check_pwd_hash, email, secret_key, user, old_session=None):
    if old_session:
        pop_session(old_session)
    new_session = Sessions(UserId=user.id)
    pwd_and_email = check_pwd_hash+email
    random_string = crypto_util.random_string(30)
    real_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    session_id = crypto_util.hash(pwd_and_email + random_string)
    nonce = crypto_util.random_string(30)
    store_new_session_nonce(new_session, nonce)
    expires = save_session(user, new_session, crypto_util.hash(session_id + real_ip + nonce), expires=app.config["SESSION_EXPIRE_TIME_MINUTES"])
    key = str(secret_key)
    key = key.encode()
    key = hashlib.sha256(key).digest()
    session = '{"session-id":"' + session_id + '", "session-nonce":"' + nonce + '"}'
    enc = crypto_util.encrypt(bytes(str(session), encoding="utf-8"), key)
    return binascii.hexlify(enc).decode("utf-8"), expires, new_session


def save_session(user, session, sessionHash, expires):
    session.HashedSessionID = sessionHash
    if not user.StayLoggedIn:
        session.SessionExpires = str(datetime.now() + timedelta(minutes=expires))
    else:
        session.SessionExpires = str(datetime.now() + timedelta(days=app.config["SESSION_EXPIRE_TIME_STAY_LOGGED_IN_DAYS"]))
    db.session.add(user)
    db.session.commit()
    return session.SessionExpires


def store_new_session_nonce(session, nonce):
    session.SessionNonce = nonce
    db.session.add(session)
    db.session.commit()


def logout():
    session = g.session_db_object
    pop_session(session)
    

def get_salt_by_email(email):
    user = Users.query.filter_by(Email=email).first()
    salt = ""
    if user == None:  # gen fake salt so the client can't tell if the user exist
        fake_salt = crypto_util.gen_salt_and_hash("this_is_fake")[1]
        salt = fake_salt
    else:
        salt = user.Salt

    return_data = {"salt" : salt}
    return return_data, 200


def delete_all_really_old_sessions():
    sessions = Sessions.query.all()
    now = datetime.now()
    for session in sessions:
        expires = datetime.strptime(session.SessionExpires, '%Y-%m-%d %H:%M:%S.%f')
        if now >= expires + timedelta(hours=0, days=app.config["REALLY_OLD_SESSIONS_DELETE_AFTER_EXPIRE_DAYS"]):
            pop_session(session)


def check_session(secret_key, enc_session):
    try:
        key = str(secret_key)
        key = key.encode()
        key = hashlib.sha256(key).digest()

        enc_session = binascii.unhexlify(enc_session)
        session = crypto_util.decrypt(enc_session, key)

    except Exception as e:
        app.logger.info("Provided session data could not be decrypted")
        return False, {"session": {"right": False}}, None

    try:
        session = json.loads(session, encoding="utf-8")
        session_id = session["session-id"]
        session_nonce = session["session-nonce"]
    except Exception as e:
        app.logger.info("Provided session data did not contain the required json data")
        return False, {"session": {"right": False}}, None

    real_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    session = crypto_util.hash(session_id + real_ip + session_nonce)

    found_session = Sessions.query.filter_by(HashedSessionID=session).first()
    if found_session:
        if found_session.SessionExpires:
            expires = datetime.strptime(found_session.SessionExpires, '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.now()

            user = Users.query.filter_by(id=found_session.UserId).first()

            if now >= expires:
                pop_session(found_session)
                app.logger.info(f"Session expired for user : {user.Email}")
                delete_all_really_old_sessions()
                return False, {"session": {"right": False}}, user
            else:
                data = {
                    'session': {
                        'right': True
                    }
                }

                # check if session is about to expire and if it is create a new session and update the expiration date
                if now >= (expires - timedelta(hours=0, minutes=app.config["SESSION_EXPIRE_TIME_MINUTES"] / 2)) or (user.StayLoggedIn and now >= (expires - (timedelta(days=app.config["SESSION_EXPIRE_TIME_STAY_LOGGED_IN_DAYS"]) - timedelta(minutes=app.config["SESSION_EXPIRE_TIME_MINUTES"] / 2)))):
                    new_encrypted_session, new_expire_time, new_session = gen_new_session(user.HashedPwd, user.Email, secret_key, user, found_session)
                    data["session"]["session"] = new_encrypted_session
                    data["session"]["expires"] = new_expire_time
                else:
                    new_session = found_session
                delete_all_really_old_sessions()
                return user, data, None, new_session
    else:
        app.logger.info(f"Session was not found")
        return False, {"session": {"right": False}}, None


def pop_session(session):
    db.session.delete(session)
    db.session.commit()
    g.session_db_object = None


def pop_all_user_sessions(user):
    sessions = Sessions.querry.filter_by(UserId=user.id)
    for session in sessions:
        pop_session(session)


def before_request(data):
    try:
        session = data["session"]
        other, s_data, user_when_expired, session_db_object = check_session(app.config["secret-key"], session)
    except Exception as e:
        g.user = None
        g.data = None
        g.session_db_object = None
        return False
    g.data = s_data
    if other and session_db_object:
        g.user = other
        g.session_db_object = session_db_object
        app.logger.info("Session was right")
    else:
        g.user = None
        g.session_db_object = None

