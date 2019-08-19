from eureHausaufgabenApp import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(200))
    Username = db.Column(db.String(200))
    School = db.Column(db.String(200))
    SchoolClass = db.Column(db.String(200))
    Role = db.Column(db.Integer)
    HashedPwd = db.Column(db.String(512))
    Salt = db.Column(db.String(512))
    HashedSessionID = db.Column(db.String(512))
    SessionExpires = db.Column(db.String(200))
    SessionNonce = db.Column(db.String(200))


class Schools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(200))