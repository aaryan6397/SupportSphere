from app.models.user import User


def test_customer_can_register(client, app):
    response = client.post(
        "/auth/register",
        data={
            "name": "Aryan Kumar",
            "email": "aryan@example.com",
            "password": "Password123",
            "confirm_password": "Password123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Account created successfully" in response.data

    with app.app_context():
        user = User.query.filter_by(
            email="aryan@example.com"
        ).first()

        assert user is not None
        assert user.role == "customer"


def test_customer_can_login(client, app):
    with app.app_context():
        user = User(
            name="Aryan Kumar",
            email="aryan@example.com",
            role="customer"
        )

        user.set_password("Password123")

        from app.extensions import db

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/auth/login",
        data={
            "email": "aryan@example.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Welcome back, Aryan Kumar!" in response.data


def test_registration_rejects_weak_password(client, app):
    response = client.post(
        "/auth/register",
        data={
            "name": "Aryan Kumar",
            "email": "aryan@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"uppercase letter" in response.data

    with app.app_context():
        assert User.query.filter_by(email="aryan@example.com").first() is None


def test_login_is_rate_limited_after_repeated_failures(client, app):
    with app.app_context():
        user = User(name="Aryan", email="aryan@example.com", role="customer")
        user.set_password("Password123")
        from app.extensions import db
        db.session.add(user)
        db.session.commit()

    for _ in range(5):
        client.post("/auth/login", data={"email": "aryan@example.com", "password": "WrongPassword123"})

    response = client.post("/auth/login", data={"email": "aryan@example.com", "password": "Password123"})
    assert response.status_code == 429
    assert b"Too many login attempts" in response.data
