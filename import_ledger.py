import sqlite3
from app import create_app
from app.extensions import db
from app.models import Wallet, Ledger
from sqlalchemy import func

app = create_app()
sqlite_conn = sqlite3.connect("instance/candy.db")
sqlite_cur = sqlite_conn.cursor()

with app.app_context():
	highest_wallet_id = db.session.query(func.max(Wallet.id)).scalar()
	if highest_wallet_id is None:
		highest_wallet_id=0
	wallet_offset = highest_wallet_id
	
	print(f"wallet offset = {wallet_offset}")

	sqlite_cur.execute("SELECT id, amount, type, reason, timestamp, wallet_id  FROM ledger")
	ledgers = sqlite_cur.fetchall()
	id_map = {}
	for row in ledgers:

		
		new_wallet_id = row[5]+1

		ledger = Ledger(
			id=row[0],
			amount=row[1],
			type=row[2],
			reason=row[3],
			timestamp=row[4],
			wallet_id=new_wallet_id)
		db.session.add(ledger)
	db.session.commit()
	print("Ledgers imported")
	print("ID Map:", id_map)
sqlite_conn.close()