from config import db, app
from models import User, Teacher, Student, Course
from faker import Faker
import random

faker = Faker()

with app.app_context():

    User.query.delete()
    Teacher.query.delete()
    Student.query.delete()
    Course.query.delete()

    

    # for _ in range(40):
        # name=faker.name()
        # userType = random.choice(["student", "teacher"])
        # email= f'{name.replace(" ", "")}@gmail.com'
        # password = f'{name.replace(" ","")}@1234'
        

        # user = User(name=name, email=email, password_hash=password,user_type=userType)
        
        # db.session.add(user)


    for _ in range(40):
        userType = random.choice(["student", "teacher"])  # Move inside the loop
        name = faker.name()
        email = f'{name.replace(" ", "")}@gmail.com'
        password = f'{name.replace(" ","")}@1234'
        
        user = User(name=name, email=email, password_hash=password, user_type = random.choice(["student", "teacher"]))
        db.session.add(user)



    for i in range(20):
        user_id = i + 1
        student = Student(user_id=user_id)
        db.session.add(student)


    for i in range(20):
        user_id = i + 21
        teacher = Teacher(user_id=user_id)
        db.session.add(teacher)

    # for i in range(20):
        # course_name = f"{faker.first_name()} course"
        # numberOfTeachers = random.randint(1,7)
        # teachers = random.sample(range(20), numberOfTeachers)
        
        # courses = Course(name=course_name, teachers=[Teacher.query.get(teacher_id) for teacher_id in teachers])
        # db.session.add(courses)
    
    for i in range(10):
        course_name = f"{faker.first_name()} course"
        
        course = Course(name=course_name)
        db.session.add(course)


    db.session.commit()

    #course_students
    all_students = db.session.query(Student).all()
    all_courses = db.session.query(Course).all()

    for student in all_students:
        student.courses.append(random.choice(all_courses))
    
    db.session.commit()

    