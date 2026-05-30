from database import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    department = db.Column(db.String(100))

    password = db.Column(db.String(100), nullable=False)