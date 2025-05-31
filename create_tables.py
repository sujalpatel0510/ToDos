from app import app, db  # Import your Flask app and db object

with app.app_context():
    db.create_all()
    print("Database tables created!")
