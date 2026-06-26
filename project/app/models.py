from app.extensions import db
from datetime import datetime,timedelta
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(200))
    created_at = db.Column(db.DateTime)