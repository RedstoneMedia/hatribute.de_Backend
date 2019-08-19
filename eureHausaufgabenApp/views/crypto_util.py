from Cryptodome.Cipher import AES
from Cryptodome import Random
from base64 import *
import hashlib
import random
import string
import re

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


def hash(s):
    h = hashlib.new("sha512")
    h.update(str(s).encode())
    return h.hexdigest()


def random_string(length):
    return "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))


def check_if_hash(check_hash):
    match = re.match("^[0123456789abcdef]*$", check_hash)
    return (match is not None) and (len(check_hash) == 128)

def hash_pwd(pwd, salt):
    h = hashlib.new("sha512")
    h.update(str(salt + pwd).encode())
    return h.hexdigest()


def gen_salt_and_hash(pwd):
    salt = random_string(30)
    h = hashlib.new("sha512")
    h.update(str(salt + pwd).encode())
    return h.hexdigest(), salt
