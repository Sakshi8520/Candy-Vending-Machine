from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter 
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity


def user_or_ip():
	try:
		user_id = get_jwt_identity()
		if user_id:
			return f"User: {user_id}"
	except Exception:
		pass 
	return get_remote_address()
limiter = Limiter(
	#identify who's making requests by their IP address but user based finding is superior cause 2 users can share same IP
	key_func=user_or_ip,
	#for now keep rate-limit counters in memory
	storage_uri="memory://",
	#Global limit
	default_limits=["10 per minute"],
	#meta limits
	meta_limits=["2 per hour"])

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()