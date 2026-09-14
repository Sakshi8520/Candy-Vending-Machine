from app import create_app
from app.extensions import db 
from app.models import User 
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload

app = create_app()
with app.app_context():
	#Show sqlalchemy queries in termina;
	db.engine.echo = True

	#print("\n--- STEP !: Get one user ---")
	#user = db.session.get(User,3)
	#print("\nUser:",user.username)
	#print("\n--- STEP 2: Access the user's purchases ---")
	#print(user.purchase_history)

	#Lazy Loading- users = db.session.scalars(db.select(User)).all()
	#for user in users:
		#print(user.purchase_history)

	#selectinload
	#users = db.session.scalars(db.select(User).options(selectinload(User.purchase_history))).all()
	#for user in users:
		#print(user.username)
		#for purchase in user.purchase_history:
			#print(purchase)

	#Joinedload
	#users = db.session.scalars(db.select(User).options(joinedload(User.purchase_history))).unique().all()
	#for user in users:
		#print(user.username)
		#for purchase in user.purchase_history:
			#print(purchase)
	
	#Pagination
	#per_page = 2
	#offset = (page - 1)*per_page
	#users = db.session.scalars(db.select(User).order_by(User.id).offset(offset).limit(per_page)).all()
	#print(f"\nPage: {page}")
	#print(f"Users per page: {per_page}")

	#for user in users:
		#print(user.id,user.username)

	#Pagination + selectinload
	#page = 2
	#per_page = 2
	#offset = (page - 1) * per_page
	#users = db.session.scalars(db.select(User).options(selectinload(User.purchase_history)).order_by(User.id).offset(offset).limit(per_page)).all()
	#print("\n--- RESULTS ---")
	#for user in users:
		#print(user.username)
		#for transcation in user.purchase_history:
			#print(transcation)

	#Pagination + joinedload
	#page = 2
	#per_page  = 2
	#offset  = (page - 1)*per_page
	#users = db.session.scalars(db.select(User).options(joinedload(User.purchase_history)).order_by(User.id).offset(offset).limit(per_page)).unique().all()
	#print("\n--- RESULTS ---")
	#for user in users:
		#print(user.username)
		#for transcation in user.purchase_history:
			#print(transcation)


	#N + 1 demonstration
	users = db.session.scalars(db.select(User).order_by(User.id).limit(4)).all()
	print("\n--- N+1 RESULTS ---")
	for user in users:
		print(user.username)
		for transaction in user.purchase_history:
			print(transaction)

	#Query Optimization
	print("/n--- ONLY NEEDED COLUMNS ---")
	users = db.session.execute(db.select(User.id,User.username).order_by(User.id)).all()
	for user in users:
		print(user.id,user.username)