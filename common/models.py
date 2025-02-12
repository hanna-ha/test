from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    organization = db.Column(db.String(128), nullable=True)
    user_path = db.Column(db.String(200), nullable=True)
    auth_level = db.Column(db.String(128), nullable=True)
    aligner = db.Column(db.Boolean, default=False)
    diffexp = db.Column(db.Boolean, default=False)
    qc_pages = db.Column(db.Boolean, default=False)
    ssg = db.Column(db.Boolean, default=False)
    failed_attempts = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime, default=None)