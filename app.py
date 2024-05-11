from config import app, db, stripe
from flask import jsonify, request, make_response, redirect, url_for
from models import Course, Student, Admin
import jwt
from functools import wraps
import datetime
from sqlalchemy.exc import IntegrityError



# Define your token_required decorator
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "jwttoken" in request.headers:
            token = request.headers["jwttoken"]
        else:
            return make_response({"ERROR": "Where is your access token"}, 403)
        try:
            decode_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")            
            current_user = Student.query.get(decode_data['id']) or Admin.query.get(decode_data['id'])

        except Exception as e:
            print(e)
            return make_response({"ERROR": "Invalid access token"}, 403)
        
        return f(current_user, *args, **kwargs)
    return decorator


#We can get all courses
@app.route('/course', methods=['GET'])
# @token_required
def get_all_courses():
    try:
        courses = Course.query.all()
        # Serialize the courses to JSON
        course_data = [{'id': course.id, 'title': course.title, 'description': course.description, 'thumbnail': course.thumbnail, 'price': course.price} for course in courses]
        return jsonify({'courses': course_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve courses', 'message': str(e)}), 500




#Log in View and route
@app.route('/login', methods=['POST'])
def login():
    user = request.get_json()    
    email = user["email"]
    password = user["password"]

    target_user = Student.query.filter_by(email=email).first() or Admin.query.filter_by(email=email).first()

    if target_user:
        if target_user.authenticate(password):   #method we defined in models for checking if password in db === <user[password]_given>
            token_generated = jwt.encode({
                "id": target_user.id, 
                "email": target_user.email,                  
                "exp": datetime.datetime.now()+datetime.timedelta(minutes=45)
                }, 
                app.config["SECRET_KEY"],"HS256")
            return make_response({"message":"Log in successful", "token":token_generated}, 200)
        
        return make_response({"message": "jokes on you. Wrong credentials"},403)

    else:
        return make_response({"message": "user not found"},404)
    

#Create a sign up view
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required!'}), 400

    email = data['email']
    password = data['password']
    user_type = data.get('user_type', 'student')  # Default to 'student' if user_type is not provided

    if user_type.lower() == 'admin':
        if Admin.query.filter_by(email=email).first():
            return jsonify({'error': 'Admin already exists!'}), 409
        user = Admin(email=email)
    else:
        username = data.get('username')
        if not username:
            return jsonify({'error': 'Username is required for students!'}), 400
        if Student.query.filter_by(email=email).first():
            return jsonify({'error': 'Student already exists!'}), 409
        user = Student(email=email, username=username)

    # Hash the password
    user.password_hash = password

    # Save the user to the database
    db.session.add(user)
    db.session.commit()

    # Generate JWT token for the new user
    token = jwt.encode({'id': user.id, 'email': user.email, 'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)},
                       app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'User created successfully!', 'token': token}), 201



# This is the Profile route for student
@app.route('/profile/student', methods=['GET', 'POST'])
@token_required
def student_profile(current_user):
    if request.method == 'GET':
        return jsonify({
            'username': current_user.username,
            'email': current_user.email
        }), 200

    elif request.method == 'POST':
        data = request.get_json()
        if 'username' in data:
            current_user.username = data['username']
        if 'password' in data:
            current_user.password_hash = data['password']
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully!'}), 200



# This is the Profile route for admin
@app.route('/profile/admin', methods=['GET', 'POST'])
@token_required
def admin_profile(current_user):
    if request.method == 'GET':
        return jsonify({
            'email': current_user.email
        }), 200

    elif request.method == 'POST':
        data = request.get_json()
        if 'password' in data:
            current_user.password_hash = data['password']
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully!'}), 200



# This will get all courses a current student is enrolled
@app.route('/courses/student', methods=['GET'])
@token_required
def get_student_courses(current_user):
    try:
        student_courses = current_user.courses
        course_data = [{'id': course.id, 'title': course.title, 'description': course.description, 'thumbnail': course.thumbnail, 'price': course.price} for course in student_courses]
        
        return jsonify({'courses': course_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve courses', 'message': str(e)}), 500


# Lets define route for retrieving courses belonging to a certain admin
@app.route('/courses/admin', methods=['GET', 'POST'])
@token_required
def admin_courses(current_user):
    if request.method == 'GET':
        admin = Admin.query.get(current_user.id)
        if not admin:
            return jsonify({'error': 'Admin not found!'}), 404

        courses = admin.courses
        course_data = [{'id': course.id, 'title': course.title, 'description': course.description, 'thumbnail': course.thumbnail, 'price': course.price} for course in courses]
        return jsonify({'courses': course_data}), 200

    elif request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('title') or not data.get('description') or not data.get('price'):
            return jsonify({'error': 'Incomplete course data!'}), 400

        new_course = Course(title=data['title'], description=data['description'], thumbnail=data.get('thumbnail'), price=data['price'], admin_id=current_user.id)
        db.session.add(new_course)
        db.session.commit()

        # Adding the created course to the admin_courses relationship table
        current_user.courses.append(new_course)
        db.session.commit()
        
        return jsonify({'message': 'Course created successfully!', 'course_id': new_course.id}), 201





# @app.route('/checkout/<int:course_id>', methods=['GET'])
# @token_required  
# def checkout(current_user, course_id):
#     # Query the course by ID
#     course = Course.query.get(course_id)
#     if not course:
#         return jsonify({'error': 'Course not found'}), 404

#     # Create a Stripe checkout session
#     try:
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[{
#                 'price_data': {
#                     'currency': 'kes',
#                     'product_data': {
#                         'name': course.title,
#                     },
#                     'unit_amount': int(course.price * 100),  # Convert price to cents
#                 },
#                 'quantity': 1,
#             }],
#             mode='payment',
#             success_url=url_for('success', _external=True),
#             cancel_url=url_for('cancel', _external=True),
#         )

#         current_user.courses.append(course)
#         db.session.commit()

#         return redirect(session.url, code=303)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # Route for successful payment
# @app.route('/success')
# def success():
#     return make_response({"message": "Successfully purchase!"})

# # Route for canceled payment
# @app.route('/cancel')
# def cancel():
#     return redirect("/course")


@app.route('/checkout/<int:course_id>', methods=['GET'])
@token_required  
def checkout(current_user, course_id):
    # Query the course by ID
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    # Check if the course price is less than or equal to 0
    # if course.price <= 0:
    #     return jsonify({'error': 'Course price must be greater than 0'}), 400
    
    # Calculate the unit_amount, ensuring it meets the minimum requirements
    unit_amount = max(int(course.price * 100), 50) 


    # Create a Stripe checkout session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': course.title,
                    },
                    'unit_amount': unit_amount,  
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )

        current_user.courses.append(course)
        db.session.commit()

        return redirect(session.url, code=303)
    except IntegrityError as e:
        # Handle the unique constraint violation
        db.session.rollback()  # Rollback the transaction
        return jsonify({'error': 'Student already enrolled in this course'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route for successful payment
@app.route('/success')
def success():
    return make_response({"message": "Successfully purchase!"})

# Route for canceled payment
@app.route('/cancel')
def cancel():
    return redirect("/course")




if __name__ == '__main__':
    app.run(port=5000, debug=True)
