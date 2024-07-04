from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    image_file = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(30), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    birthdate = db.Column(db.Date)
    last_login = db.Column(db.DateTime)
    friends = db.relationship('Friend', backref='user', lazy=True)
    trips = db.relationship('Trip', backref='traveler', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)
    is_accepted = db.Column(db.Boolean, nullable=False, default=False)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
