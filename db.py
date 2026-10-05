from werkzeug.security import generate_password_hash
from app import app, db, User  # Import app alongside db and User

with app.app_context():
    # 1. Verify DB URL being targeted
    print("--> Target Database URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    # 2. Query user
    user = User.query.filter_by(username='student1').first()

    if user:
        # Update password hash for student1
        user.password_hash = generate_password_hash('student1')
        db.session.commit()
        print(f"Successfully updated password hash for user: {user.username} ({user.email})")
    else:
        print("User 'student1' not found in the target database.")