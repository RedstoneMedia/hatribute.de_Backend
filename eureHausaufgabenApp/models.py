from eureHausaufgabenApp import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(200))
    Username = db.Column(db.String(200))
    SchoolId = db.Column(db.Integer)
    SchoolClassId = db.Column(db.Integer)
    Role = db.Column(db.Integer)
    Points = db.Column(db.Integer)
    HashedPwd = db.Column(db.String(512))
    Salt = db.Column(db.String(512))
    HashedSessionID = db.Column(db.String(512))
    SessionExpires = db.Column(db.String(200))
    SessionNonce = db.Column(db.String(200))



class Schools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(200))
    UnitsSchoolName = db.Column(db.String(200))


class SchoolClasses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ClassName = db.Column(db.String(200))
    SchoolId = db.Column(db.Integer)



class HomeworkLists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Exercise = db.Column(db.String(800))
    DonePercentage = db.Column(db.Integer)
    Due = db.Column(db.Date)
    Subject = db.Column(db.String(20))
    CreatorId = db.Column(db.Integer)
    SchoolClassId = db.Column(db.Integer)


class UserViewedHomework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer)
    HomeworkListId = db.Column(db.Integer)



class SubHomeworkLists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Exercise = db.Column(db.String(800))
    UserId = db.Column(db.Integer)
    Done = db.Column(db.Boolean(create_constraint=False))
    HomeworkListId = db.Column(db.Integer)



class ClassReports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.Integer)
    ByUserId = db.Column(db.Integer)
    SchoolClassId = db.Column(db.Integer)
    HomeworkListId = db.Column(db.Integer)
    SubHomeworkId = db.Column(db.Integer)