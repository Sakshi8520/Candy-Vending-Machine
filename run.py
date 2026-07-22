print("hello")
from app import create_app
print("Before ca")
app = create_app()
print(__name__)
print("AFter ca")

if __name__ == "__main__":
    from app.extensions import db
    from sqlalchemy import text

    with app.app_context():
        result = db.session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table';")
        )
        print(result.fetchall())
        print("Inside if")

    app.run(debug=True)

