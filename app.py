from flask import Flask
from flask import request
from flask import jsonify
#STORAGE
users = []
app = Flask(__name__)
@app.route("/")
def home():
    return '''
        <form method="POST" action="/submit">
        <input type="text" name="name">
        <input type="submit">
        </form>
    '''
    #return "Backend Era"
@app.route("/about")
def about():
    return "I am learning backend"

#GET requests
@app.route("/user")
def user():
    name = request.args.get("name")
    id = request.args.get("id")
    return f"Hello {name}, your id is {id}"
    
@app.route("/submit",methods=["POST"])
def submit():
    name = request.form.get("name")
    return f"Welcome {name}"

#JSON response
@app.route("/api")
def api():
    return jsonify({
        "name":"Sakshi",
        "status":"Learning Backend"
    })

#JSON POST endpoint
#CRUD operations
#CREATE
@app.route("/api/user", methods=["POST"])
def create_user():
    
    data = request.get_json()
    #name = data.get("name")
    #user_id = data.get("id")
    #user = {
        #"name": name,
        #"id": user_id
    #}
    if isinstance(data, list):
        for user in data:
            users.append(user)
    else:
        users.append(user)
    return jsonify({
        "message":f"Users added",
        "users": users
    })
#retrive users
#READ
@app.route("/api/users",methods=["GET"])
def get_users():
    return jsonify(users)

#retrieve specific user
#SEARCH 
@app.route("/api/user/<int:user_id>",methods=["GET"])
def get_user(user_id):
    for user in users:
        if user["id"] == user_id:
            return jsonify(user)
    return jsonify({"message":"User not found"}), 404

#DELETE users
@app.route("/api/user/<int:user_id>",methods=["DELETE"])
def delete_user(user_id):
    for user in users:
        if user["id"] == user_id:
            users.remove(user)
            return jsonify({"message":"User deleted"})
    return jsonify({"mesaage":"User not found"}),404
if __name__ == "__main__":
    app.run(debug=True)
