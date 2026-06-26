from flask import Flask,request,jsonify
from app.extensions import db, migrate
from app.auth.routes import auth_bp
from app.chat.routes import chat_bp
from app.extensions import jwt
from datetime import timedelta
from app import models

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "secret-key"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=20)

    db.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)
    app.register_blueprint(auth_bp,url_prefix="/auth")
    app.register_blueprint(chat_bp,url_prefix="/chat")
    return app
