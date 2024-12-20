from app import db
from flask_login import UserMixin

class Seeker(db.Model, UserMixin):
    __tablename__ = "users"
    sid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

class Provider(db.Model, UserMixin):
    __tablename__ = "company"
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    websiteurl = db.Column(db.String, nullable=False)

class Jobs(db.Model):
    __tablename__ = "jobs"
    jid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)  # Could relate to a Provider
    description = db.Column(db.String, nullable=False)

class Submission(db.Model):
    __tablename__ = "application"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jid = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, nullable=False)  # Could relate to a Seeker
    resume = db.Column(db.String, nullable=False)  # Path to the resume file
