from app.auth.routes import generate_reset_token
from app.extensions import db
from app.models.user import User


def test_password_reset_token_is_one_time(client, app):
    with app.app_context():
        user = User(name="Aryan", email="aryan@example.com", role="customer")
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()
        token = generate_reset_token(user)

    response = client.post(
        f"/auth/reset-password/{token}",
        data={"password": "NewPassword123", "confirm_password": "NewPassword123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Password updated" in response.data

    with app.app_context():
        user = User.query.filter_by(email="aryan@example.com").first()
        assert user.check_password("NewPassword123")

    reused = client.get(f"/auth/reset-password/{token}", follow_redirects=True)
    assert b"invalid or has expired" in reused.data
