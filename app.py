from flask import Flask, render_template, request, redirect
from database import db
from models import Student

app = Flask(__name__)
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
    return render_template("student_dashboard.html")

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



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
    