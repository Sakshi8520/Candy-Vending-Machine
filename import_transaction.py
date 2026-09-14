import sqlite3
from app import create_app
from app.extensions import db
from app.models import User, UserCandyTransaction, Candy
from sqlalchemy import func

app = create_app()
sqlite_conn = sqlite3.connect("instance/candy.db")
sqlite_cur = sqlite_conn.cursor()

with app.app_context():

	
	sqlite_cur.execute("SELECT id, user_id, candy_id, quantity, total_price, timestamp  FROM user_candy_transaction")
	transactions = sqlite_cur.fetchall()
	
	for row in transactions:

		
		new_user_id = row[1]+1

		transaction = UserCandyTransaction(
			id=row[0],
			user_id=new_user_id,
			candy_id=row[2],
			quantity=row[3],
			total_price=row[4],
			timestamp=row[5])
		db.session.add(transaction)
	db.session.commit()
	print("Transactions imported")
	
sqlite_conn.close()