import pytest
from app import create_app 
from werkzeug.security import generate_password_hash 
from app.models import User, Wallet, Candy, Ticket, Ledger, UserCandyTransaction
from app import db 


@pytest.fixture
def app():  
	app = create_app()
	return app 

@pytest.fixture
def client(app):  
	return app.test_client()

@pytest.fixture 
def test_user(app): 
	with app.app_context():
		user = User(
			username = "pytest_user",
			password = generate_password_hash("testpassword"),
			is_admin = False)
		wallet = Wallet(
			balance = 500,
			user = user)
		db.session.add(user)
		db.session.add(wallet)
		db.session.commit()

		yield user

		db.session.delete(wallet)
		db.session.delete(user)
		db.session.commit()

@pytest.fixture
def test_candy(app):
	with app.app_context():
		candy = Candy(
			candy_name = "pytest_candy",
			stock = 10,
			price = 20)
		db.session.add(candy)
		db.session.commit()

		yield candy 

		db.session.delete(candy)
		db.session.commit()


def test_app_exists(app): 
	assert app is not None 


def test_login_endpoint_exists(app): 
	print(app.url_map)


def test_login(client,test_user):
	response = client.post("/auth/users/log_in", json = {
		"username": "pytest_user",
		"password": "testpassword"
		})
	print(response.status_code)
	print(response.get_json())
	assert response.status_code == 200

def test_purchase(client, test_user, test_candy):
	response = client.post("/auth/users/log_in", json = {
		"username": "pytest_user",
		"password": "testpassword"
		})
	csrf_token = client.get_cookie("csrf_access_token").value
	print(response.status_code)
	print(response.headers)
	print(client.get_cookie("access_token_cookie"))
	assert response.status_code == 200

	response = client.post("/auth/candy/purchase", json = {
		"candy_name" : "pytest_candy",
		"quantity" : 1
		},
		headers = {
		"X-CSRF-TOKEN": csrf_token
		})
	print(response.status_code)
	print(response.get_json())

	assert response.status_code == 200

	with client.application.app_context():
		assert test_user.wallet.balance == 480
		assert test_candy.stock == 9
	with client.application.app_context():
		UserCandyTransaction.query.delete()
		Ticket.query.delete()
		Ledger.query.delete()
		db.session.commit()

def test_candy_not_found_error(client, test_candy, test_user):
	response = client.post("/auth/users/log_in", json = {
		"username": "pytest_user",
		"password": "testpassword"
		})
	csrf_token = client.get_cookie("csrf_access_token").value
	print(response.status_code)
	print(response.headers)
	print(client.get_cookie("access_token_cookie"))
	assert response.status_code == 200

	before_balance = test_user.wallet.balance
	print(before_balance)
	before_stock = test_candy.stock
	response = client.post("/auth/candy/purchase", json ={
		"candy_name": "fake_candy",
		"quantity": 1
		}, headers = {
	    "X-CSRF-TOKEN": csrf_token
		})
	after_balance = test_user.wallet.balance
	after_stock = test_candy.stock
	assert response.status_code == 404
	assert response.get_json() == {"error": "Candy Not Found"}
	assert before_balance == after_balance
	assert before_stock == after_stock

def test_out_of_stock_error(client, test_user, test_candy):
	response = client.post("/auth/users/log_in", json = {
		"username": "pytest_user",
		"password": "testpassword"
		})
	csrf_token = client.get_cookie("csrf_access_token").value
	assert response.status_code == 200

	before_balance = test_user.wallet.balance
	before_stock = test_candy.stock
	response = client.post("/auth/candy/purchase", json = {
		"candy_name": "pytest_candy",
		"quantity": 11
		}, headers = {
		"X-CSRF-TOKEN": csrf_token})
	after_stock = test_candy.stock
	after_balance = test_user.wallet.balance
	ledger = Ledger.query.filter_by(wallet_id=test_user.wallet.id).first()
	ticket = Ticket.query.filter_by(user_id=test_user.id).first()

	assert response.status_code == 409
	assert response.get_json() == {"error": "Out Of Stock"}
	assert before_balance == after_balance
	assert before_stock == after_stock
	assert ledger is None 
	assert ticket is None 


def test_insuffiecient_balance_error(client,test_user,test_candy):
	response = client.post("/auth/users/log_in", json = {
		"username": "pytest_user",
		"password": "testpassword"
		})
	csrf_token = client.get_cookie("csrf_access_token").value
	assert response.status_code == 200

	wallet = Wallet.query.filter_by(user_id=test_user.id).first()
	wallet.balance = 100
	db.session.commit()
	before_balance = wallet.balance
	before_stock = test_candy.stock

	response = client.post("/auth/candy/purchase", json = {
		"candy_name": "pytest_candy",
		"quantity": 6
		}, headers = {
		"X-CSRF-TOKEN": csrf_token})
	after_stock = test_candy.stock
	after_balance = test_user.wallet.balance

	assert response.status_code == 409
	assert response.get_json() == {"error":"Insufficient Balance"}
	assert before_balance == after_balance
	assert before_stock == after_stock
	assert Ledger.query.filter_by(wallet_id=test_user.wallet.id).first() is None
	assert Ticket.query.filter_by(user_id=test_user.id).first() is None

def test_invalid_quantity(client,test_user,test_candy):
	response = client.post("/auth/users/log_in", json = {
		"username": "pytest_user",
		"password": "testpassword"
		})
	csrf_token = client.get_cookie("csrf_access_token").value
	assert response.status_code == 200
	before_balance = test_user.wallet.balance
	before_stock = test_candy.stock

	response = client.post("/auth/candy/purchase", json = {
		"candy_name": "pytest_candy",
		"quantity": "xyz"
		}, headers = {
		"X-CSRF-TOKEN": csrf_token})
	after_stock = test_candy.stock
	after_balance = test_user.wallet.balance
	assert response.status_code == 400
	assert response.get_json() == {"msg": "Invalid quantity"}
	assert before_balance == after_balance
	assert before_stock == after_stock
	assert Ledger.query.filter_by(wallet_id=test_user.wallet.id).first() is None
	assert Ticket.query.filter_by(user_id=test_user.id).first() is None

def test_zero_quantity(client,test_user,test_candy):
	response = client.post("/auth/users/log_in", json = {
		"username": "pytest_user",
		"password": "testpassword"
		})
	csrf_token = client.get_cookie("csrf_access_token").value
	assert response.status_code == 200
	before_balance = test_user.wallet.balance
	before_stock = test_candy.stock

	response = client.post("/auth/candy/purchase", json = {
		"candy_name": "pytest_candy",
		"quantity": 0
		}, headers = {
		"X-CSRF-TOKEN": csrf_token})
	after_stock = test_candy.stock
	after_balance = test_user.wallet.balance
	assert response.status_code == 400
	assert response.get_json() == {"msg": "quantity must be greater than 0"}
	assert before_balance == after_balance
	assert before_stock == after_stock
	assert Ledger.query.filter_by(wallet_id=test_user.wallet.id).first() is None
	assert Ticket.query.filter_by(user_id=test_user.id).first() is None

def test_successful_purchase(client,test_user,test_candy):
	response = client.post("/auth/users/log_in", json = {
		"username": "pytest_user",
		"password": "testpassword"
		})
	csrf_token = client.get_cookie("csrf_access_token").value
	assert response.status_code == 200


	response = client.post("/auth/candy/purchase", json = {
		"candy_name": "pytest_candy",
		"quantity": 1
		}, headers = {
		"X-CSRF-TOKEN": csrf_token})


	assert response.status_code == 200
	with client.application.app_context():
		assert test_user.wallet.balance == 480
		assert test_candy.stock == 9
		ledger = Ledger.query.filter_by(wallet_id=test_user.wallet.id).first()
		ticket = Ticket.query.filter_by(user_id=test_user.id).first() 
		transaction = UserCandyTransaction.query.filter_by(user_id=test_user.id).first()
		assert ledger.amount == 20
		assert ledger.type == "DEBIT"
		assert ledger.reason == f"Bought {transaction.quantity} {test_candy.candy_name}"
		assert transaction.quantity == 1
		assert transaction.total_price == 20
		assert ticket.user_id == test_user.id 
		assert ticket.status == "Completed"
		assert ticket.transaction_id == transaction.id

def test_ticket_not_found_error(client,test_user,test_candy):
	response = client.post("/auth/users/log_in", json = {
		"username": "pytest_user",
		"password": "testpassword"
		})
	csrf_token = client.get_cookie("csrf_access_token").value
	assert response.status_code == 200

	response = client.get("/auth/ticket/view/999999",headers = {
		"X-CSRF-TOKEN": csrf_token})

	assert response.status_code == 404
	assert response.get_json() == {"error": "Ticket Not Found"}
	

