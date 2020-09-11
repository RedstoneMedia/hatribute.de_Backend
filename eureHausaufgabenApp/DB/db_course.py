from flask import g
from typing import List

from eureHausaufgabenApp import db, app
from eureHausaufgabenApp.models import Schools, UserCoursesLists, Courses, HomeworkLists


def get_user_courses_list_list_by_user() -> List[UserCoursesLists]:
    school = get_school_by_user()
    if not school:
        return None

    user_courses_list = g.user.UserCoursesList
    return user_courses_list


def get_user_courses_by_user() -> List[Courses]:
    courses = []
    if user_courses_list := get_user_courses_list_list_by_user():
        for user_courses_list_item in user_courses_list:
            courses.append(user_courses_list_item.course)
    return courses


def course_to_dict(course: Courses) -> dict:
    homework_list = course.HomeworkList
    course_return = {
        "CourseName" : course.CourseName,
        "CourseId" : course.id,
        "homework" : []
    }
    for h in homework_list:
        course_return["homework"].append(homework_to_dict(h))
    return course_return


def courses_list_items_to_dict(course_list_items) -> List[dict]:
    courses_return = []
    for course_list_item in course_list_items:
        courses_return.append(course_to_dict(course_list_item.course))
    return courses_return


def get_courses_dict_list_by_user() -> List[dict]:
    courses_list_items = get_user_courses_list_list_by_user()  # type: List[UserCoursesLists]
    if courses_list_items:
        return courses_list_items_to_dict(courses_list_items)


def get_user_courses() -> int:
    courses_dict_list = get_courses_dict_list_by_user()
    if g.user.Role == -1:
        g.data["courses"] = courses_dict_list
        return 200
    remove_past_homework()
    if courses_dict_list:
        g.data["courses"] = courses_dict_list
        return 200
    else:
        return 401


def is_course_id_in_courses(courses : List[Courses], course_id : int):
    for course in courses:
        if course.id == course_id:
            return True
    return False


from .db_school import get_school_by_user
from .db_homework import homework_to_dict, remove_past_homework