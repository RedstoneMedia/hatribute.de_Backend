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

formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s %(levelname)s in %(module)s: %(message)s'
)

file_logging_handler = RotatingFileHandler(
    filename="logs/flask_app.log",
    maxBytes=10000,
    encoding="utf-8"
)
file_logging_handler.setFormatter(formatter)
file_logging_handler.setLevel(logging.ERROR)
default_handler.setFormatter(formatter)

app = Flask(__name__)
app.logger.addHandler(file_logging_handler)


app.config.from_object('config')

if "USE_PRODUCTION_DB" in os.environ:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASSWORD']}@{os.environ['MYSQL_HOST']}/{os.environ['MYSQL_DATABASE']}"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DEBUG_SQLALCHEMY_DATABASE_URI"]
if "TEMP_IMAGE_FOLDER" in os.environ:
    app.config["TEMP_IMAGE_FOLDER"] = os.environ["TEMP_IMAGE_FOLDER"]
else:
    app.config["TEMP_IMAGE_FOLDER"] = app.config["DEBUG_TEMP_IMAGE_FOLDER"]


db = SQLAlchemy(app)
CORS(app)
from .models import Users
db.create_all()
from .views.authentication import authentication
from .views.homework import homework
from .views.mod_dashboard import mod_dashboard
from .views.knowledge import knowledge
from .views.admin_dashboard import admin_dashboard
from .views.owner_info import owner_info
app.register_blueprint(authentication)
app.register_blueprint(homework)
app.register_blueprint(mod_dashboard)
app.register_blueprint(knowledge)
app.register_blueprint(admin_dashboard)
app.register_blueprint(owner_info)

delete_all_temp_sub_image_folders(app.config["TEMP_IMAGE_FOLDER"], ["img"]) # auto delete temp folders at startup