from distutils.log import Log
from flask import Flask  # Import the Flask class
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_wtf import CSRFProtect
from flask_login import LoginManager
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, 
            template_folder = '../templates', 
            static_folder='../static') # Create an instance of the class for our use
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = os.getenv('USER_SECRET_KEY')
    
    CORS(app)  # Enable CORS
    # Register blueprints

    from app.routes.tickets import tickets as tickets_bp
    from app.routes.auth import auth as auth_bp
    from app.routes.utils import utils as utils_bp
    from app.routes.main import main as main_bp
    app.register_blueprint(tickets_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(utils_bp)
    app.register_blueprint(main_bp)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)

    return app

