from flask import Flask,request,jsonify,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (jwt_manager, jwt_required,get_jwt_identity,create_access_token)
from datetime import datetime, timedelta
app = Flask(__name__)
app.secret_key = "rpg.9201"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Players.db"
db = SQLAlchemy(app)
class Players(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100),nullable=False,unique=True)
    password = db.Column(db.String(200))
    level = db.Column(db.Integer,default=1)
    gold = db.Column(db.Integer,default=150)
    xp = db.Column(db.Integer,default=100)
    streak = db.Column(db.Integer,default=0)
    quest = db.relationship("Quest",backref="player")

class Quest(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    difficulty = db.Column(db.String(100),default="easy")
    xp_reward = db.Column(db.Integer,default=10)
    status = db.Column(db.String(100),default="Not started")
    player_id = db.Column(db.Integer,db.ForeignKey("players.id"))
    completed_at = db.Column(db.DateTime)

with app.app_context():
    db.create_all()

#Signup
@app.route("/signup",methods=["POST"])
def signup():
    data = request.get_json()
    created_users = []
    for player in data:
        username = player.get("username")
        password = player.get("password")
        level = player.get("level")
        hashed_password = generate_password_hash(password)
        new_player = Players(
        username = username,
        password = hashed_password,
        level = level
    )
        db.session.add(new_player)
        created_users.append(new_player)
    db.session.commit()
    print(created_users)
    
    return jsonify({"msg":"User Created",
                    "users" : [
                        {"id": p.id,
                "username": p.username,
                "level": p.level}
                for p in created_users
                    ]
                        })


#Login
@app.route("/login",methods=["POST"])
def login():
    data = request.get_json()
    id = data.get("id")
    username = data.get("username")
    password = data.get("password")
    player = Players.query.filter_by(username=username).first()
    if player and check_password_hash(player.password,password):
        session["user_id"] = player.id

        return jsonify({"msg":"Login successful"
                        })
    return jsonify({"msg":"Invalid credentials"})

#Protected routes
#Profile
@app.route("/profile",methods=["GET"])
def profile():
    if session.get("User_id"):
        return jsonify({"msg":"Logged in"})
    return jsonify({"msg":"Unauthorized access"}),401
#Logout
@app.route("/logout",methods=["GET"])
def logout():
    if session.get("user_id"):
        session.clear()
        return jsonify({"msg":"You've been logged out"})
    return jsonify({"msg":"Something went wrong"})

#add quest
@app.route("/quest",methods=["POST"])
def add_quest():
    data = request.get_json()
    for quest in data:
        title = quest.get("title")
        player_id = quest.get("player_id")
        difficulty = quest.get("difficulty")
        xp_reward = quest.get("xp_reward")
        status = quest.get("status")
        quest = Quest(
            title = title,
            player_id = player_id,
            difficulty = difficulty,
            xp_reward = xp_reward,
            status = status
        )
        db.session.add(quest)
    db.session.commit()
    return jsonify({"msg":"Quest added succesfully"})
#relationship
with app.app_context():
    player = Players.query.get(2)
    #quests = Quest.query.all()
    print(f"level = {player.level}")
    print(f"username = {player.username}")
    for p in player.quest:
        print(f"title = {p.title}")
        print(f"difficulty = {p.difficulty}")
        print(f"xp = {p.xp_reward}")


#Game logic-when quest event happens
base_xp = p.xp_reward

#Difficulty multiplier-

if p.difficulty == "easy":
    difficulty_multiplier = 1.0
if p.difficulty == "medium":
    difficulty_multiplier = 2.0
if p.difficulty == "hard":
    difficulty_multiplier = 2.5
if p.difficulty == "extreme":
    difficulty_multiplier = 3.0
#level bonus-
level_bonus = 0
if player.level >= 5:
    level_bonus = 0.25
if player.level >=10:
    level_bonus = 0.25
#XP formula-
final_xp = base_xp * difficulty_multiplier + level_bonus
print(f"final xp = {final_xp}")
#Quest completed
with app.app_context():
    p.status = "completed"
    print(f"Status={p.status}")
    #level up
    player.level += 1
    print(f"level = {player.level}")
    p.completed_at = datetime.utcnow()
    print(p.completed_at)
    db.session.commit()

#refresh quest
with app.app_context():
    print(p.completed_at)
    if datetime.utcnow() - p.completed_at >= timedelta(hours=24):
            p.status = "not completed"
            print(f"status = {p.status}")
            db.session.commit()
        
if __name__ == "__main__":
    app.run(debug=True)

