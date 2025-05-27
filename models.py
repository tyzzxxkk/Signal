from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    love_histories = db.relationship('LoveHistory', backref='user', lazy=True)

class LoveHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    name1 = db.Column(db.String(64), nullable=False)
    name2 = db.Column(db.String(64), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    msg = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LoveHistory {self.name1} ❤️ {self.name2} = {self.score}%>"
