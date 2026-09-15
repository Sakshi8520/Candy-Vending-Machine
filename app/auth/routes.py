from flask import Blueprint,request,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import (JWTManager,create_access_token,create_refresh_token,jwt_required,get_jwt_identity)
from app.extensions import db
from app.models import User,Candy,UserCandyTransaction,Ticket,Wallet,Ledger
from app.config import Config
from datetime import datetime,timedelta
from flask import request
from app.extensions import db
from app.models import User
from app.exceptions import InsufficientBalanceError
from app.exceptions import CandyNotFoundError
from app.exceptions import TicketNotFoundError
from app.exceptions import OutofStockError
from app.schemas import CandyPurchaseSchema
from app.schemas import UserSchema
from app.schemas import CandySchema
import os 
import threading
import time 
from flask import current_app, request 
from werkzeug.utils import secure_filename
import uuid
from flask import send_from_directory
from flask import url_for
from app.extensions import limiter
from flask_jwt_extended import get_jwt
from app.token_blocklist import revoked_tokens




schema = CandyPurchaseSchema()
user_schema = UserSchema()

auth_bp = Blueprint("auth",__name__)
@auth_bp.post("/test_candy")
def Test_auth():
	data = request.get_json()
	candy_id = data.get("candy_id")
	quantity = data.get("quantity")
	current_app.logger.info(f"purchase requested: candy_id={candy_id},quantity={quantity}")
	result = schema.load(data)
	return jsonify(result)

@auth_bp.get("/candies")
def get_candy():
	min_price = request.args.get("min_price",type=int)
	max_price = request.args.get("max_price",type=int)
	search = request.args.get("search")
	query = Candy.query
	if not candy:
		raise CandyNotFoundError()
	if min_price is not None:
		query = query.filter(Candy.price>=min_price)
	if max_price is not None:
		query = query.filter(Candy.price<=max_price)
	if search:
		query = query.filter(Candy.candy_name.ilike(f"%{search}%"))
	candies = query.all()
	schema = CandySchema(many=True)
	data = schema.dump(candies)
	return jsonify({
		"data":data
		})

@auth_bp.post("/candies/<int:candy_id>/image")
@limiter.limit("5 per minute")
def upload_candy_image(candy_id):
	candy = Candy.query.get(candy_id)
	if not candy:
		return jsonify({"error":"Candy not found"}),404
	file = request.files.get("file")
	if not file:
		return {"error":"No file uploaded"},400
	filename = secure_filename(file.filename)
	if not filename:
		return {"error":"Invalid filename"},400
	upload_folder = os.path.join(current_app.root_path,"uploads")
	os.makedirs(upload_folder,exist_ok=True)
	file_path = os.path.join(upload_folder,filename)
	file.save(file_path)
	candy.image_filename = filename
	db.session.commit()
	return {
		"candy_id":candy_id,
		"filename":candy.image_filename,
		"message":"Candy Image uploaded successfully"
	},201

#Return uploaded files
@auth_bp.get("/get_candies/<int:candy_id>/image")
def get_candy_image(candy_id):
	candy = Candy.query.get(candy_id)
	if not candy:
		return jsonify({"error":"Candy not found"}),404
	if not candy.image_filename:
		return {"error":"Candy has no image"},404
	upload_folder = os.path.join(current_app.root_path,"uploads")
	return {
	"id":candy.id,
	"candy_name":candy.candy_name,
	"image_url": url_for("auth.get_candy_image",candy_id=candy.id)
	}


@auth_bp.get("/pagination")
@limiter.limit("30 per minute")
def pagination():
	page = request.args.get("page",1,type=int)
	per_page = request.args.get("per_page",2,type=int)
	search = request.args.get("search")
	if page < 1:
		return {"error":"Page must be atleast 1"},400
	if per_page < 1 or per_page > 50:
		return {"error":"per_page must be between 1 and 50"},400

	query = Candy.query
	if search:
		query = query.filter(Candy.candy_name.ilike(f"%{search}%"))
		
	candies = query.order_by(Candy.id).paginate(page=page,per_page=per_page)
	#If page doesnt exists
	if page > candies.pages and candies.total > 0:
		return {"error":"Page not found"},404
	schema = CandySchema(many=True)
	#many=True means list of candies(multiple objects)
	return {
	"pagination":{
	"page":candies.page,
	"per_page":candies.per_page,
	"total": candies.total,
	"pages": candies.pages,
	"has_next": candies.has_next,
	"has_prev": candies.has_prev,
	"next_num": candies.next_num,
	"prev_num": candies.prev_num},
	"data": schema.dump(candies.items)
	}




#Sign up
@auth_bp.route("/sign_up",methods=["POST"])
@limiter.limit("5 per minute")
def sign_up():
	data = request.get_json()
	username = data.get("username")
	password = data.get("password")
	hashed_password = generate_password_hash(password)
	existing_user = User.query.filter_by(username=username).first()
	print("Username received:", username)
	print("Existing user:", existing_user)
	if existing_user:
		return jsonify({"message":"Username already taken"})
	new_user = User(
		username=username,
		password=hashed_password)
	if len(password)<8:
		return jsonify({"msg":"Password too short!"})
	new_wallet = Wallet(
		balance = Config.WELCOME_BONUS)
	new_user.wallet = new_wallet
	db.session.add(new_user)
	db.session.add(new_wallet)
	db.session.commit()
	print(new_user.id)
	print(new_wallet.id,new_wallet.user_id,new_wallet.balance)
	current_app.logger.info(f"User {user.id} created their account and got a {new_wallet.balance} worth welcome bonus")

	return jsonify({"msg":f'You are registered successfully {new_user.username}, you got a {new_wallet.balance} worth welcome bonus'})



#Log in
@auth_bp.route("/users/log_in",methods=["POST"])
@limiter.limit("5 per minute")
def log_in():
	data = request.get_json()
	username = data.get("username")
	password = data.get("password")
	print("Username enetered:", username)
	user = User.query.filter_by(username=username).first()
	print("User object:", user)

	if user:
		if check_password_hash(user.password,password):
			access_token = create_access_token(identity=username)
			refresh_token = create_refresh_token(identity=username)
			return jsonify({"access_token":access_token,
				 "refresh_token":refresh_token})
		return jsonify({"msg":"Wrong username or password"}),401
	return jsonify({"msg":"username doesn't exists,please sign up"})

#Logout
@auth_bp.post("/users/logout")
@jwt_required()
def logout():
	jti = get_jwt()["jti"]
	revoked_tokens.add(jti)
	return {"message":"successfully logged out"}

#Refresh token logout
@auth_bp.post("/logout/refresh")
@jwt_required()
def logout_refresh():
	jti = get_jwt()["jti"]
	revoked_tokens.add(jti)
	return {"message":"Refresh token revoked"}


#Refresh route
@auth_bp.post("/login/refresh")
@jwt_required(refresh=True)
def refresh():
	username = get_jwt_identity()
	new_access_token = create_access_token(identity=username)
	return {
	"access_token":new_access_token
	}
	
@auth_bp.route("/users/me",methods=["GET"])
@jwt_required()
def me():
	current_user = get_jwt_identity()
	return jsonify(logged_in_as = current_user)
			

@auth_bp.route("/candy/purchase",methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def buy_candy():
	current_user = get_jwt_identity()
	data = request.get_json()
	candy_name = data.get("candy_name")
	try:
		quantity = int(data.get("quantity"))
	except (TypeError, ValueError):
		return jsonify({"msg":"Invalid quantity"}),400
	if quantity <= 0:
		return jsonify({"msg":"quantity must be greater than 0"}),400
	
	try:
		user = User.query.filter_by(username=current_user).first

		if not user:
			return jsonify({"msg":"User not found"}),404

		#Locking candy first
		candy = (Candy.query.filter_by(candy_name=candy_name).with_for_update().first())
		if not candy:
			raise CandyNotFoundError()
			current_app.logger.warning(f"Candy not found: candy_id={candy_id}")
		#Refresh wallet with a lock (lock candy first then candy and not change this sequence to avoid deadlock)

		wallet = (Wallet.query.filter_by(user_id=user.id).with_for_update().first())
		if not wallet:
			return jsonify({"msg":"Wallet not found"}),404

		
		
		#Check locked values
		if candy.stock < quantity:
			raise OutofStockError()

		total_price = candy.price * quantity

		if wallet.balance < total_price:
			raise InsufficientBalanceError()
		
		
			
		new_ticket = Ticket(
			status = "Pending")
		new_ticket.user = user
		db.session.add(new_ticket)

		wallet.balance -= total_price
		candy.stock -= quantity

		new_ledger = Ledger(
			amount = total_price,
			type = "DEBIT",
			reason = f'Bought {quantity} {candy_name}',
			timestamp = datetime.now())
		new_ledger.wallet = user.wallet
		db.session.add(new_ledger)
		new_transaction = UserCandyTransaction(
			quantity = quantity,
			total_price = total_price,
			timestamp = datetime.now())
		new_transaction.user = user
		new_transaction.candy = candy
		db.session.add(new_transaction)
		new_ticket.status = "Completed"
		db.session.commit()
		return jsonify({"msg":"Purchase Successful",
					"Ticket_id":new_ticket.id})

	except Exception:
		db.session.rollback()
		raise
		

@auth_bp.route("/ticket/view/<int:ticket_id>",methods=["GET"])
@jwt_required()
def view_ticket(ticket_id):
	current_user = get_jwt_identity()
	user = User.query.filter_by(username=current_user).first()
	if user:
		ticket = Ticket.query.filter_by(id = ticket_id,
			user_id = user.id).first()
		if ticket:
			return jsonify({"Ticket id": ticket.id,
				"Status":ticket.status})
		else:
			raise TicketNotFoundError()
	return jsonify({"msg":"Invalid credentials"})

@auth_bp.route("/user/ticket",methods=["GET"])
@jwt_required()
def my_tickets():
	current_user = get_jwt_identity()
	user = User.query.filter_by(username=current_user).first()
	if user:
		ticket = Ticket.query.filter_by(user_id=user.id).all()
		if ticket:
			ticket_stack = []
			for tickets in ticket:
				ticket_stack.append({
					"Ticket id": tickets.id,
					"Status": tickets.status
					})
			return jsonify(ticket_stack)
		return jsonify({"msg":"No record"})
	return jsonify({"msg":"Invalid credential"})

@auth_bp.route("/user/transaction_history",methods=["GET"])
@jwt_required()
def transaction_history():
	current_user = get_jwt_identity()
	user = User.query.filter_by(username=current_user).first()
	if user:
		transaction_history = UserCandyTransaction.query.filter_by(user_id=user.id).all()
		if transaction_history:
			transactions = []
			for transaction in transaction_history:
				transactions.append({"Transaction ID": transaction.id,
					"Candy": transaction.candy.candy_name,
					"Quantity": transaction.quantity,
					"Total Price": transaction.total_price,
					"Time": transaction.timestamp})
			return jsonify(transactions)
		return jsonify({"msg":"No record available"})
	return jsonify({"msg":"Invalid credential"})

@auth_bp.route("/user/wallet/balance",methods=["GET"])
@jwt_required()
def wallet_history():
	current_user = get_jwt_identity()
	user = User.query.filter_by(username=current_user).first()
	if user:
		wallet = user.wallet
		ledgers = wallet.ledger
		history = []
		for entries in ledgers:
			history.append({
				"Amount": entries.amount,
				"Type": entries.type,
				"Reason": entries.reason,
				"Time": entries.timestamp
				})
		return jsonify(history)
	return jsonify({"msg":"Invalid credential"})

@auth_bp.get("/test-users")
def test_users():
	page = request.args.get("page", 1, type=int)
	per_page = request.args.get("per_page", 2, type=int)
	offset = (page - 1)*per_page
	users = db.session.scalars(db.select(User).order_by(User.id).offset(offset).limit(per_page)).all()
	return {
	"page": page,
	"per_page": per_page,
	"users": [
	{
	"id": user.id,
	"username": user.username
	}
	for user in users
	]
	}
