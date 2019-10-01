import hashlib
from eureHausaufgabenApp.util import crypto_util
from flask import request, g
import binascii
from datetime import datetime
from datetime import timedelta
import json
from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import Users
import time


def login(email, hashed_pwd, stay_logged_in , secret_key):
    user = Users.query.filter_by(Email=email).first()

    if user == None:
        print("user dose not exist !")
        return {"right": False}, 401

    if crypto_util.check_if_hash(hashed_pwd) == False:
        print("pwd is not a hash")
        return {"right": False}, 401

    original_hash_pwd = user.HashedPwd
    check_pwd_hash = hashed_pwd
    if original_hash_pwd == check_pwd_hash:
        print("[{email}] : right pwd".format(email=str(email)))
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
        print("wrong pwd")
        return {"right": False}, 401

def gen_new_session(check_pwd_hash, email, secret_key, user):
    pwd_and_email = check_pwd_hash+email
    random_string = crypto_util.random_string(30)
    real_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    session_id = crypto_util.hash(pwd_and_email + random_string)
    nonce = crypto_util.random_string(30)
    store_new_session_nonce(user, nonce)
    expires = save_session(user, crypto_util.hash(session_id + real_ip + nonce), expires=10)
    key = str(secret_key)
    key = key.encode()
    key = hashlib.sha256(key).digest()
    session = '{"session-id":"' + session_id + '", "session-nonce":"' + nonce + '"}'
    enc = crypto_util.encrypt(bytes(str(session), encoding="utf-8"), key)
    return binascii.hexlify(enc).decode("utf-8"), expires


def save_session(user, sessionHash, expires):
    user.HashedSessionID = sessionHash
    if not user.StayLoggedIn:
        user.SessionExpires = str(datetime.now() + timedelta(minutes=expires))
    else:
        user.SessionExpires = str(datetime.now() + timedelta(days=62))
    db.session.add(user)
    db.session.commit()
    return user.SessionExpires


def store_new_session_nonce(user, nonce):
    user.SessionNonce = nonce
    db.session.add(user)
    db.session.commit()


def logout():
    user = g.user
    pop_session(user)
    

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


def check_session(secret_key, enc_session):
    try:
        key = str(secret_key)
        key = key.encode()
        key = hashlib.sha256(key).digest()

        enc_session = binascii.unhexlify(enc_session)
        session = crypto_util.decrypt(enc_session, key)

    except Exception as e:
        print("invalid session data")
        print(e)
        return False, {"session": {"right": False}}, None

    try:
        session = json.loads(session, encoding="utf-8")
        session_id = session["session-id"]
        session_nonce = session["session-nonce"]
    except Exception as e:
        print(e)
        return False, {"session": {"right": False}}, None

    real_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    session = crypto_util.hash(session_id + real_ip + session_nonce)

    user = Users.query.filter_by(HashedSessionID=session).first()
    if user:
        if user.SessionExpires:
            expires = datetime.strptime(user.SessionExpires, '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.now()

            if now >= expires:
                return False, {"session": {"right": False}}, user

            else:
                new_session = gen_new_session(user.HashedPwd, user.Email, secret_key, user)
                data = {
                    'session': {
                        'right': True,
                        'session': new_session[0],
                        'expires': new_session[1]
                    }
                }
                return user, data, None
    else:
        return False, {"session": {"right": False}}, None


def pop_session(user):
    user.HashedSessionID = None
    user.SessionExpires = None
    user.SessionNonce = None
    db.session.add(user)
    db.session.commit()


def before_request(data):
    try:
        session = data["session"]
        other, s_data, user_when_expired = check_session(app.config["secret-key"], session)
    except Exception as e:
        g.user = None
        g.data = None
        return False
    g.data = s_data
    if other:
        print("right session data : " + str(other.Email))
        g.user = other
    else:
        if user_when_expired:
            pop_session(user_when_expired)
            print("session expired")
            g.user = None
        else:
            print("session wrong")
            g.user = None