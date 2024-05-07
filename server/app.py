from config import app, db, make_response, request, jsonify
from models import Student, Admin, Course, Module



@app.route("/")
def hello():
    return "Hello student"


#list all courses
@app.route("/courses")
def allcourses():
    courses = Course.query.all()
    print(courses)









if __name__ == "__main__":
    app.run(debug=True)