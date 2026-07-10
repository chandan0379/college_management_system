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

    department = db.Column(db.String(100))

    subject = db.Column(db.String(100))

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

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    subject = db.Column(db.String(100))

    filename = db.Column(db.String(300))

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_name = db.Column(db.String(100))

    assignment_id = db.Column(db.Integer)

    filename = db.Column(db.String(300))

class Exam(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    subject = db.Column(db.String(100))

    duration = db.Column(db.Integer)


class Question(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    exam_id = db.Column(db.Integer)

    question = db.Column(db.Text)

    option_a = db.Column(db.String(200))

    option_b = db.Column(db.String(200))

    option_c = db.Column(db.String(200))

    option_d = db.Column(db.String(200))

    correct_answer = db.Column(db.String(1))


class StudentAnswer(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer)

    exam_id = db.Column(db.Integer)

    question_id = db.Column(db.Integer)

    selected_option = db.Column(db.String(1))


class Result(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer)

    student_name = db.Column(db.String(100))

    roll_number = db.Column(db.String(100))

    exam_id = db.Column(db.Integer)

    exam_title = db.Column(db.String(200))

    marks = db.Column(db.Integer)

    total = db.Column(db.Integer)

    percentage = db.Column(db.Float)

class ResultAnswer(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    result_id = db.Column(db.Integer)

    question = db.Column(db.Text)

    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))

    student_answer = db.Column(db.String(1))
    correct_answer = db.Column(db.String(1))

    is_correct = db.Column(db.Boolean)

