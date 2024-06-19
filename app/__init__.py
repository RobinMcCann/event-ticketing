from flask import Flask  # Import the Flask class
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
            template_folder = '../templates', 
            static_folder='../static') # Create an instance of the class for our use
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    CORS(app)  # Enable CORS
    # Register blueprints

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    db.init_app(app)

    return app

