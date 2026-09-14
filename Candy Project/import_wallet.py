import sqlite3
from app import create_app
from app.extensions import db
from app.models import Wallet, User
from sqlalchemy import func


app = create_app()
sqlite_conn = sqlite3.connect("instance/candy.db")
sqlite_cur = sqlite_conn.cursor()

with app.app_context():
	highest_id = db.session.query(func.max(User.id)).scalar()
	if highest_id is None:
		highest_id=0

	offset = highest_id
	highest_wallet_id = db.session.query(func.max(Wallet.id)).scalar()
	if highest_wallet_id is None:
		highest_wallet_id=0
	wallet_offset = highest_wallet_id
	print(f"Offset = {offset}")
	print(f"wallet offset = {wallet_offset}")

	sqlite_cur.execute("SELECT id, user_id, balance FROM wallet")
	wallets = sqlite_cur.fetchall()
	id_map = {}
	for row in wallets:

		old_user_id = row[1]
		new_user_id = old_user_id + 1
		id_map[old_user_id] = new_user_id
		new_wallet_id = row[0]+wallet_offset

		wallet = Wallet(
			id=new_wallet_id,
			user_id = new_user_id,
			balance=row[2])
		db.session.add(wallet)
	db.session.commit()
	print("Wallets imported")
	print("ID Map:", id_map)
sqlite_conn.close()