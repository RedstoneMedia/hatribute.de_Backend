import os
from typing import List

from flask import g

from hatributeApp.util import file_util
from hatributeApp.util.crypto_util import random_string

from hatributeApp import db, app
from hatributeApp.models import SubHomeworkLists



def get_sub_homework_from_id(sub_homework_id: int) -> SubHomeworkLists:
    return SubHomeworkLists.query.filter_by(id=sub_homework_id).first()


# Converts a sub homework into a dict.
def sub_homework_to_dict(sub_homework: SubHomeworkLists):
    return {
        "Exercise" : sub_homework.Exercise,
        "Done" : sub_homework.Done,
        "User" : user_to_dict(sub_homework.user),
        "id" : sub_homework.id,
        "reported" : has_reported_sub_homework(sub_homework)
    }


# Removes a sub homework, including all uploaded images that are linked to that sub homework.
def remove_sub_homework(sub_homework: SubHomeworkLists):
    sub_folder = "{}-{}".format(sub_homework.HomeworkListId, sub_homework.id)
    count = file_util.get_image_count_in_sub_folder(sub_folder)
    if count > 0:
        file_util.remove_sub_folder(sub_folder)
    db.session.delete(sub_homework)
    db.session.commit()


# Registers the current user for the specified sub homework.
def register_user_for_sub_homework(sub_homework_id: int) -> int:
    sub_homework = get_sub_homework_from_id(sub_homework_id)
    if sub_homework:
        if not sub_homework.UserId:  # Check if no one has registered yet
            sub_homework.UserId = g.user.id
            db.session.commit()
            return 200
        g.data["already_registered_user"] = user_to_dict(get_user_by_id(sub_homework.UserId))
        return 403  # Someone has registered for this homework
    return 401


# De-registers the current user for the specified sub homework.
def de_register_user_for_sub_homework(sub_homework_id: int) -> int:
    sub_homework = get_sub_homework_from_id(sub_homework_id)
    if sub_homework:
        if sub_homework.Done:
            g.user.Points -= get_sub_homework_add_points()
            db.session.commit()
        reset_sub_homework(sub_homework)
        return 200
    return 401


# Returns how many points should be added to that user based on the users role.
def get_sub_homework_add_points() -> int:
    points = 0
    if g.user.Role == 0:
        points = 10
    elif g.user.Role >= 1:
        points = 15
    return points


# Uploads base64 images to the sub homework and finishes the sub homework.
def upload_sub_homework(sub_homework_id : int, files : List[str]) -> int:
    sub_homework = get_sub_homework_from_id(sub_homework_id)
    if sub_homework:
        if sub_homework.UserId != g.user.id: # Check if user is registered for that sub homework.
            return 403
        if len(files) > 10:
            return 403
        homework = sub_homework.homework_list
        file_util.save_images_in_sub_folder(files, "{}-{}".format(sub_homework.HomeworkListId, sub_homework.id))
        sub_homework.Done = True
        update_homework_done(homework)
        g.user.Points += get_sub_homework_add_points()
        db.session.commit()
        return 200
    return 400


# Copies the images of the sub homework the users wishes to view into a temporary folder that is hosted and returns the url to those images.
def get_sub_homework_images_url(sub_homework_id: int) -> int:
    sub_homework = get_sub_homework_from_id(sub_homework_id)
    if sub_homework:
        viewed_homework = get_viewed_homework_by_homework_id(sub_homework.HomeworkListId)
        if not view_homework(sub_homework.HomeworkListId, viewed_homework):
            if not viewed_homework:
                return 403
        sub_folder = "{}-{}".format(sub_homework.HomeworkListId, sub_homework.id)
        random_folder_string = "{0:s}{1:s}".format(sub_folder, random_string(10))
        copy_to_folder = os.path.join(app.config['TEMP_IMAGE_FOLDER'], random_folder_string)
        file_util.copy_sub_images(sub_folder, copy_to_folder)
        image_count_total = file_util.get_image_count_in_sub_folder(sub_folder)
        file_util.delete_temp_sub_image_folder(max(min(image_count_total/4, 30), app.config["DEL_TEMP_SUB_IMAGES_WAIT_TIME"]), copy_to_folder) # start thread that waits a given amount of seconds and then deletes the temporary folder
        g.data["images_url"] = "assets/temp_homework_files/{0:s}".format(random_folder_string)
        g.data["images_total"] = image_count_total
        return 200
    return 400


# Returns the images of the sub homework the users wishes to view as base64.
def get_sub_homework_base64_images(sub_homework_id : int) -> int:
    sub_homework = get_sub_homework_from_id(sub_homework_id)
    if sub_homework:
        viewed_homework = get_viewed_homework_by_homework_id(sub_homework.HomeworkListId)
        if not view_homework(sub_homework.HomeworkListId, viewed_homework):
            if not viewed_homework:
                return 403
        sub_folder = "{}-{}".format(sub_homework.HomeworkListId, sub_homework.id)
        base64_images = file_util.get_images_in_sub_folder_as_base64(sub_folder)
        g.data["base64_images"] = base64_images
        g.data["images_total"] = len(base64_images)
        return 200
    return 400


# Removes all uploaded images of the specified sub homework and de-registers the registered user.
def reset_sub_homework(sub_homework: SubHomeworkLists):
    sub_homework.Done = False
    sub_homework.UserId = None
    homework = sub_homework.homework_list
    update_homework_done(homework)
    sub_folder = "{}-{}".format(sub_homework.HomeworkListId, sub_homework.id)
    count = file_util.get_image_count_in_sub_folder(sub_folder)
    if count > 0:
        file_util.remove_sub_folder(sub_folder)
    db.session.commit()



from .db_mod import has_reported_sub_homework
from .db_user import user_to_dict, get_user_by_id
from .db_homework import update_homework_done, get_viewed_homework_by_homework_id, view_homework