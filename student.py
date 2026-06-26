from flask import Flask
from flask import request
from flask import jsonify
import sqlite3

conn = sqlite3.connect("student.db")
cursor = conn.cursor()
cursor.execute("""
               CREATE TABLE IF NOT EXISTS students (
               roll_no INTEGER PRIMARY KEY,
               name TEXT)
               """)
conn.commit()
conn.close()

app = Flask(__name__)

@app.route("/")
def home():
    return "Student API"

#Create student
students = []
@app.route("/students",methods=["POST"])
def create_students():
    try:
        conn = sqlite3.connect("student.db")
        cursor = conn.cursor()
        data = request.get_json()
        #batch insert/bulk API
        for student in data:
            roll_no = student.get("roll_no")
            name = student.get("name")
        #if isinstance(data, list):
        #for student in data:
            #students.append(student)
        #else:
        #students.append(student)
        #return jsonify({
        #"message": "Student created",
        #"students": students
        #})
        cursor.execute(
        "INSERT INTO students(roll_no,name) VALUES (?,?)", (roll_no,name)
)
        conn.commit()
        conn.close()
        return jsonify({"message":"Student created",
                        "students": data})
    except Exception as e:
        return jsonify({"error":str(e)})

#Get students
@app.route("/students",methods=["GET"])
def get_students():
    #return jsonify(students)
    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return jsonify(students)
    # not needed because no DB change happened conn.commit()
    
    

#Get specific student
@app.route("/student/<int:roll_no>",methods=["GET"])
def get_student(roll_no):
    #for student in students:
        #if int(student["roll_no"]) == roll_no:
            #return jsonify(student)
        
    #return jsonify({
                #"message": "Student not found"
            #}),404
    try:
        conn = sqlite3.connect("student.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
        )
        student = cursor.fetchone()
        conn.close()
        return jsonify(student)
    except:
        return jsonify({
            "message": "Student not found"
        }),404

#Delete student
@app.route("/student/<int:roll_no>", methods=["DELETE"])
def delete_student(roll_no):
    #for student in students:
        #if student["roll_no"] == roll_no:
            #students.remove(student)
            #return jsonify({"message": "Student deleted"})
    #return jsonify({"mesage":"Student not found"}),404
    try:
        conn = sqlite3.connect("student.db")
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM students WHERE roll_no = ?", (roll_no,)
        )
        conn.commit()
        cursor.execute(
            "SELECT * FROM students"
        )
        student = cursor.fetchall()
        conn.close()
        return jsonify({"message": "Student deleted",
                        "student": student})
    except:
        return jsonify({
            "message": "no student has specified roll no"
        })
        

#Update student
@app.route("/student/<int:roll_no>",methods=["PUT"])
def update_student(roll_no):
    try: 
        conn = sqlite3.connect("student.db")
        cursor = conn.cursor()
        data = request.get_json()
        
        roll_no = data.get("roll_no")
        name = data.get("name")
        cursor.execute(
                "UPDATE students SET name = ? WHERE roll_no = ?", (name,roll_no)
            )
        conn.commit()
        cursor.execute(
            "SELECT * FROM students"
        )
        student = cursor.fetchall()
        conn.close()
        return jsonify({
            "message": f"Student with roll no {roll_no} updated",
            "student": student
        })
    except Exception as e:
        return jsonify({"error": str(e)})
        #if student["roll_no"] == roll_no:
            #student["name"] = data["name"]
            #return jsonify({
                #"message": "Student updated",
                #"student": student
            #})
    #return jsonify({"message": "Student not found"}),404

                   
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
#Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
#create ORM object
db = SQLAlchemy(app)
#models-create table using class
class Student(db.Model):
    roll_no = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), nullable=False)
#create all tables from models
with app.app_context():
    db.create_all()

@app.route("/home")
def home():
    return "working"
#ORM Create route
@app.route("/orm_students",methods=["POST"])
def create_students():
    data = request.get_json()
    for student in data:

        roll_no = student.get("roll_no")
        name =student.get("name")
    new_student = Student(
        roll_no = roll_no,
        name = name
    )
    #prepare this object for insertion
    db.session.add(new_student)
    #save it permanently
    db.session.commit()
    return jsonify({
        "message": "student created"
    })

#READ ORM
@app.route("/orm_students",methods=["GET"])
def get_students():
    students = Student.query.all()
    #serialization(convert obj tp dict/json)
    output = []
    for student in students:
        output.append({
            "roll_no": student.roll_no,
            "name": student.name
        })
    return jsonify(output)

#VIEW ORM
@app.route("/orm_student/<int:roll_no>",methods=["GET"])
def get_student(roll_no):
    try:
        student = Student.query.filter_by(roll_no=roll_no).first()
        return jsonify({
            "roll_no": student.roll_no,
            "name": student.name
        })
    except:
        return jsonify({"message":"No such student exists"})


#DELETE ORM
@app.route("/orm_student/<int:roll_no>",methods=["DELETE"])
def delete_student(roll_no):
    try:
        #find object
        student = Student.query.filter_by(roll_no=roll_no).first()
        #delete object
        db.session.delete(student)
        db.session.commit()
        return jsonify({"roll_no":student.roll_no,
                        "name":student.name,
                        "message":f"student with roll no {student.roll_no} has been deleted"})
    except:
        return jsonify({"message":"No such student exists"})
    
#UPDATE ORM
@app.route("/orm_student/<int:roll_no>",methods=["PUT"])
def update_student(roll_no):
    try:
        data = request.get_json()
        #find student
        student = Student.query.filter_by(roll_no=roll_no).first()
        new_name = data.get("name")
        student.name = new_name
        #save
        db.session.commit()
        return jsonify({
            "name": student.name,
            "roll_no": student.roll_no,
            "message":f"student with roll no {student.roll_no}'s name has been updated to {student.new_name}"
        })
    except:
        return jsonify({"message":"No such student exists"})


#ORM relationships
#One to Many
from flask import request,jsonify,Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///student.db"
db = SQLAlchemy(app)
class Student(db.Model):
    roll_no = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    marks = db.relationship("Marks",backref="student")

class Marks(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    subject = db.Column(db.String(100),nullable=False)
    marks = db.Column(db.Integer)
    student_roll_no = db.Column(db.Integer,db.ForeignKey("student.roll_no"))

with app.app_context():
    db.create_all()

@app.route("/student_data",methods=["POST"])
def student_data():
    data = request.get_json()
    for student in data:
        roll_no = student.get("roll_no")
        name = student.get("name")
    new_student = Student(
        roll_no = roll_no,
        name = name
    )
    db.session.add(new_student)
    db.session.commit()   
    return jsonify({"message": "Student created"}) 

@app.route("/marks_data",methods=["POST"])
def marks_data():
    data = request.get_json()
    
    subject = data.get("subject")
    marks = data.get("marks")
    student_roll_no = data.get("student_roll_no")
    new_mark = Marks(
    subject = subject,
    marks = marks,
    student_roll_no = student_roll_no
    )
    db.session.add(new_mark)
    db.session.commit()
    return jsonify({
        "message": "Marks Created"
    })
    
with app.app_context():
    student = Student.query.order_by(Student.roll_no).first()
    #not needed-marks = Marks.query.first()
    #print(student.name)
    #print(student.marks)
    #for mark in student.marks:
        #print(mark.subject)
        #print(mark.marks)
        

#One to one ORM
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100),nullable=False)
    profile = db.relationship("Profile",backref="user",uselist=False)

class Profile(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    bio = db.Column(db.String(100))
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
with app.app_context():
    db.create_all()

@app.route("/user",methods=["POST"])
def create_user():
    data = request.get_json()
    id = data.get("id")
    username = data.get("username")
    user = User(
        id = id,
        username = username
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"User created"})
@app.route("/profile",methods=["POST"])
def create_profile():
    data = request.get_json()
    id = data.get("id")
    bio = data.get("bio")
    user_id = data.get("user_id")
    profile = Profile(
        id = id,
        bio = bio,
        user_id = user_id
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify({"message":"Profile created"})
with app.app_context():
    user = User.query.first()
    #print(user.profile)
    #print(user.profile.bio)
    #print(user.username)
    #print(user.profile.user_id)

#Many to Many ORM relationship
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///courses.db"
db = SQLAlchemy(app)
class Students(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100),nullable=False)
    courses = db.relationship("Courses",secondary="student_course",backref="students")

class Courses(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    course_name = db.Column(db.String(100))

student_course = db.Table(
    "student_course",
    db.Column(
        "student_id",db.Integer,db.ForeignKey("students.id"),
        primary_key = True
    ),
    db.Column(
        "course_id",db.Integer,db.ForeignKey("courses.id"),
        primary_key=True
    )
)

with app.app_context():
    db.create_all()

@app.route("/students",methods=["POST"])
def create_students():
    data = request.get_json()
    id = data.get("id")
    name = data.get("name")
    students = Students(
        id = id,
        name = name
    )
    db.session.add(students)
    db.session.commit()
    return jsonify({"message":"Student created"})
@app.route("/courses",methods=["POST"])
def create_courses():
    data = request.get_json()
    id = data.get("id")
    course_name = data.get("course_name")
    courses = Courses(
        id = id,
        course_name = course_name
    )
    db.session.add(courses)
    db.session.commit()
    return jsonify({"message":"Courses created"})
with app.app_context():
    students = Students.query.first()
    courses = Courses.query.first()
    #connect objects
    students.courses.append(courses)
    #print(students.courses)
    #print(students.courses[0].course_name)

if __name__ == "__main__":
    app.run(debug=True)

