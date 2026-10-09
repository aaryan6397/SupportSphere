from app import create_app
from app.extensions import db


def test_csrf_rejects_post_without_token():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "csrf-test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "CSRF_PROTECTION_ENABLED": True,
    })

    with app.app_context():
        db.create_all()
        client = app.test_client()
        response = client.post(
            "/auth/register",
            data={
                "name": "Aryan Kumar",
                "email": "aryan@example.com",
                "password": "Password123",
                "confirm_password": "Password123",
            },
        )

        assert response.status_code == 400

        db.session.remove()
        db.drop_all()
