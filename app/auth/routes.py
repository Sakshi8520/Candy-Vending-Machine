from flask import Blueprint,request,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import (JWTManager,create_access_token,create_refresh_token,jwt_required,get_jwt_identity)
from flask_jwt_extended import set_access_cookies
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
from flask import make_response


auth_bp = Blueprint("auth",__name__)

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


#Database Transactions
@auth_bp.post("/test_transaction/<int:wallet_id>/<int:candy_id>")
def test_transaction(wallet_id,candy_id):
	wallet = Wallet.query.get(wallet_id)
	candy = Candy.query.get(candy_id)
	print("BEFORE:",wallet.balance,candy.stock)
	try:
		wallet.balance -= 100
		candy.stock -= 1
		print("AFTER CHANGES:", wallet.balance,candy.stock)
		#raise Exception("Intentional transaction failure")
		db.session.commit()
	except Exception:
		db.session.rollback()
		raise 
	return {"message":"Transaction Successful"}

@auth_bp.route("/test_cookie")
def test_cookie():
	response = make_response({"msg":"cookie set"})
	response.set_cookie("candy_test","Kitkat",httponly=True,secure=False,samesite="None")
	return response

	
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
		print("Stored:", user.password)
		print("Entered:", password)
		print("Match:", check_password_hash(user.password, password))
		if check_password_hash(user.password,password):
			access_token = create_access_token(identity=username)
			refresh_token = create_refresh_token(identity=username)
			response = jsonify({
				"access_token": access_token,
				"refresh_token": refresh_token
				})
			set_access_cookies(response, access_token)
			return response
			#return jsonify({"access_token":access_token,
				 #"refresh_token":refresh_token})
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
#@jwt_required(refresh=True) means only refresh token is allowed
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
		user = User.query.filter_by(username=current_user).first()

		if not user:
			return jsonify({"msg":"User not found"}),404

		#Locking candy first
		candy = (Candy.query.filter_by(candy_name=candy_name).with_for_update().first())
		if not candy:
			raise CandyNotFoundError()
			current_app.logger.warning(f"Candy not found: candy_id={candy_id}")
		#Refresh wallet with a lock (lock candy first then candy and not change this sequence to avoid deadlock)

		wallet = (Wallet.query.filter_by(user_id=user.id).with_for_update().first())
		print("PURCHASE WALLET BALANCE:", wallet.balance)
		if not wallet:
			return jsonify({"msg":"Wallet not found"}),404

		
		
		#Check locked values
		if candy.stock < quantity:
			raise OutofStockError()

		total_price = candy.price * quantity

		if wallet.balance < total_price:
			current_app.logger.warning("Purchase attempted with insufficient balance: user_id=%s candy_id=%s", user.id, candy.id)
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
		current_app.logger.info("Candy purchased successfully: user_id=%s candy_id=%s quantity=%s",user.id,candy.id,quantity)
		return jsonify({"msg":"Purchase Successful",
					"Ticket_id":new_ticket.id})

	except Exception:
		db.session.rollback()
		current_app.logger.exception("Purchase failed")
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

