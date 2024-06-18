from flask import Flask  # Import the Flask class
from flask_cors import CORS

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)



app = Flask(__name__, template_folder = "..\\templates") # Create an instance of the class for our use
CORS(app)  # Enable CORS

from app.utils.db import db
from app import routes
from app.utils import utils

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


with app.app_context():
    db.init_app(app)
    db.create_all()