from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    def __repr__(self):
        return f"<User {self.username}>"

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Active')

    def __repr__(self):
        return f"<Asset {self.name}>"
