from app import db
from flask_login import UserMixin
class Seeker(db.Model, UserMixin):
    __tablename__ = "users"
    email = db.Column(db.String, nullable=False,primary_key =True)
    password = db.Column(db.String, nullable=False)
    def get_id(self):
        return self.email

class Provider(db.Model, UserMixin):
    __tablename__ = "company"
    email = db.Column(db.String, nullable=False,primary_key =True)
    password = db.Column(db.String, nullable=False)
    websiteurl = db.Column(db.String, nullable=False)
    def get_id(self):
        return self.email

class Jobs(db.Model):
    __tablename__ = "jobs"
    jid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    cemail = db.Column(db.String, nullable=False)  # Could relate to a Provider
    description = db.Column(db.String, nullable=False)

class Submission(db.Model):
    __tablename__ = "application"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    jid = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, nullable=False)  # Could relate to a Seeker
    resume = db.Column(db.String, nullable=False)  # Path to the resume file
