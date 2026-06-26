#Authentication
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(200))
with app.app_context():
    db.create_all()
#Signup route
@app.route("/signup",methods=["POST"])
def signup():
    data = request.get_json()
    #not id cause database auto generates it
    username = data.get("username")
    password = data.get("password")
    #Hash Password
    hashed_password = generate_password_hash(password)
    new_user = Users(
        username = username,
        password = hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "message":"User created"
    })

#Login route
#Sessions-
from flask import session
#create secret key bc flask signs/encrypts session data
app.secret_key = "abc123"

from werkzeug.security import check_password_hash
@app.route("/login",methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    #get hashed password-
    user = Users.query.filter_by(username=username).first()
    #if user exists
    if user:
        stored_password = user.password

        if check_password_hash(stored_password,password):
            #remember this logged in user
            session["user_id"] = user.id
            return jsonify({"message":"Login successful"})
        return jsonify({"message":"Invalid credentials"})
        
#Protected routes only valid session user_id can access-Test session
@app.route("/profile",methods=["GET"])
def profile():
    if session["user_id"]:
        return jsonify({"message":"Logged in"})
    return jsonify({"message":"Unauthorized access"})


@app.route("/profile1")
def profile1():
    #Logout - use .pop or .clear()
    #session.pop("user_id")
    #try:
        #if session["user_id"]:
            #return jsonify({"message":"Logged in"})
    #except:
        #return jsonify({"message":"Unauthorized access"})
    if session.get("user_id"):
        return jsonify({"message":"Logged in"})
    return jsonify({"message":"Unauthorized access"})

#JWT 
from flask import Flask,request,jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
#expiration of tokens
from datetime import timedelta
#secret key for aigning tokens
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
jwt = JWTManager(app)

#Login-Generate Token
@app.route("/logins",methods=["POST"])
def logins():
    username = request.json.get("username")
    password = request.json.get("password")
    user = Users.query.filter_by(username=username).first()
    #if user and user.password == password:
    if username == "admin" and password == "1234":
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    return jsonify({"msg":"bad credentials"}),401

#Protected route
@app.route("/profiles",methods=["GET"])
@jwt_required()
def profiles():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)


#Cookies
from flask import Flask, make_response, request
#Route to SET cookie
@app.route("/set")
def set_cookie():
    response = make_response("Cookie has been set!")
    response.set_cookie("username","admin")
    return response

#Route to READ cookie
@app.route("/get")
def get_cookie():
    username = request.cookies.get("username")
    return f"Cookie value: {username}"

#Route to DELETE cookie
@app.route("/delete")
def delete_cookie():
    response = make_response("Cookie deleted")
    response.delete_cookie("username")
    return response
if __name__ == "__main__":
    app.run(debug=True)
