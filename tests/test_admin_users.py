from app.extensions import db
from app.models.user import User


def test_admin_can_deactivate_customer_account(client, app):
    with app.app_context():
        admin = User(name="Admin", email="admin@example.com", role="admin")
        admin.set_password("Password123")
        customer = User(name="Customer", email="customer@example.com", role="customer")
        customer.set_password("Password123")
        db.session.add_all([admin, customer])
        db.session.commit()
        customer_id = customer.id

    client.post("/auth/login", data={"email": "admin@example.com", "password": "Password123"})
    response = client.post(f"/admin/users/{customer_id}/active", follow_redirects=True)
    assert response.status_code == 200
    assert b"Account deactivated" in response.data
    with app.app_context():
        assert db.session.get(User, customer_id).is_active_account is False
