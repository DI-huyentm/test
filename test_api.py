import unittest
import json
from app import Student, db, app

class TestAPI(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        self.student_data = {
            "name": "Huyen",
            "gender": 0,
            "school": "HUST"
        }
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_student(self):
        response = self.app.post('/create_student', json=self.student_data)
        self.assertEqual(response.status_code, 201)

        with app.app_context():
            student = Student.query.filter_by(name=self.student_data["name"]).first()
            self.assertIsNotNone(student)

    def test_get_students(self):
        with app.app_context():
            new_student = Student(name="Huyen", gender=0, school="HUST")
            db.session.add(new_student)
            db.session.commit()

        response = self.app.get('/students')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data["students"]) > 0)

    def test_update_student(self):
        with app.app_context():
            new_student = Student(name="Huyen", gender=0, school="HUST")
            db.session.add(new_student)
            db.session.commit()

        update_data = {
            "name": "Updated Name",
            "gender": "Male"
        }

        response = self.app.patch('/update_student/1', json=update_data)
        self.assertEqual(response.status_code, 200)

        with app.app_context():
            updated_student = Student.query.filter_by(id=1).first()
            self.assertEqual(updated_student.name, update_data["name"])
            self.assertEqual(updated_student.gender, update_data["gender"])

    def test_delete_student(self):
        with app.app_context():
            new_student = Student(name="Huyen", gender=0, school="HUST")
            db.session.add(new_student)
            db.session.commit()

        response = self.app.delete('/delete_student/1')
        self.assertEqual(response.status_code, 200)

        # Check if the student is actually deleted from the database
        with app.app_context():
            deleted_student = Student.query.filter_by(id=1).first()
            self.assertIsNone(deleted_student)

if __name__ == '__main__':
    unittest.main()
