from database import db

class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    roll_number = db.Column(db.String(50), unique=True)

    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    department = db.Column(db.String(100))
    password = db.Column(db.String(100))

    attendance = db.Column(db.Integer, default=0)
    marks = db.Column(db.Integer, default=0)
    semester = db.Column(db.String(50))
    
    photo = db.Column(db.String(200))
    signature = db.Column(db.String(200))
    
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

    student_id = db.Column(db.Integer)

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("book.id")
    )

    book = db.relationship("Book")

    issue_date = db.Column(db.String(50))

    due_date = db.Column(db.String(50))

class Librarian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class StudyResource(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    filename = db.Column(db.String(300))

    subject = db.Column(db.String(100))

