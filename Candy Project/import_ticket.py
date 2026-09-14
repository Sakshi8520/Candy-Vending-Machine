import sqlite3
from app import create_app
from app.extensions import db
from app.models import User, Ticket
from sqlalchemy import func

app = create_app()
sqlite_conn = sqlite3.connect("instance/candy.db")
sqlite_cur = sqlite_conn.cursor()

with app.app_context():


	sqlite_cur.execute("SELECT id, user_id, status, transaction_id  FROM ticket")
	tickets = sqlite_cur.fetchall()
	
	for row in tickets:

		
		new_user_id = row[1]+1

		ticket = Ticket(
			id=row[0],
			user_id=new_user_id,
			status=row[2],
			transaction_id=row[3])
		db.session.add(ticket)
	db.session.commit()
	print("Tickets imported")
	
sqlite_conn.close()