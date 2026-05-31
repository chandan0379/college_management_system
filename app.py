from flask import Flask, render_template, request, redirect, session
from database import db
from models import Student

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

        return "Student Registered Successfully!"

    return render_template("register.html")

@app.route("/admin")
def admin():
    return render_template("admin_dashboard.html")

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

@app.route("/teacher")
def teacher():
    return render_template("teacher_dashboard.html")

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
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
    