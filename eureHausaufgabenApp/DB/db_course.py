from flask import g
from typing import List

from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import Schools, UserCoursesLists, Courses, HomeworkLists, Users


def get_user_courses_list_list_by_user() -> List[UserCoursesLists]:
    school = get_school_by_user()
    if not school:
        return None

    user_courses_list = g.user.UserCoursesList
    return user_courses_list


def get_course_by_course_id(id: int):
    return Courses.query.filter_by(id=id).first()


def get_user_courses_by_user() -> List[Courses]:
    courses = []
    if user_courses_list := get_user_courses_list_list_by_user():
        for user_courses_list_item in user_courses_list:
            courses.append(user_courses_list_item.course)
    return courses


def course_to_dict(course: Courses, include_homework=True) -> dict:
    homework_list = course.HomeworkList
    course_return = {
        "CourseName" : course.CourseName,
        "CourseId" : course.id,
        "IsDefaultCourse" : course.IsDefaultCourse,
        "SchoolId" : course.SchoolId
    }
    if include_homework:
        course_return["homework"] = []
        for h in homework_list:
            course_return["homework"].append(homework_to_dict(h))
    return course_return


def courses_list_items_to_dict(course_list_items, include_homework=True) -> List[dict]:
    courses_return = []
    for course_list_item in course_list_items:
        courses_return.append(course_to_dict(course_list_item.course, include_homework=include_homework))
    return courses_return


def get_courses_dict_list_by_user(include_homework=True) -> List[dict]:
    courses_list_items = get_user_courses_list_list_by_user()  # type: List[UserCoursesLists]
    if courses_list_items:
        return courses_list_items_to_dict(courses_list_items, include_homework=include_homework)


def get_all_courses() -> int:
    if g.user.Role >= 3:
        g.data["courses"] = []
        for course in Courses.query.all():
            g.data["courses"].append(course_to_dict(course, include_homework=False))
        return 200
    return 401


def get_all_user_school_courses() -> int:
    user_school = g.user.school
    if not user_school:
        return 404
    g.data["courses"] = []
    for course in sorted(user_school.Courses, key=lambda course: course.CourseName):
        g.data["courses"].append(course_to_dict(course, include_homework=False))
    return 200


def get_user_courses(include_homework=True) -> int:
    courses_dict_list = get_courses_dict_list_by_user(include_homework=include_homework)
    if g.user.Role == -1:
        g.data["courses"] = courses_dict_list
        return 200
    remove_past_homework()
    if courses_dict_list:
        g.data["courses"] = courses_dict_list
    else:
        g.data["courses"] = []
    return 200


def is_course_id_in_courses(courses : List[Courses], course_id : int):
    for course in courses:
        if course.id == course_id:
            return True
    return False


def add_course_to_user(user : Users, course : Courses):
    if UserCoursesLists.query.filter_by(UserId=user.id, CourseId=course.id).first():
        return 400
    new_user_course = UserCoursesLists(UserId=user.id, CourseId=course.id)
    db.session.add(new_user_course)
    db.session.commit()
    return 200


def remove_course_from_user(course: Courses, user: Users):
    if user_course_entry := UserCoursesLists.query.filter_by(UserId=user.id, CourseId=course.id).first():
        db.session.delete(user_course_entry)
        db.session.commit()
        return 200
    return 400


def remove_all_courses_from_user(user : Users):
    for user_course in user.UserCoursesList:
        db.session.delete(user_course)
    db.session.commit()


def remove_course_from_all_users(course: Courses):
    for user_course in UserCoursesLists.query.filter_by(CourseId=course.id):
        db.session.delete(user_course)
    db.session.commit()


def add_default_courses_to_user(user : Users):
    default_courses = Courses.query.filter_by(SchoolId=user.SchoolId, IsDefaultCourse=True)
    for course in default_courses:
        add_course_to_user(user, course)


def create_course(course_name: str, school_name: str, is_default_course: bool):
    if g.user.Role >= 3:
        school = get_school_by_name(school_name)
        if school:
            course = Courses(SchoolId=school.id, IsDefaultCourse=is_default_course, CourseName=course_name)
            db.session.add(course)
            if course.IsDefaultCourse:
                for user in Users.query.all(): #type: Users
                    if user.HashedPwd != None:
                        add_course_to_user(user, course)
            db.session.commit()
            return 200
        return 404
    return 401


def remove_course(course_id: int):
    if g.user.Role >= 3:
        course = Courses.query.filter_by(id=course_id).first() # type: Courses
        if course:
            remove_course_from_all_users(course)
            db.session.delete(course)
            db.session.commit()
            return 200
        return 404
    return 401


from .db_school import get_school_by_user, get_school_by_name
from .db_homework import homework_to_dict, remove_past_homework