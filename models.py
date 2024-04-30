from config import bcrypt, db

from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import DateTime
import datetime
from sqlalchemy.ext.hybrid import hybrid_property



    

course_student =db.Table(
    "course_student",
    db.Column("student_id", db.Integer, db.ForeignKey("students.id")),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id"))
)


course_teacher = db.Table(
    "course_teacher",
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("teacher_id", db.Integer, db.ForeignKey("teachers.id"))
)


class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, unique=True, nullable=False)
    user_type = db.Column(db.String, nullable=False, default="student")

    #One to many relationship: list
    students = db.relationship("Student", backref="user")
    teachers = db.relationship("Teacher", backref="user")

    # serialize the class
    serialize_only = (name, email)

    #Lets work on hashing our password
    @hybrid_property   #This is getter
    def password_hash(self):
        return self._password_hash

    #Lets set our password
    @password_hash.setter
    def password_hash(self, password):
        new_password = bcrypt.generate_password_hash(password.encode("utf-8"))
        self._password_hash = new_password.decode("utf-8")     


    #Authentication
    def autheticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode("utf-8"))
    
class Student(db.Model, SerializerMixin):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True, unique=True)
    # ForeignKey for backref created -> User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    serialize_only =(user_id)

    #many to many raltionship -> course_student
    courses = db.relationship("Course", secondary=course_student, back_populates="students")
    

class Teacher(db.Model, SerializerMixin):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key = True, unique=True)


    # ForeignKey for backref created -> User 
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    serialize_only = (user_id)

    courses = db.relationship("Course", secondary=course_teacher, back_populates="teachers")



class Course(db.Model, SerializerMixin):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    #name of the course
    name = db.Column(db.String, nullable=False, unique=True)
    duration = db.Column(DateTime, default=datetime.timedelta(minutes=30), nullable=False)

    serialize_only = (name, duration)
    # teachers = db.Column(db.Integer, db.ForeignKey("teachers.id"))

    students = db.relationship("Student", secondary=course_student, back_populates="courses")
    teachers = db.relationship("Teacher", secondary=course_teacher, back_populates="courses")
