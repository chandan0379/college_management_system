from re import search
from flask import Flask, render_template, request, redirect, session
import werkzeug
from database import db
from datetime import datetime, timedelta
from models import Student, Teacher, Book, IssuedBook, Librarian, StudyResource, Assignment, Submission, Exam, Question, StudentAnswer, Result, ResultAnswer
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import os
load_dotenv()
from groq import Groq
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
import smtplib
import random
from email.mime.text import MIMEText
from models import *

app = Flask(__name__)
app.secret_key = "college_management_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///college.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create uploads directories if they don't exist
os.makedirs(os.path.join(app.root_path, "static/uploads/photos"), exist_ok=True)
os.makedirs(os.path.join(app.root_path, "static/uploads/signatures"), exist_ok=True)

db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        student = Student.query.filter_by(
            email=email,
            password=password
        ).first()

        if student:
            session["student_name"] = student.name
            session["student_id"] = student.id
            session["student_department"] = student.department
            return redirect("/student")

        return "Invalid Email or Password"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        roll_number = request.form["roll_number"]
        password = request.form["password"]

        student = Student(
            name=name,
            email=email,
            roll_number=roll_number,
            department=department,
            password=password
        )

        db.session.add(student)
        db.session.commit()

        return redirect("/admin")

    return render_template("register.html")

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin"] = True
            return redirect("/admin")

        return "Invalid Admin Credentials"

    return render_template("admin_login.html")

@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect("/admin_login")

    search = request.args.get("search")

    teachers = Teacher.query.all()
    librarians = Librarian.query.all()

    if search:
        students = Student.query.filter(
            Student.name.contains(search)
        ).all()
    else:
        students = Student.query.all()

    total_students = len(students)
    total_teachers = Teacher.query.count()
    total_librarians = Librarian.query.count()
    total_books = Book.query.count()


    cse_students = Student.query.filter_by(
        department="CSE"
    ).count()

    it_students = Student.query.filter_by(
        department="IT"
    ).count()

    ece_students = Student.query.filter_by(
        department="ECE"
    ).count()

    me_students = Student.query.filter_by(
        department="ME"
    ).count()

    csds_students = Student.query.filter_by(
        department="CSDS"
    ).count()

    ee_students = Student.query.filter_by(
        department="EE"
    ).count()

    # Department Wise Teachers

    cse_teachers = Teacher.query.filter_by(
        subject="CSE"
    ).count()

    it_teachers = Teacher.query.filter_by(
        subject="IT"
    ).count()

    ece_teachers = Teacher.query.filter_by(
        subject="ECE"
    ).count()

    me_teachers = Teacher.query.filter_by(
        subject="ME"
    ).count()

    csds_teachers = Teacher.query.filter_by(
        subject="CSDS"
    ).count()

    ee_teachers = Teacher.query.filter_by(
        subject="EE"
    ).count()

    if total_students > 0:

        avg_attendance = sum(
            s.attendance for s in students
        ) / total_students

        avg_marks = sum(
            s.marks for s in students
        ) / total_students

    else:

        avg_attendance = 0
        avg_marks = 0

    return render_template(
        "admin_dashboard.html",

        students=students,
        teachers=teachers,
        librarians=librarians,

        total_students=total_students,
        total_teachers=total_teachers,
        total_librarians=total_librarians,
        total_books=total_books,

        avg_attendance=round(avg_attendance, 1),
        avg_marks=round(avg_marks, 1),

        cse_students=cse_students,
        it_students=it_students,
        ece_students=ece_students,
        me_students=me_students,
        csds_students=csds_students,
        ee_students=ee_students,

        cse_teachers=cse_teachers,
        it_teachers=it_teachers,
        ece_teachers=ece_teachers,
        me_teachers=me_teachers,
        csds_teachers=csds_teachers,
        ee_teachers=ee_teachers
    )



@app.route("/delete_librarian/<int:id>")
def delete_librarian(id):

    librarian = Librarian.query.get(id)

    db.session.delete(librarian)
    db.session.commit()

    return redirect("/admin")

@app.route("/edit_librarian/<int:id>", methods=["GET", "POST"])
def edit_librarian(id):

    librarian = Librarian.query.get(id)

    if request.method == "POST":

        librarian.username = request.form["username"]
        librarian.password = request.form["password"]

        db.session.commit()

        return redirect("/admin")

    return render_template(
        "edit_librarian.html",
        librarian=librarian
    )


@app.route("/student")
def student():

    if "student_id" not in session:
        return redirect("/login")

    student = Student.query.get(session["student_id"])

    return render_template(
        "student_dashboard.html",
        student=student
    )
@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    student = Student.query.get_or_404(id)

    if request.method == "POST":

        student.name = request.form["name"]
        student.department = request.form["department"]
        student.attendance = request.form["attendance"]
        student.marks = request.form["marks"]
        student.semester = request.form["semester"]

        db.session.commit()

        return redirect("/admin")

    return render_template(
        "edit_student.html",
        student=student
    )

@app.route("/teachers")
def teachers():

    teachers = Teacher.query.all()

    return render_template(
        "teacher_dashboard.html",
        teachers=teachers
    )


@app.route("/add_teacher", methods=["GET", "POST"])
def add_teacher():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]   # NEW
        subject = request.form["subject"]
        password = request.form["password"]

        teacher = Teacher(

            name=name,
            email=email,
            department=department,   # NEW
            subject=subject,
            password=password

        )

        db.session.add(teacher)
        db.session.commit()

        return redirect("/teachers")

    return render_template("add_teacher.html")

@app.route("/upload_resource", methods=["GET", "POST"])
def upload_resource():

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    teacher = Teacher.query.get(session["teacher_id"])

    if request.method == "POST":

        title = request.form["title"]
        subject = request.form["subject"]

        pdf = request.files["pdf"]

        filename = pdf.filename

        pdf.save(
            "static/uploads/resources/" + filename
        )

        resource = StudyResource(

            title=title,

            subject=subject,

            department=teacher.department,   # Auto Department

            filename=filename

        )

        db.session.add(resource)
        db.session.commit()

        return redirect("/teacher_panel")

    return render_template("upload_resource.html")

@app.route("/study_resources")
def study_resources():

    resources = StudyResource.query.all()

    return render_template(
        "study_resources.html",
        resources=resources
    )

@app.route("/delete_student/<int:id>")
def delete_student(id):

    student = Student.query.get_or_404(id)

    db.session.delete(student)

    db.session.commit()

    return redirect("/admin")



@app.route("/edit_teacher/<int:id>", methods=["GET", "POST"])
def edit_teacher(id):

    teacher = Teacher.query.get_or_404(id)

    if request.method == "POST":

        teacher.name = request.form["name"]
        teacher.email = request.form["email"]
        teacher.subject = request.form["subject"]

        db.session.commit()

        return redirect("/teachers")

    return render_template(
        "edit_teacher.html",
        teacher=teacher
    )

@app.route("/delete_teacher/<int:id>")
def delete_teacher(id):

    teacher = Teacher.query.get_or_404(id)

    db.session.delete(teacher)

    db.session.commit()

    return redirect("/teachers")


@app.route("/students")
def students():

    all_students = Student.query.all()

    output = ""

    for student in all_students:
        output += f"""
        <h3>{student.name}</h3>
        <p>{student.email}</p>
        <p>{student.department}</p>
        <hr>
        """

    return output

@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        teacher = Teacher.query.filter_by(
            email=email,
            password=password
        ).first()

        if teacher:

            session["teacher_id"] = teacher.id

            # Department save korchi
            session["teacher_department"] = teacher.department

            return redirect("/teacher_panel")

        return "Invalid Email or Password"

    return render_template("teacher_login.html")

@app.route("/student_login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        student = Student.query.filter_by(
            email=email,
            password=password
        ).first()

        if student:

            session["student_id"] = student.id

            return redirect("/student_dashboard")

        return "Invalid Email or Password"

    return render_template("student_login.html")

@app.route("/teacher_panel")
def teacher_panel():

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    teacher = Teacher.query.get(session["teacher_id"])

    search = request.args.get("search")

    if search:

     students = Student.query.filter(

        Student.department == session["teacher_department"],

        Student.name.contains(search)

    ).all()

    else:

     students = Student.query.filter_by(

        department=session["teacher_department"]

    ).all()

    total_students = len(students)

    if total_students > 0:
        avg_attendance = sum(s.attendance for s in students) / total_students
        avg_marks = sum(s.marks for s in students) / total_students
    else:
        avg_attendance = 0
        avg_marks = 0

    return render_template(
        "teacher_panel.html",
        teacher=teacher,
        students=students,
        total_students=total_students,
        avg_attendance=round(avg_attendance, 1),
        avg_marks=round(avg_marks, 1),
        search=search
    )

@app.route("/add_book", methods=["GET", "POST"])
def add_book():

    if request.method == "POST":

        book = Book(
            title=request.form["title"],
            author=request.form["author"],
            category=request.form["category"],
            quantity=int(request.form["quantity"])
        )

        db.session.add(book)
        db.session.commit()

        return redirect("/library")

    return render_template("add_book.html")

@app.route("/library")
def library():

    if "librarian_id" not in session:
        return redirect("/librarian_login")

    books = Book.query.all()

    return render_template(
        "library.html",
        books=books
    )
@app.route("/delete_book/<int:id>")
def delete_book(id):

    book = Book.query.get_or_404(id)

    db.session.delete(book)
    db.session.commit()

    return redirect("/library")


@app.route("/student_library")
def student_library():

    if "student_id" not in session:
        return redirect("/student_login")

    books = Book.query.all()

    return render_template(
        "student_library.html",
        books=books
    )

@app.route("/issue_book/<int:id>", methods=["GET", "POST"])
def issue_book(id):

    book = Book.query.get_or_404(id)

    students = Student.query.all()

    if request.method == "POST":

        student_id = request.form["student_id"]

        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=15)

        issued = IssuedBook(
            student_id=student_id,
            book_id=book.id,
            issue_date=issue_date.strftime("%d-%m-%Y"),
            due_date=due_date.strftime("%d-%m-%Y")
        )

        db.session.add(issued)

        if book.quantity > 0:
            book.quantity -= 1

        db.session.commit()

        return redirect("/library")

    return render_template(
        "issue_book.html",
        students=students,
        book=book
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/teacher_logout")
def teacher_logout():

    session.pop("teacher_id", None)

    return redirect("/teacher_login")

@app.route("/admin_logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin_login")

@app.route("/teacher_edit_student/<int:id>", methods=["GET", "POST"])
def teacher_edit_student(id):

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    student = Student.query.get_or_404(id)

    # Department Security
    if student.department != session["teacher_department"]:

        return "❌ Access Denied! You can only manage students from your own department.", 403

    if request.method == "POST":

        student.attendance = int(request.form["attendance"])
        student.marks = int(request.form["marks"])

        db.session.commit()

        return redirect("/teacher_panel")

    return render_template(
        "teacher_edit_student.html",
        student=student
    )

@app.route("/student_dashboard")
def student_dashboard():

    if "student_id" not in session:
        return redirect("/student_login")

    print("Current Student ID =", session["student_id"])

    student = Student.query.get(session["student_id"])

    results = Result.query.filter_by(
        student_id=student.id
    ).order_by(Result.id.desc()).all()

    return render_template(
        "student_dashboard.html",
        student=student,
        results=results
    )

@app.route("/student_profile", methods=["GET", "POST"])
def student_profile():

    if "student_id" not in session:
        return redirect("/student_login")

    student = Student.query.get(session["student_id"])

    if request.method == "POST":

        photo = request.files.get("photo")
        signature = request.files.get("signature")

        if photo and photo.filename != "":

            photo_filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.root_path,
                    "static/uploads/photos",
                    photo_filename
                )
            )

            student.photo = photo_filename

        if signature and signature.filename != "":

            signature_filename = secure_filename(signature.filename)

            signature.save(
                os.path.join(
                    app.root_path,
                    "static/uploads/signatures",
                    signature_filename
                )
            )

            student.signature = signature_filename

        db.session.commit()

        return redirect("/student_profile")

    return render_template(
        "student_profile.html",
        student=student
    )

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if "student_id" not in session:
        return redirect("/student_login")

    student = Student.query.get(session["student_id"])

    if request.method == "POST":

        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        if student.password == old_password:

            student.password = new_password

            db.session.commit()

            return redirect("/student")

        return "Old Password Incorrect"

    return render_template("change_password.html")

@app.route("/librarian_login", methods=["GET", "POST"])
def librarian_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        librarian = Librarian.query.filter_by(
            username=username,
            password=password
        ).first()

        if librarian:
            session["librarian_id"] = librarian.id
            return redirect("/library")

        return "Invalid Login"

    return render_template("librarian_login.html")

@app.route("/create_librarian")
def create_librarian():

    librarian = Librarian(
        username="librarian",
        password="1234"
    )

    db.session.add(librarian)
    db.session.commit()

    return "Librarian Created"

@app.route("/test_librarian")
def test_librarian():

    librarians = Librarian.query.all()

    return str(len(librarians))

@app.route("/add_librarian", methods=["GET", "POST"])
def add_librarian():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        librarian = Librarian(
            username=username,
            password=password
        )

        db.session.add(librarian)
        db.session.commit()

        return redirect("/admin")

    return render_template("add_librarian.html")

@app.route("/issued_books")
def issued_books():

    if "student_id" not in session:
        return redirect("/student_login")

    student_id = session["student_id"]

    books = IssuedBook.query.filter_by(
        student_id=student_id
    ).all()

    return render_template(
        "issued_books.html",
        books=books
    )

@app.route("/teacher_resources")
def teacher_resources():

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    resources = StudyResource.query.all()

    return render_template(
        "teacher_resources.html",
        resources=resources
    )
@app.route("/delete_resource/<int:id>")
def delete_resource(id):

    resource = StudyResource.query.get(id)

    db.session.delete(resource)

    db.session.commit()

    return redirect("/teacher_resources")

@app.route("/edit_resource/<int:id>",
           methods=["GET", "POST"])
def edit_resource(id):

    resource = StudyResource.query.get(id)

    if request.method == "POST":

        resource.title = request.form["title"]
        resource.subject = request.form["subject"]

        db.session.commit()

        return redirect("/teacher_resources")

    return render_template(
        "edit_resource.html",
        resource=resource
    )

@app.route("/upload_assignment", methods=["GET","POST"])
def upload_assignment():

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    teacher = Teacher.query.get(session["teacher_id"])

    if request.method == "POST":

        title = request.form["title"]
        subject = request.form["subject"]

        pdf = request.files["pdf"]

        filename = pdf.filename

        pdf.save(
            "static/uploads/assignments/" + filename
        )

        assignment = Assignment(

            title=title,

            subject=subject,

            department=teacher.department,

            filename=filename

        )

        db.session.add(assignment)
        db.session.commit()

        return redirect("/teacher_panel")

    return render_template(
        "upload_assignment.html"
    )

@app.route("/assignments")
def assignments():

    if "student_id" not in session:
        return redirect("/student_login")

    student = Student.query.get(
        session["student_id"]
    )

    assignments = Assignment.query.filter_by(
        department=student.department
    ).all()

    submitted_ids = []

    submissions = Submission.query.filter_by(
        student_name=student.name
    ).all()

    for s in submissions:
        submitted_ids.append(
            s.assignment_id
        )

    return render_template(
        "assignments.html",
        assignments=assignments,
        submitted_ids=submitted_ids
    )


@app.route("/submit_assignment/<int:id>",
           methods=["GET","POST"])
def submit_assignment(id):

    if "student_id" not in session:
        return redirect("/student_login")

    assignment = Assignment.query.get(id)

    student = Student.query.get(
        session["student_id"]
    )

    if request.method == "POST":

        existing = Submission.query.filter_by(
            student_name=student.name,
            assignment_id=id
        ).first()

        if existing:
            return "Already Submitted"

        pdf = request.files["pdf"]

        filename = pdf.filename

        pdf.save(
            "static/uploads/submissions/" + filename
        )

        submission = Submission(
            student_name=student.name,
            assignment_id=id,
            filename=filename
        )

        db.session.add(submission)
        db.session.commit()

        return redirect("/assignments")

    return render_template(
        "submit_assignment.html",
        assignment=assignment
    )
@app.route("/view_submissions")
def view_submissions():

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    submissions = Submission.query.all()

    return render_template(
        "view_submissions.html",
        submissions=submissions
    )

@app.route("/create_exam", methods=["GET","POST"])
def create_exam():

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    teacher = Teacher.query.get(session["teacher_id"])

    if request.method == "POST":

        title = request.form["title"]
        subject = request.form["subject"]
        duration = request.form["duration"]

        exam = Exam(

            title=title,

            department=teacher.department,   # Automatic

            subject=subject,

            duration=duration

        )

        db.session.add(exam)
        db.session.commit()

        return redirect("/teacher_panel")

    return render_template("create_exam.html")

@app.route("/exam_list")
def exam_list():

    exams = Exam.query.all()

    return render_template(
        "exam_list.html",
        exams=exams
    )
@app.route("/add_question/<int:id>",
           methods=["GET","POST"])
def add_question(id):

    if request.method == "POST":

        question = request.form["question"]

        option_a = request.form["option_a"]

        option_b = request.form["option_b"]

        option_c = request.form["option_c"]

        option_d = request.form["option_d"]

        correct_answer = request.form["correct_answer"]

        q = Question(

            exam_id=id,

            question=question,

            option_a=option_a,

            option_b=option_b,

            option_c=option_c,

            option_d=option_d,

            correct_answer=correct_answer

        )

        db.session.add(q)

        db.session.commit()

        return redirect(f"/add_question/{id}")

    return render_template(
        "add_question.html"
    )

@app.route("/student_exams")
def student_exams():

    if "student_id" not in session:
        return redirect("/student_login")

    student = Student.query.get(session["student_id"])

    exams = Exam.query.filter_by(
        department=student.department
    ).all()

    return render_template(
        "student_exams.html",
        exams=exams
    )

@app.route("/finish_exam/<int:exam_id>")
def finish_exam(exam_id):

    if "student_id" not in session:
        return redirect("/student_login")

    questions = Question.query.filter_by(exam_id=exam_id).all()

    answers = session.get("exam_answers", {})

    score = 0

    student = Student.query.get(session["student_id"])
    exam = Exam.query.get(exam_id)

    for q in questions:

        if answers.get(str(q.id)) == q.correct_answer:
            score += 1

    percentage = round(score * 100 / len(questions), 2)

    result = Result(

        student_id=student.id,
        student_name=student.name,
        roll_number=student.roll_number,

        exam_id=exam.id,
        exam_title=exam.title,

        marks=score,
        total=len(questions),
        percentage=percentage

    )

    db.session.add(result)
    db.session.commit()

    for q in questions:

        answer = ResultAnswer(

            result_id=result.id,

            question=q.question,

            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,

            student_answer=answers.get(str(q.id)),
            correct_answer=q.correct_answer,

            is_correct=(
                answers.get(str(q.id)) == q.correct_answer
            )

        )

        db.session.add(answer)

    db.session.commit()

    session.pop("exam_answers", None)

    return redirect(f"/view_result/{result.id}")
 
@app.route("/exam/<int:exam_id>/<int:question_no>", methods=["GET","POST"])
def exam_question(exam_id, question_no):

    if "student_id" not in session:
        return redirect("/student_login")

    questions = Question.query.filter_by(
        exam_id=exam_id
    ).all()

    total_questions = len(questions)

    if total_questions == 0:
        return "No Question Found"

    if question_no > total_questions:
        return redirect(f"/finish_exam/{exam_id}")

    question = questions[question_no-1]

    progress = int(question_no*100/total_questions)

    if request.method=="POST":

        answers=session.get("exam_answers",{})

        answers[str(question.id)] = request.form.get("answer")

        session["exam_answers"]=answers

        return redirect(f"/exam/{exam_id}/{question_no+1}")

    return render_template(

        "exam_question.html",

        question=question,

        question_no=question_no,

        total_questions=total_questions,

        exam_id=exam_id,

        progress=progress

    )
@app.route("/my_result")
def my_result():

    result = Result.query.filter_by(
        student_id=session["student_id"]
    ).order_by(Result.id.desc()).first()

    return render_template(

        "my_result.html",

        result=result

    )
@app.route("/start_exam/<int:id>")
def start_exam(id):

    if "student_id" not in session:
        return redirect("/student_login")

    already = Result.query.filter_by(
        student_id=session["student_id"],
        exam_id=id
    ).first()

    if already:
        return redirect(f"/view_result/{already.id}")

    session["exam_answers"] = {}

    return redirect(f"/exam/{id}/1")

@app.route("/view_result/<int:result_id>")
def view_result(result_id):

    if "student_id" not in session:
        return redirect("/student_login")

    result = Result.query.get_or_404(result_id)

    if result.student_id != session["student_id"]:
        return "Unauthorized", 403

    answers = ResultAnswer.query.filter_by(
        result_id=result.id
    ).all()

    return render_template(
        "view_result.html",
        result=result,
        answers=answers
    )
@app.route("/exam_results")
def exam_results():

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    results = Result.query.order_by(Result.id.desc()).all()

    return render_template(
        "exam_results.html",
        results=results
    )

@app.route("/teacher_view_result/<int:result_id>")
def teacher_view_result(result_id):

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    result = Result.query.get_or_404(result_id)

    answers = ResultAnswer.query.filter_by(
        result_id=result.id
    ).all()

    return render_template(
        "teacher_view_result.html",
        result=result,
        answers=answers
    )

@app.route("/test")
def test():
    return "WORKING"

@app.route("/test_students")
def test_students():
    students = Student.query.all()
    return str(len(students))

@app.route("/test_issue")
def test_issue():
    return app.url_map.__str__()

@app.route("/test_books")
def test_books():

    books = Book.query.all()

    return str(len(books))

@app.route("/reset_exam/<int:result_id>")
def reset_exam(result_id):

    if "teacher_id" not in session:
        return redirect("/teacher_login")

    result = Result.query.get_or_404(result_id)

    # Delete answer sheet
    ResultAnswer.query.filter_by(
        result_id=result.id
    ).delete()

    # Delete student answers
    StudentAnswer.query.filter_by(
        student_id=result.student_id,
        exam_id=result.exam_id
    ).delete()

    # Delete result
    db.session.delete(result)

    db.session.commit()

    return redirect("/exam_results")


def send_otp(email, otp):

    sender = "kunduchandan240@gmail.com"

    app_password = "msir cjjw boxu mzty"

    message = MIMEText(
        f"Your College Management System OTP is {otp}"
    )

    message["Subject"] = "Password Reset OTP"

    message["From"] = sender
    message["To"] = email

    server = smtplib.SMTP("smtp.gmail.com",587)

    server.starttls()

    server.login(sender, app_password)

    server.sendmail(
        sender,
        email,
        message.as_string()
    )

    server.quit()


@app.route("/forgot_password", methods=["GET","POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        student = Student.query.filter_by(
            email=email
        ).first()

        if not student:
            return "Email Not Registered"

        otp = random.randint(100000,999999)

        session["otp"] = str(otp)

        session["reset_email"] = email

        send_otp(email, otp)

        return redirect("/verify_otp")

    return render_template("forgot_password.html")
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        user_otp = request.form["otp"]

        if user_otp == session.get("otp"):

            return redirect("/reset_password")

        return "Invalid OTP"

    return render_template("verify_otp.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():

    if "reset_email" not in session:
        return redirect("/forgot_password")

    if request.method == "POST":

        new_password = request.form["new_password"]

        student = Student.query.filter_by(
            email=session["reset_email"]
        ).first()

        if student:

            student.password = new_password

            db.session.commit()

        session.pop("otp", None)
        session.pop("reset_email", None)

        return redirect("/student_login")

    return render_template("reset_password.html")

@app.route("/ai_chat")
def ai_chat():

    if "student_id" not in session:
        return redirect("/student_login")

    chats = Chat.query.filter_by(
        student_id=session["student_id"]
    ).order_by(Chat.id.desc()).all()

    if len(chats)==0:

        chat=Chat(

            student_id=session["student_id"],

            title="New Chat"

        )

        db.session.add(chat)

        db.session.commit()

        return redirect(f"/chat/{chat.id}")

    return redirect(f"/chat/{chats[0].id}")

@app.route("/new_chat")
def new_chat():

    if "student_id" not in session:
        return redirect("/student_login")

    chat=Chat(

        student_id=session["student_id"],

        title="New Chat"

    )

    db.session.add(chat)

    db.session.commit()

    return redirect(f"/chat/{chat.id}")

@app.route("/chat/<int:id>", methods=["GET", "POST"])
def open_chat(id):

    if "student_id" not in session:
        return redirect("/student_login")

    chat = Chat.query.get_or_404(id)

    if chat.student_id != session["student_id"]:
        return "Access Denied"

    if request.method == "POST":

        question = request.form["question"]

        # Save User Message
        db.session.add(
            Message(
                chat_id=id,
                role="user",
                content=question
            )
        )
        db.session.commit()

        # Build Conversation History
        conversation = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant for college students."
            }
        ]

        old_messages = Message.query.filter_by(
            chat_id=id
        ).order_by(Message.id).all()

        for m in old_messages:
            conversation.append({
                "role": m.role,
                "content": m.content
            })

        # Ask Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation
        )

        answer = response.choices[0].message.content

        # Save AI Message
        db.session.add(
            Message(
                chat_id=id,
                role="assistant",
                content=answer
            )
        )

        # Rename Chat
        if chat.title == "New Chat":
            chat.title = question[:30]

        db.session.commit()

        return redirect(f"/chat/{id}")

    chats = Chat.query.filter_by(
        student_id=session["student_id"]
    ).order_by(Chat.id.desc()).all()

    messages = Message.query.filter_by(
        chat_id=id
    ).order_by(Message.id).all()

    return render_template(
        "ai_chat.html",
        chat=chat,
        chats=chats,
        messages=messages
    )

@app.route("/delete_chat/<int:id>")
def delete_chat(id):

    if "student_id" not in session:
        return redirect("/student_login")

    chat=Chat.query.get_or_404(id)

    if chat.student_id!=session["student_id"]:
        return "Access Denied"

    Message.query.filter_by(
        chat_id=id
    ).delete()

    db.session.delete(chat)

    db.session.commit()

    return redirect("/ai_chat")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
    