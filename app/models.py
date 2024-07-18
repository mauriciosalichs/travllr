from datetime import datetime
from app import db, login
from random import randint
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

def generate_large_id(code):
    while True:
        new_id = randint(1000000000, 9999999999)
        if code == 'u' and not User.query.get(new_id):
            return new_id
        elif code == 'f' and not Friend.query.get(new_id):
            return new_id
        elif code == 't' and not Trip.query.get(new_id):
            return new_id
        elif code == 'm' and not Message.query.get(new_id):
            return new_id

class User(UserMixin, db.Model):
    id = db.Column(db.BigInteger, primary_key=True, default=lambda: generate_large_id('u'), unique=True)
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
    friends = db.relationship('Friend', backref='user', lazy=True) # Useless?
    trips = db.relationship('Trip', backref='traveler', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Friend(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, default=lambda: generate_large_id('f'), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=True)
    is_accepted = db.Column(db.Boolean, nullable=False, default=False)

class Trip(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, default=lambda: generate_large_id('t'), unique=True)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
class Message(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, default=lambda: generate_large_id('m'), unique=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, nullable=True, default=False)
    
class Location:
    def __init__(self,city,country):
        self.city = city
        self.country = country

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
