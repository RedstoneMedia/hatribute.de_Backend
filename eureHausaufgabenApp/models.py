from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from eureHausaufgabenApp import db

class Schools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(200))

    Classes = relationship("SchoolClasses", uselist=True, backref="school")
    Users = relationship("Users", uselist=True, backref="school")


class SchoolClasses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ClassName = db.Column(db.String(200))
    SchoolId = db.Column(db.Integer, ForeignKey(Schools.id))

    HomeworkList = relationship("HomeworkLists", uselist=True, backref="school_class")
    Reports = relationship("ClassReports", uselist=True, backref="school_class")
    Users = relationship("Users", uselist=True, backref="school_class")


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(200))
    Username = db.Column(db.String(200))
    SchoolId = db.Column(db.Integer, ForeignKey(Schools.id))
    SchoolClassId = db.Column(db.Integer, ForeignKey(SchoolClasses.id))
    Role = db.Column(db.Integer)
    Points = db.Column(db.Integer)
    StayLoggedIn = db.Column(db.Boolean(create_constraint=False))
    HashedPwd = db.Column(db.String(60))

    ActiveSessions = relationship("Sessions", uselist=True, backref="user")
    UserViewedHomework = relationship("UserViewedHomework", uselist=True, backref="user")


class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, ForeignKey(Users.id))
    HashedSessionID = db.Column(db.String(512))
    SessionExpires = db.Column(db.String(200))
    Actions = db.Column(db.Integer)


class HomeworkLists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Exercise = db.Column(db.String(800))
    DonePercentage = db.Column(db.Integer)
    Due = db.Column(db.Date)
    Subject = db.Column(db.String(20))
    CreatorId = db.Column(db.Integer, ForeignKey(Users.id))
    SchoolClassId = db.Column(db.Integer, ForeignKey(SchoolClasses.id))

    Creator = relationship("Users", foreign_keys='HomeworkLists.CreatorId', uselist=False)
    SubHomework = relationship("SubHomeworkLists", uselist=True, backref="homework_list")
    UserViewedHomework = relationship("UserViewedHomework", uselist=True, backref="homework_list")
    Reports = relationship("ClassReports", uselist=True, backref="homework_list")


class SubHomeworkLists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Exercise = db.Column(db.String(800))
    UserId = db.Column(db.Integer, ForeignKey(Users.id))
    Done = db.Column(db.Boolean(create_constraint=False))
    HomeworkListId = db.Column(db.Integer, ForeignKey(HomeworkLists.id))

    User = relationship("Users", foreign_keys='SubHomeworkLists.UserId', uselist=False)
    Reports = relationship("ClassReports",  uselist=True, backref="sub_homework")


class ClassReports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.Integer)
    ByUserId = db.Column(db.Integer)
    SchoolClassId = db.Column(db.Integer, ForeignKey(SchoolClasses.id))
    SubHomeworkId = db.Column(db.Integer, ForeignKey(SubHomeworkLists.id))
    HomeworkListId = db.Column(db.Integer, ForeignKey(HomeworkLists.id))


class UserViewedHomework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, ForeignKey(Users.id))
    HomeworkListId = db.Column(db.Integer, ForeignKey(HomeworkLists.id))


class KnowledgeSources(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.Integer)
    Title = db.Column(db.String(200))
    Description = db.Column(db.String(400))
    Subject = db.Column(db.String(40))
    ByUserId = db.Column(db.Integer, ForeignKey(Users.id))
    SchoolClassId = db.Column(db.Integer, ForeignKey(SchoolClasses.id))
    Data = db.Column(db.String(200))
    Votes = db.Column(db.Integer)
    CreationTime = db.Column(db.Date)
    LastModifiedTime = db.Column(db.Date)

    SchoolClass = relationship("SchoolClasses", foreign_keys='KnowledgeSources.SchoolClassId', uselist=False)
    ByUser = relationship("Users", foreign_keys='KnowledgeSources.ByUserId', uselist=False)