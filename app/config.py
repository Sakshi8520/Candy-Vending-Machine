from datetime import timedelta
class Config:
	SQLALCHEMY_DATABASE_URI = "sqlite:///candy.db"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	JWT_SECRET_KEY = "candy88"
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
	WELCOME_BONUS = 500
	