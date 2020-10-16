from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from eureHausaufgabenApp import db

class Schools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(200))

    Courses = relationship("Courses", uselist=True, backref="school")
    Users = relationship("Users", uselist=True, backref="school")


class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    CourseName = db.Column(db.String(200))
    SchoolId = db.Column(db.Integer, ForeignKey(Schools.id))
    IsDefaultCourse = db.Column(db.Boolean(create_constraint=False))

    HomeworkList = relationship("HomeworkLists", uselist=True, backref="course")
    Reports = relationship("ClassReports", uselist=True, backref="course")
    UsersCoursesList = relationship("UserCoursesLists", uselist=True, backref="course")


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(200))
    SchoolId = db.Column(db.Integer, ForeignKey(Schools.id))
    Role = db.Column(db.Integer)
    Points = db.Column(db.Integer)
    HashedPwd = db.Column(db.String(60))
    FirstTimeSignInToken = db.Column(db.String(200))

    ActiveSessions = relationship("Sessions", uselist=True, backref="user")
    UserViewedHomework = relationship("UserViewedHomework", uselist=True, backref="user")
    UserCoursesList = relationship("UserCoursesLists", uselist=True, backref="user")
    Reports = relationship("ClassReports", uselist=True, backref="by_user")


class UserCoursesLists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, ForeignKey(Users.id))
    CourseId = db.Column(db.Integer, ForeignKey(Courses.id))


class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserId = db.Column(db.Integer, ForeignKey(Users.id))
    HashedSessionID = db.Column(db.String(512))
    SessionExpires = db.Column(db.String(200))
    StayLoggedIn = db.Column(db.Boolean(create_constraint=False))
    Actions = db.Column(db.Integer)


class HomeworkLists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Exercise = db.Column(db.String(800))
    DonePercentage = db.Column(db.Integer)
    Due = db.Column(db.Date)
    CreatorId = db.Column(db.Integer, ForeignKey(Users.id))
    CourseId = db.Column(db.Integer, ForeignKey(Courses.id))

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
    ByUserId = db.Column(db.Integer, ForeignKey(Users.id))
    CourseId = db.Column(db.Integer, ForeignKey(Courses.id))
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
    ByUserId = db.Column(db.Integer, ForeignKey(Users.id))
    CourseId = db.Column(db.Integer, ForeignKey(Courses.id))
    Data = db.Column(db.String(200))
    Votes = db.Column(db.Integer)
    CreationTime = db.Column(db.Date)
    LastModifiedTime = db.Column(db.Date)

    Course = relationship("Courses", foreign_keys='KnowledgeSources.CourseId', uselist=False)
    ByUser = relationship("Users", foreign_keys='KnowledgeSources.ByUserId', uselist=False)