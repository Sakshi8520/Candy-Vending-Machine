from flask import Blueprint,request,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import (JWTManager,create_access_token,jwt_required,get_jwt_identity)
from app.extensions import db
from app.models import User,Candy,UserCandyTransaction,Ticket,Wallet,Ledger
from app.exceptions import UserNotFoundError
from app.extensions import limiter
from app.decorators import admin_required

admin_bp = Blueprint("admin",__name__)
@admin_bp.route("/test")
def create_admin():
	existing_admin = User.query.filter_by(username="admin").first()
	if existing_admin:
		return jsonify({"msg":"Admin already exists"})
	admin = User(username="admin",
		password = generate_password_hash("admin1235"),
		is_admin = True)
	db.session.add(admin)
	db.session.commit()
	return jsonify({"msg":"Admin created"})

@admin_bp.route("/candy/add",methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def add_candy():
	username = get_jwt_identity()
	user = User.query.filter_by(username=username).first()
	print(user.is_admin)
	if not user.is_admin:
		return jsonify({"msg":"Access denied, admins only"}),403
	data = request.get_json()
	candy_name = data.get("candy_name")
	price = data.get("price")
	stock = data.get("stock")
	candy_stock = Candy(
		candy_name = candy_name,
		price = price,
		stock = stock)
	db.session.add(candy_stock)
	db.session.commit()
	print("After commit:",Candy.query.all())
	return jsonify({"msg":f'Candy {candy_stock.candy_name} added successfully'})

@admin_bp.route("/stock/view",methods=["GET"])
@jwt_required()
@limiter.limit("100 per minute")
def view_stock():
	username = get_jwt_identity()
	user = User.query.filter_by(username=username).first()
	if not user.is_admin:
		return jsonify({"msg":"Access denied, admins only"}),403
	stock = Candy.query.all()
	stock_list = []
	print("All candies:",Candy.query.all())
	print("Count:",Candy.query.count())
	for candy in stock:
		stock_list.append({
			"candy_name" : candy.candy_name,
		"price" : candy.price,
		"stock" : candy.stock
			})
	return jsonify({"stock": stock_list})

@admin_bp.route("/users/get/<int:id>",methods=["GET"])
def get_users(id):
	user = User.query.filter_by(id=id).first()
	if user:
		return jsonify({
			"data": {"username": user.username}})
	else:
		raise UserNotFoundError()

@admin_bp.get("/test_admin")
@jwt_required()
@admin_required
def test_admin():
	return {"message":"Welcome admin!"}