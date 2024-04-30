from config import app, db, make_response, request, jsonify, jwt
from models import User, Teacher, Student, Course
import datetime
from functools import wraps


#We can lock certain pages only to be accessed by logged in Users
#creation of @token_required

def token_required(f):
    @wraps
    def func(*args, **kwargs):
        token = None

        #Lets get userToken generated and assign it to the above token
        if "userToken" in request.headers:
            token = request.headers["userToken"]

        #if there is no token, return error message
        else:
            return make_response({"message":"ERROR TOKEN UNAVAILABLE"}, 403)
        
        try:
            #Lets decode the token we have received counter_check token.io
            decode_token = jwt.decode(token, app.config["SECRET_KEY"], "HS256")
            #from the decoded token use either attribute to fetch from db
            logged_user = User.query.get(decode_token["id"])
        except Exception as e:
            return make_response({"ERROR": "INVALID TOKE"}, 403)

        return f(logged_user, *args, **kwargs)
    
    return func


@app.route("/")
def hello():
    return "Hello student"


#list all courses
@token_required
@app.route("/courses")
def allcourses():
    courses = Course.query.all()
    print(courses)




#Log in 
@app.route("/login", methods=["POST"])
def login():
    #Get user inputs from the login form
    user = request.get_json()
    #Now get each field you need
    email = user["email"]
    password = user["password"]

    #Based on the above use either to fetch current user request from db
    current_user = User.query.filter_by(email=email).first()

    #If you find its in db, check credentials are correct
    if current_user:
        #Perform authentication
        if current_user.autheticate(password):
            #If that is true, generate a token for logged in user with 1hour token expiration
            generated_token = jwt.encode({
                "id": current_user.id,
                "name": current_user.name,
                "user_type":current_user.user_type,
                "expiry": datetime.datetime.now() + datetime.timedelta(minutes=60)
            },
            app.config["SECRET_KEY"], "HS256")
            
            #we return a message, the token generated and status code
            return make_response({"message": "Logged successfully", "token": generated_token}, 200)

        #If credentials are wrong
        return make_response({"message": "Worng credentials"}, 403)
    
    #if current_user == False (email not found in our db) 
    else:
        return make_response({"message": "user not Found"}, 404)



if __name__ == "__main__":
    app.run(debug=True)