from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from .util.file_util import delete_all_temp_sub_image_folders
from flask import has_request_context, request
from flask.logging import default_handler
import logging
from logging.handlers import RotatingFileHandler
import os

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


def setup_logging_handler() -> RotatingFileHandler:
    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s %(levelname)s in %(module)s: %(message)s'
    )

    file_logging_handler = RotatingFileHandler(
        filename="logs/flask_app.log",
        maxBytes=10000,
        encoding="utf-8"
    )
    file_logging_handler.setFormatter(formatter)
    file_logging_handler.setLevel(logging.WARN)
    default_handler.setFormatter(formatter)
    return file_logging_handler


# Create flask app
app = Flask(__name__)
# Set logging handler
app.logger.addHandler(setup_logging_handler())
app.logger.setLevel(logging.DEBUG)

# Load config.py
app.config.from_object('config')

# Set Database URI based on environment variables and config.py
if "USE_PRODUCTION_DB" in os.environ:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASSWORD']}@{os.environ['MYSQL_HOST']}/{os.environ['MYSQL_DATABASE']}"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DEBUG_SQLALCHEMY_DATABASE_URI"]

# Set Temp image folder based on environment variables  and config.py
if "TEMP_IMAGE_FOLDER" in os.environ:
    app.config["TEMP_IMAGE_FOLDER"] = os.environ["TEMP_IMAGE_FOLDER"]
else:
    app.config["TEMP_IMAGE_FOLDER"] = app.config["DEBUG_TEMP_IMAGE_FOLDER"]

# Setup the database
db = SQLAlchemy(app)
from .models import *
db.create_all()

# Setup auto CORS headers
CORS(app)

# Import blueprints
from .views.authentication import authentication
from .views.user import user
from .views.homework import homework
from .views.mod_dashboard import mod_dashboard
from .views.knowledge import knowledge
from .views.admin_dashboard import admin_dashboard
from .views.owner_info import owner_info
from .views.sub_homework import sub_homework

# Initialize blueprints
app.register_blueprint(authentication)
app.register_blueprint(user)
app.register_blueprint(homework)
app.register_blueprint(sub_homework)
app.register_blueprint(mod_dashboard)
# app.register_blueprint(knowledge) Deactivated for now
app.register_blueprint(admin_dashboard)
app.register_blueprint(owner_info)

# Auto delete temp folders at startup
delete_all_temp_sub_image_folders(app.config["TEMP_IMAGE_FOLDER"], ["img"])

# Create temporary admin setup user if in setup mode or remove that admin user if not in setup mode.
with app.app_context():
    from .DB import db_user, db_school
    if "SETUP_MODE" in os.environ or (not "SETUP_MODE" in os.environ and app.config["DEBUG_SETUP_MODE"]):
        app.logger.warning("SETUP_MODE is on, if using in production please turn this off after the setup immediately.")
        db_school.add_school(app.config["SETUP_MODE_ADMIN_SCHOOL_NAME"])
        result = db_user.setup_user(app.config["SETUP_MODE_ADMIN_USERNAME"], app.config["SETUP_MODE_ADMIN_SCHOOL_NAME"], use_g_data=False)
        if result[0] == 200:
            data = result[1]
            if not "user_already_exists" in data:
                user = db_user.get_user_by_id(data["new_user_id"]).Role = 4
                db.session.commit()
                app.logger.info(f"setup sign in token : {data['new_first_time_sign_in_token']}")
    else:
        school = db_school.get_school_by_name(app.config["SETUP_MODE_ADMIN_SCHOOL_NAME"])
        if school:
            db_school.remove_school_by_id(school.id)