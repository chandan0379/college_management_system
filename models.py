from database import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    department = db.Column(db.String(100))

    password = db.Column(db.String(100), nullable=False)

    attendance = db.Column(db.Integer, default=85)
    marks = db.Column(db.Integer, default=420)
    courses = db.Column(db.Integer, default=5)
    semester = db.Column(db.String(50), default="4th Semester")
    
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    subject = db.Column(db.String(100), nullable=False)
    
    password = db.Column(db.String(100), nullable=False)

class Book(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    author = db.Column(db.String(100), nullable=False)

    category = db.Column(db.String(100), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    
class IssuedBook(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_name = db.Column(db.String(100))

    book_title = db.Column(db.String(100))