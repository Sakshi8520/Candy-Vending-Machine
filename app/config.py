from datetime import timedelta
import os 
from dotenv import load_dotenv
import logging
load_dotenv()

class Config:
	SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
	SECRET_KEY = os.getenv("SECRET_KEY")
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
	WELCOME_BONUS = 500
	MAX_CONTENT_LENGTH = 5*1024*1024
	JWT_TOKEN_LOCATION = ["headers","cookies"]
	JWT_COOKIE_SECURE = False
	JWT_COOKIE_SAMESITE = "Lax"
	JWT_COOKIE_HTTPONLY = True
	FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")
	UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
	LOG_LEVEL = logging.INFO

class DevelopmentConfig(Config):
	DEBUG = True
	TESTING = False
	LOG_LEVEL = logging.DEBUG
	#SQLALCHEMY_DATABASE_URI = "postgresql://localhost/candy_dev"

class ProductionConfig(Config):
	DEBUG = False
	TESTING = False
	JWT_COOKIE_SECURE = True
	#SQLALCHEMY_DATABASE_URI = "postgresql://localhost/candy"
	
class TestingConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL")
	DEBUG = False
	TESTING = True
	LOG_LEVEL = logging.DEBUG
	PROPAGATE_EXCEPTIONS = True