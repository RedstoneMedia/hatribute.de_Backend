from flask import g


def get_school_by_user():
    return g.user.school