from config import bcrypt, db

# from sqlalchemy_serializer import SerializerMixin
# from sqlalchemy import DateTime
# import datetime
# from sqlalchemy.ext.hybrid import hybrid_property

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    courses = db.relationship('Course', secondary='student_courses', backref=db.backref('students', lazy='dynamic'))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    courses = db.relationship('Course', secondary='admin_courses', backref=db.backref('admins', lazy='dynamic'))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.String(120), nullable=True)
    price = db.Column(db.Float, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    modules = db.relationship('Module', backref='course', lazy=True)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    media = db.Column(db.String(120), nullable=False) # Assuming media is a path to the file
    notes = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

# Association table for Student-Course many-to-many relationship
student_courses = db.Table('student_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

# Association table for Admin-Course many-to-many relationship
admin_courses = db.Table('admin_courses',
    db.Column('admin_id', db.Integer, db.ForeignKey('admin.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

 