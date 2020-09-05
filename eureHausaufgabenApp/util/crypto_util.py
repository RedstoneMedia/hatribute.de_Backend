from Cryptodome.Cipher import AES
from Cryptodome import Random
from base64 import *
import hashlib
import bcrypt
import random
import string


def encrypt(raw, key):
    BS = 16
    pad = lambda s: s + (BS - len(s) % BS) * bytes(chr(BS - len(s) % BS), encoding="utf-8")
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(raw))


def decrypt(enc, key):
    BS = 16
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    enc = b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')


def hash_sha512(s):
    h = hashlib.new("sha512")
    h.update(str(s).encode())
    return h.hexdigest()


def random_string(length):
    return "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))


def hash_pwd(pwd):
    salt = bcrypt.gensalt(rounds=15)
    return str(bcrypt.hashpw(bytes(pwd, encoding="utf-8"), salt), encoding="utf-8")


def check_pwd(pwd, pwd_hash):
    return bcrypt.checkpw(bytes(pwd, encoding="utf-8"), bytes(pwd_hash, encoding="utf-8"))
