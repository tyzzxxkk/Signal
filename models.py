from extensions import db
from flask_login import UserMixin
import datetime 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    love_histories = db.relationship('LoveHistory', backref='user', lazy=True)
    name = db.Column(db.String(100), nullable=True)

class Letter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    receiver_email = db.Column(db.String(120), nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', backref='sent_letters', foreign_keys=[sender_id])

    def __repr__(self):
        return f"<Letter from {self.sender_name} to {self.receiver_email}>"

class LoveHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name1 = db.Column(db.String(60), nullable=False)
    name2 = db.Column(db.String(60), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(500), nullable=False) 
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<LoveHistory {self.name1} & {self.name2} ({self.score}%)>"