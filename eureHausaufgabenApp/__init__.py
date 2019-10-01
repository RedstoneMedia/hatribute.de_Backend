from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import binascii
from Cryptodome import Random
from .util.file_util import delete_all_temp_sub_image_folders
import shutil
import os


app = Flask(__name__)
app.config.from_object('config')
app.config["secret-key"] = binascii.hexlify(Random.new().read(64))
db = SQLAlchemy(app)
CORS(app)
from .models import Users
db.create_all()
from .views.authentication import authentication
from .views.homework import homework
from .views.modDashboard import modDashboard
app.register_blueprint(authentication)
app.register_blueprint(homework)
app.register_blueprint(modDashboard)

delete_all_temp_sub_image_folders(app.config["TEMP_IMAGE_FOLDER"], ["img"]) # auto delete temp folders at startup