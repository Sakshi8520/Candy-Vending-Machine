import sqlite3

from app import create_app
from app.extensions import db
from app.models import User
from sqlalchemy import func

app = create_app()
#Connect to old sqlite database
sqlite_conn  = sqlite3.connect("instance/candy.db")
sqlite_cur = sqlite_conn.cursor()

with app.app_context():
	#Find the highest user ID already in postgresql(It shows 1 from MAX() query)
	highest_id = db.session.query(func.max(User.id)).scalar()

	if highest_id is None:
		highest_id=0

	offset = highest_id
	print(f"Offset = {offset}")

	#Read users from sqlite
	sqlite_cur.execute("SELECT id, username, password, is_admin FROM user")
	users = sqlite_cur.fetchall()

	id_map = {}
	for row in users:
		old_id = row[0]
		new_id = old_id + offset

		id_map[old_id] = new_id

		user = User(
			id=new_id,
			username=row[1],
			password=row[2],
			is_admin=row[3])
		db.session.add(user)
	db.session.commit()
	print("Users imported!")
	print("ID Map:", id_map)
sqlite_conn.close()