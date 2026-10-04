from flask import render_template
from . import main_bp

@main_bp.route("/")
def home():
	return render_template("index.html")

@main_bp.route("/login")
def login_page():
	return render_template("login.html")