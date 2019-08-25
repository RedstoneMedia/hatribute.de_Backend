import os
import time
from PIL import Image
from base64 import decodebytes


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

            if image_type_info[1] != "png":
                im = Image.open(image_path)
                im.save("Homework\\{}.png".format(image_name))
                del im
                if os.path.isfile(image_path):
                    for i in range(0, 10):
                        try:
                            os.remove(image_path)
                            break
                        except PermissionError:
                            time.sleep(0.1)
            return True
        return False
    except Exception as e:
        return e