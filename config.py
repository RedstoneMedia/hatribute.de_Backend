DEBUG_SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:test@localhost/eure_hausaufgaben_db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG_TEMP_IMAGE_FOLDER = "temp_homework_files"
SESSION_EXPIRE_TIME_MINUTES = 5
SESSION_EXPIRE_TIME_STAY_LOGGED_IN_DAYS = 62
DEL_TEMP_SUB_IMAGES_WAIT_TIME = 30  # the amount of seconds to wait until deleting the temporary images
SESSION_PER_USER_LIMIT = 3
OWNER_INFO_PATH = "owner_info.json"