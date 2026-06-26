from flask import Blueprint,request,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from app.extensions import db
from app.models import User
from flask_jwt_extended import (JWTManager, create_access_token,jwt_required,get_jwt_identity)
auth_bp = Blueprint("auth",__name__)
@auth_bp.route("/test")
def test_auth():
    return {"message":"auth works"}
@auth_bp.route("/register",methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    hashed_password = generate_password_hash(password)
    existing_user = User.query.filter_by(password=password).first()
    if existing_user:
        return jsonify({"msg":"Username already taken"})
    new_user = User(
        username = username,
        password = hashed_password,
        email = email
    )
    if "@" not in new_user.email:
        return jsonify({"msg":"Invalid email"})
    if len(new_user.password) < 8:
        return jsonify({"msg": "Password too short"})
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "msg":"You are registered sucessfully"
        })
    

@auth_bp.route("/login",methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password,password):
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)
    return jsonify({"msg":"Wrong username or password"}),401

@auth_bp.route("/me",methods=["GET"])
@jwt_required()
def me():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as = current_user)