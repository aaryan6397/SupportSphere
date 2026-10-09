from getpass import getpass

from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    email = input("Admin email: ").strip().lower()
    name = input("Admin name: ").strip()
    password = getpass("Admin password: ")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        print("An account already exists with this email.")

    elif not name or not password:
        print("Name and password are required.")

    elif len(password) < 6:
        print("Password must have at least 6 characters.")

    else:
        admin = User(
            name=name,
            email=email,
            role="admin"
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully.")