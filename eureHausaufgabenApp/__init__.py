from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import binascii
from Cryptodome import Random


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