from re import search
from flask import Flask, render_template, request, redirect, session
from database import db
from datetime import datetime, timedelta
from models import Student, Teacher, Book,IssuedBook, Librarian
from werkzeug.utils import secure_filename
import os

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

    if search:
        students = Student.query.filter(
            Student.name.contains(search)
        ).all()
    else:
        students = Student.query.all()

    total_students = len(students)
    total_teachers = Teacher.query.count()
    if total_students > 0:
        avg_attendance = sum(s.attendance for s in students) / total_students
        avg_marks = sum(s.marks for s in students) / total_students
    else:
        avg_attendance = 0
        avg_marks = 0

    return render_template(
        "admin_dashboard.html",
        students=students,
        teachers=teachers,
        total_students=total_students,
        total_teachers=total_teachers,
        avg_attendance=round(avg_attendance, 1),
        avg_marks=round(avg_marks, 1)
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
        subject = request.form["subject"]
        password = request.form["password"]

        teacher = Teacher(
          name=name,
          email=email,
          subject=subject,
          password=password
)

        db.session.add(teacher)
        db.session.commit()

        return redirect("/teachers")

    return render_template("add_teacher.html")

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
            Student.name.contains(search)
        ).all()
    else:
        students = Student.query.all()

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

    student = Student.query.get(session["student_id"])

    return render_template(
        "student_dashboard.html",
        student=student
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

 


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
    