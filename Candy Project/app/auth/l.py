from app import create_app
from app.models import User
app = create_app()

with app.app_context():
	print(User.query.all())