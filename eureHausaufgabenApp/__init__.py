from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import binascii
from Cryptodome import Random
from .util.file_util import delete_all_temp_sub_image_folders
from flask import has_request_context, request
from flask.logging import default_handler
import logging

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
default_handler.setFormatter(formatter)

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
from .views.knowledge import knowledge
app.register_blueprint(authentication)
app.register_blueprint(homework)
app.register_blueprint(modDashboard)
app.register_blueprint(knowledge)

delete_all_temp_sub_image_folders(app.config["TEMP_IMAGE_FOLDER"], ["img"]) # auto delete temp folders at startup