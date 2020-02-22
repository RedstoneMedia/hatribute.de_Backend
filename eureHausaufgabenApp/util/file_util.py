import os
import time
from PIL import Image
from base64 import decodebytes, b64encode
from threading import Thread
import shutil

def remove_sub_folder(sub_folder):
    shutil.rmtree("Homework\\" + sub_folder)

def get_image_count_in_sub_folder(sub_folder):
    folder_path = "Homework\\{}".format(sub_folder)
    if os.path.exists(folder_path):
        return len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])
    return 0


def copy_sub_images(sub_folder, copy_to_folder):
    folder_path = "Homework\\{}".format(sub_folder)
    if not os.path.exists(copy_to_folder):
        os.mkdir(copy_to_folder)
    else:
        return
    if os.path.exists(folder_path):
        for name in os.listdir(folder_path):
            path = os.path.join(folder_path, name)
            if os.path.isfile(path):
                shutil.copy(path, copy_to_folder, follow_symlinks=False)



def delete_temp_sub_image_folder(wait_time, temp_folder):
    if os.path.exists(temp_folder):
        t = Thread(target=_delete_temp_sub_image_folder, args=(wait_time, temp_folder, ))
        t.start()


def delete_all_temp_sub_image_folders(temp_folders_path, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = ["img"]
    if os.path.exists(temp_folders_path):
        for name in os.listdir(temp_folders_path):
            path = os.path.join(temp_folders_path, name)
            if os.path.isdir(path):
                if not name in ignore_dirs:
                    shutil.rmtree(path)


def _delete_temp_sub_image_folder(wait_time, temp_folder):
    time.sleep(wait_time)
    shutil.rmtree(temp_folder)

def get_images_in_sub_folder_as_base64(sub_folder):
    base64_images = []
    for i in range(get_image_count_in_sub_folder(sub_folder)):
        folder_path = "Homework\\{}".format(sub_folder)
        base64_images.append(get_base64image_from_path("{}\\{}.jpg".format(folder_path, i)))
    return base64_images

def get_base64image_from_path(path):
    with open(path, "rb") as image_file:
        encoded_string = b64encode(image_file.read())
    encoded_string = str(encoded_string, encoding="utf-8")
    encoded_string = "data:image/jpg;base64, {0:s}".format(encoded_string)
    return encoded_string

def save_images_in_sub_folder(images, sub_folder):
    folder_path = "Homework\\{}".format(sub_folder)
    if os.path.isdir(folder_path):
        pass
    else:
        os.mkdir(folder_path)
        for i, image in enumerate(images):
            save_image_from_b64_string(image, "{}\\{}".format(sub_folder, i))


def save_image_from_b64_string(image_data : str, image_name):
    try:
        data = image_data.split(":")
        image_info = data[1].split(";")
        image_type_info = image_info[0].split("/")
        base64 = image_info[1].split(",")
        if image_type_info[0] == "image" and base64[0] == "base64":
            base64_string = base64[1]
            image_path = "Homework\\{}.{}".format(image_name, image_type_info[1])
            with open(image_path, "wb") as fh:
                fh.write(decodebytes(bytes(base64_string, encoding="utf-8")))
            fh.close()
            im = Image.open(image_path)
            rgb_im = im.convert('RGB')  # remove alpha
            rgb_im.thumbnail((2560, 1440))  # limit image size to Q HD
            rgb_im.save("Homework\\{}.jpg".format(image_name), optimize=True, quality=60)  # save as jpg
            del im, rgb_im

            if image_type_info[1] != "jpg":
                for i in range(0, 10):
                    try:
                        os.remove(image_path)  # delete original
                        break
                    except PermissionError:
                        time.sleep(0.1)
            return True
        return False
    except Exception as e:
        return e