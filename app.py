import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize SQLAlchemy with a base class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
socketio = SocketIO()

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///polls.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")

# Configure login
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import and register routes
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    from models import Admin, Question, Option, Vote
    
    # Create database tables
    db.create_all()
    
    # Initialize admin account if not exists
    from werkzeug.security import generate_password_hash
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('admin123')  # Default password, should be changed
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("Created default admin account")
    
    # Import routes
    from routes import *
