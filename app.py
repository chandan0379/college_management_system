from re import search

from flask import Flask, render_template, request, redirect, session
from database import db
from models import Student, Teacher

app = Flask(__name__)
app.secret_key = "college_management_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///college.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
        password = request.form["password"]

        student = Student(
            name=name,
            email=email,
            department=department,
            password=password
        )

        db.session.add(student)
        db.session.commit()

        return redirect("/admin")

    return render_template("register.html")

@app.route("/admin")
def admin():

    search = request.args.get("search")

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
        student_name=student.name,
        attendance=student.attendance,
        marks=student.marks,
        courses=student.courses,
        department=student.department,
        semester=student.semester
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
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/teacher_logout")
def teacher_logout():

    session.pop("teacher_id", None)

    return redirect("/teacher_login")

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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
    