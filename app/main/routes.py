from flask import render_template
from . import main_bp

@main_bp.route("/")
def home():
	return render_template("index.html")

@main_bp.route("/login")
def login_page():
	return render_template("login.html")

@main_bp.route("/signup")
def signup_page():
	return render_template("signup.html")

@main_bp.route("/buy_candy")
def candies_page():
	return render_template("candies.html")

#Liveness check
@main_bp.route("/health")
def health():
	return {"status":"ok"}, 200