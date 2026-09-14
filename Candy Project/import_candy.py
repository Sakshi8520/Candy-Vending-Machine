import sqlite3
 
from app import create_app
from app.extensions import db 
from app.models import Candy 

app = create_app()

sqlite_conn = sqlite3.connect("instance/candy.db")
sqlite_cur = sqlite_conn.cursor()

with app.app_context():
	sqlite_cur.execute("SELECT id,candy_name,price,stock FROM candy")
	rows = sqlite_cur.fetchall()

	for row in rows:
		candy = Candy(
			id=row[0],
			candy_name=row[1],
			price=row[2],
			stock=row[3])
		db.session.add(candy)
	db.session.commit()
print("Candies imported!")

