from flask import Blueprint,request,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import (JWTManager,create_access_token,jwt_required,get_jwt_identity)
from app.extensions import db
from app.models import User,Candy,UserCandyTransaction,Ticket,Wallet,Ledger
from app.config import Config
from datetime import datetime,timedelta

auth_bp = Blueprint("auth",__name__)
@auth_bp.route("/test")
def Test_auth():
	return {"message":"this route works!"}

#Sign up
@auth_bp.route("/sign_up",methods=["POST"])
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

	return jsonify({"msg":f'You are registered successfully {new_user.username}, you got a {new_wallet.balance} worth welcome bonus'})

#Log in
@auth_bp.route("/log_in",methods=["POST"])
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
			return jsonify(access_token=access_token)
		return jsonify({"msg":"Wrong username or password"}),401
	return jsonify({"msg":"username doesn't exists,please sign up"})

@auth_bp.route("/me",methods=["GET"])
@jwt_required()
def me():
	current_user = get_jwt_identity()
	return jsonify(logged_in_as = current_user)

@auth_bp.route("/buy_candy",methods=["POST"])
@jwt_required()
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
	candy = Candy.query.filter_by(candy_name=candy_name).first()
	if candy:
		user = User.query.filter_by(username=current_user).first()
		total_price = candy.price * quantity
		if candy.stock >= quantity:
			print(user)
			wallet = Wallet.query.filter_by(user_id=user.id).first()
			print(wallet)
			print(user.wallet)
			print("Balance:",user.wallet.balance)
			print("Price:",candy.price)
			print("Total:",total_price)
			if user.wallet.balance >= total_price:
				new_ticket = Ticket(
					status = "Pending")
				new_ticket.user = user
				db.session.add(new_ticket)
				user.wallet.balance -= total_price
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
			return jsonify({"msg":"Insufficient balance"})
		return jsonify({"msg":"Out of stock"})
	return jsonify({"msg":f'{candy_name} currently unavailable'})

@auth_bp.route("/view_ticket/<int:ticket_id>",methods=["GET"])
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
		return jsonify({"msg":"Ticket not found"}),404
	return jsonify({"msg":"Invalid credentials"})

@auth_bp.route("/my_tickets",methods=["GET"])
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

@auth_bp.route("/transaction_history",methods=["GET"])
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

@auth_bp.route("/wallet_balance",methods=["GET"])
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