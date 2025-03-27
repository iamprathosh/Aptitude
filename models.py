from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    question_image_filename = db.Column(db.String(255), nullable=True)  # Store image filename for complex questions
    is_diagram = db.Column(db.Boolean, default=False)  # Whether this is a diagrammatic question
    answer_type = db.Column(db.String(20), default='option')  # 'option' or 'text'
    
    # Relationship with options
    options = db.relationship('Option', backref='question', cascade='all, delete-orphan')

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)  # Store image filename for diagrammatic options
    is_image_option = db.Column(db.Boolean, default=False)  # Whether this option is an image
    
    # Relationship with votes
    votes = db.relationship('Vote', backref='option', cascade='all, delete-orphan')
    
    @property
    def vote_count(self):
        return len(self.votes)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=True)  # Can be null for text answers
    text_answer = db.Column(db.Text, nullable=True)  # For free-text answers
    session_id = db.Column(db.String(128), nullable=False)  # Store user's session ID
    question_id = db.Column(db.Integer, nullable=False)  # Store question ID for easier lookups
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
