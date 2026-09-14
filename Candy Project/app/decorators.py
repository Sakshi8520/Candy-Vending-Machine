from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User 

def admin_required(fn):
	@wraps(fn)
	def wrapper(*args,**kwargs):
		username = get_jwt_identity()
		user = User.query.filter_by(username=username).first()
		if not user:
			return jsonify({
				"error":"User not found"
				}),404
		if not user.is_admin:
			return jsonify({"error":"Admin access required"}),403
		return fn(*args,**kwargs)
	return wrapper