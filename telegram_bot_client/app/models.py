from flask_login import UserMixin
from . import db

class Bot(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Text, unique=True)
    handle = db.Column(db.Text, unique=True)
    offset = db.Column(db.Integer, default=0)
    contacts = db.relationship('Contact', backref='bot', lazy=True)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'), nullable=False)
