from datetime import timedelta
import os 
from dotenv import load_dotenv
load_dotenv()

class Config:
	SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
	WELCOME_BONUS = 500
	MAX_CONTENT_LENGTH = 5*1024*1024

class DevelopmentConfig(Config):
	DEBUG = True
	#SQLALCHEMY_DATABASE_URI = "postgresql://localhost/candy_dev"

class ProductionConfig(Config):
	DEBUG = False
	#SQLALCHEMY_DATABASE_URI = "postgresql://localhost/candy"
	