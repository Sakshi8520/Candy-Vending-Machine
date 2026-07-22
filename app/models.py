from app.extensions import db
from datetime import timedelta,datetime
class User(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(50),unique=True)
	password = db.Column(db.String(200))
	is_admin = db.Column(db.Boolean,default=False)
	purchase_history = db.relationship("UserCandyTransaction",back_populates="user")
	wallet = db.relationship("Wallet",back_populates = "user",uselist=False)
	ticket = db.relationship("Ticket",back_populates="user")
class Candy(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	candy_name = db.Column(db.String(100),unique=True)
	price = db.Column(db.Integer)
	stock = db.Column(db.Integer)
	purchases = db.relationship("UserCandyTransaction",back_populates="candy")

class UserCandyTransaction(db.Model):
	id = db.Column(db.Integer,primary_key=True,autoincrement=True)
	user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
	candy_id = db.Column(db.Integer,db.ForeignKey("candy.id"))
	quantity = db.Column(db.Integer,nullable=False)
	total_price = db.Column(db.Integer,nullable=False)
	timestamp = db.Column(db.DateTime)
	user = db.relationship("User",back_populates="purchase_history")
	candy = db.relationship("Candy",back_populates="purchases")
	

class Ticket(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
	status = db.Column(db.String(50),nullable=False)
	transaction_id = db.Column(db.Integer,unique=True)
	user = db.relationship("User",back_populates="ticket")

class Wallet(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
	balance = db.Column(db.Integer)
	ledger = db.relationship("Ledger",back_populates="wallet")
	user = db.relationship("User",back_populates="wallet",uselist=False)

class Ledger(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	amount = db.Column(db.Integer)
	type = db.Column(db.String(100))
	reason = db.Column(db.String(100))
	timestamp = db.Column(db.DateTime)
	wallet_id = db.Column(db.Integer,db.ForeignKey("wallet.id"))
	wallet = db.relationship("Wallet",back_populates="ledger")

