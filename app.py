from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import os

app = Flask(__name__)
CORS(app)

metrics = PrometheusMetrics(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my_flask_app.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    gender = db.Column(db.Integer, unique=False, nullable=False)
    school = db.Column(db.String(80), unique=False, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "school": self.school,
        }
    
with app.app_context():    
    db.create_all()

@app.route('/')
def hello_world():
    return "Hello World"


@app.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    json_students = list(map(lambda x: x.to_json(), students))
    return jsonify({"students": json_students})

@app.route("/create_student", methods=["POST"])
def create_student():
    name = request.json.get("name")
    gender = request.json.get("gender")
    school = request.json.get("school")

    print(name, gender, school)

    if not (name or gender or school):
        return (
            jsonify({"message": "You must include a name, gender and school"}),
            400,
        )
    
    new_student = Student(name=name, gender=gender, school=school)
    try:
        db.session.add(new_student)
        db.session.commit()
    except Exception as e:
        return (
            jsonify({"message": str(e)}),
            400,
        )
    
    return jsonify({"message": "Student created!"}), 201

@app.route("/update_student/<int:student_id>", methods=["PATCH"])
def update_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"message": "Student not found!"}), 404
    
    data = request.json
    student.name = data.get("name", student.name)
    student.gender = data.get("gender", student.gender)
    student.school = data.get("school", student.school)

    db.session.commit()

    return jsonify({"message":"Student updated!"}), 200

@app.route("/delete_student/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"message": "Student not found!"}), 404
    

    db.session.delete(student)
    db.session.commit()

    return jsonify({"message":"Student deleted!"}), 200