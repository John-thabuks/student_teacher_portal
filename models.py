from config import bcrypt, db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property

class Student(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password = db.Column(db.String(), nullable=False)
    courses = db.relationship('Course', secondary='student_courses', backref=db.backref('students', lazy='dynamic'))
    messages = db.relationship('Message', backref='student', lazy='dynamic')

    serialize_only = ("email", "username")
    #getter for our  _password
    @hybrid_property
    def password_hash(self):
        return self._password
    
    #setter for our _password
    @password_hash.setter   
    def password_hash(self, user_password):
        new_password_hash = bcrypt.generate_password_hash(user_password.encode("utf-8"))
        self._password = new_password_hash.decode("utf-8")

    #authenticate method :-> used to compare user's password to _password_hash
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password, password.encode("utf-8"))


class Admin(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column(db.String(), nullable=False)
    courses = db.relationship('Course', secondary='admin_courses', backref=db.backref('admins', lazy='dynamic'))

    #getter for our  _password
    @hybrid_property
    def password_hash(self):
        return self._password
    
    #setter for our _password
    @password_hash.setter   
    def password_hash(self, user_password):
        new_password_hash = bcrypt.generate_password_hash(user_password.encode("utf-8"))
        self._password = new_password_hash.decode("utf-8")

    #authenticate method :-> used to compare user's password to _password_hash
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password, password.encode("utf-8"))

    serialize_only = ("email",)

class Course(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.String(120), nullable=True)
    price = db.Column(db.Float, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    modules = db.relationship('Module', backref='course', lazy=True)

    serialize_only = (title, description, thumbnail, price, admin_id)
class Module(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    media = db.Column(db.String(120), nullable=False) # Assuming media is a path to the file
    notes = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    serialize_only = ("title", "media","notes", "course_id")

class Message(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    serialize_only = ("title", "content", "student_id")

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
