DEBUG_SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:test@localhost/eure_hausaufgaben_db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG_TEMP_IMAGE_FOLDER = "temp_homework_files"
SESSION_EXPIRE_TIME_MINUTES = 10
SESSION_EXPIRE_TIME_STAY_LOGGED_IN_DAYS = 62
DEL_TEMP_SUB_IMAGES_WAIT_TIME = 30  # the amount of seconds to wait until deleting the temporary images
REALLY_OLD_SESSIONS_DELETE_AFTER_EXPIRE_DAYS = 1
SESSION_PER_USER_LIMIT = 3