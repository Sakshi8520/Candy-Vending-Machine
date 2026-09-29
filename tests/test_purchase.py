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