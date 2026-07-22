from flask import Flask,request,jsonify
from app.extensions import db,jwt,migrate
from app.config import Config
from datetime import timedelta
from app.auth.routes import auth_bp
from app.admin.routes import admin_bp
from app import models

def create_app():
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	with app.app_context():
		db.create_all()
	migrate.init_app(app,db)
	jwt.init_app(app)
	app.register_blueprint(auth_bp,url_prefix="/auth")
	app.register_blueprint(admin_bp,url_prefix="/admin")
	return app

