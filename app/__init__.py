from flask import Flask,request,jsonify,current_app
from app.extensions import db,jwt,migrate
from app.config import Config
from datetime import timedelta
from app.auth.routes import auth_bp
from app.admin.routes import admin_bp
from app import models
from app.exceptions import UserNotFoundError
from app.exceptions import InsufficientBalanceError
from app.exceptions import CandyNotFoundError
from app.exceptions import TicketNotFoundError
from app.exceptions import OutofStockError
import os 
from app.config import DevelopmentConfig,ProductionConfig
from marshmallow.exceptions import ValidationError
import logging
from logging.handlers import RotatingFileHandler
from app.extensions import limiter
from app.token_blocklist import revoked_tokens
from app.middleware import SimpleMiddleware
from app.middleware import SecondMiddleware
from flask_cors import CORS 



def create_app():
	app = Flask(__name__)
	#Middleware/request-response lifecyle

	@app.before_request
	def log_request():
		current_app.logger.info(f"REQUEST:{request.method} {request.path}")
	@app.after_request
	def log_response(response):
		current_app.logger.info(f"RESPONSE: {response.status_code}")
		return response
	#Global error handler- doesn't exist error
	@app.errorhandler(404)
	def not_found(error):
		return jsonify({
			"error": "Resource not found"
			}),404
	#Global error handler-internal server error
	@app.errorhandler(500)
	def internal_server_error(error):
		return jsonify({
			"error":"Internal Server error"
		}),500	
	#Custom Errors
	@app.errorhandler(UserNotFoundError)
	def handle_user_not_found_error(error):
		return jsonify({
			"error":"User not found"
			}),404
	@app.errorhandler(InsufficientBalanceError)
	def handle_insufficient_balance_error(error):
		return jsonify({
			"error":"Insufficient Balance"
			}),409
	@app.errorhandler(CandyNotFoundError)
	def handle_candy_not_found_error(error):
		return jsonify({
			"error":"Candy Not Found"
			}),404	
	@app.errorhandler(TicketNotFoundError)
	def handle_ticket_not_found_error(error):
		return jsonify({
			"error":"Ticket Not Found"
			}),404
	@app.errorhandler(OutofStockError)
	def handle_out_of_stock_error(error):
		return jsonify({
			"error":"Out Of Stock"
			}),409
	@app.errorhandler(ValidationError)
	def handle_validation_error(error):
		return jsonify({
			"error":"Validation failed",
			"messages":error.messages
			}),400
	#429 error handler
	@app.errorhandler(429)
	def handle_rate_limit(e):
		return jsonify({
			"error":"rate_limit_exceeded",
			"message":"Too many requests. Please try again later"
			}),429

	#Invalid/expired/revoked token callback
	#1.Expired
	@jwt.expired_token_loader
	def expired_token_callback(jwt_header,jwt_payload):
		return jsonify({
			"error":"token_expired",
			"message":"Your access token has expired."
			}),401
	#2.Invalid
	@jwt.invalid_token_loader
	def invalid_token_callback(error):
		return jsonify({
			"error":"invalid_token",
			"message":"The access token is invalid"
			}),401
	#3.Missing token
	@jwt.unauthorized_loader
	def unauthorized_token_callback(error):
		return jsonify({
			"error":"invalid_token",
			"message":"Authentication token is required"
			}),401

	
	#token blocklisting
	@jwt.token_in_blocklist_loader
	def check_if_token_revoked(jwt_header,jwt_payload):
		jti = jwt_payload["jti"]
		return jti in revoked_tokens

	#Handle revoked tokens-
	@jwt.revoked_token_loader
	def revoked_token_callback(jwt_header,jwt_payload):
		return jsonify({
			"error":"token_revoked",
			"message":"This token has been revoked"
			}),401
	#Environment-
	environment = os.getenv("FLASK_ENV","development")
	if environment == "production":
		app.config.from_object(ProductionConfig)
	else:
		app.config.from_object(DevelopmentConfig)

	CORS(app,origins=app.config["FRONTEND_ORIGIN"],supports_credentials=True)

	#logging-
	log_folder = os.path.join(app.root_path,"logs")
	os.makedirs(log_folder,exist_ok=True)
	log_file = os.path.join(log_folder,"app.log")
	#file_handler = logging.FileHandler(log_file)
	#Log rotates-
	file_handler = RotatingFileHandler(log_file,maxBytes=1024,backupCount=3)
	file_handler.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)s %(levelname)s in %(module)s: %(message)s")
	file_handler.setFormatter(formatter)
	app.logger.addHandler(file_handler)

	
	app.config["RATELIMIT_HEADERS_ENABLED"] = True
	db.init_app(app)
	with app.app_context():
		db.create_all()
	migrate.init_app(app,db)
	jwt.init_app(app)
	limiter.init_app(app)
	app.register_blueprint(auth_bp,url_prefix="/auth")
	app.register_blueprint(admin_bp,url_prefix="/admin")
	app.wsgi_app = SimpleMiddleware(app.wsgi_app)
	app.wsgi_app = SecondMiddleware(app.wsgi_app)
	return app

