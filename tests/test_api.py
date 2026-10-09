from app.extensions import db
from app.models.api_token import ApiToken
from app.models.ticket import Ticket
from app.models.user import User


def test_api_requires_valid_bearer_token(client):
    response = client.get("/api/v1/tickets")
    assert response.status_code == 401
    assert response.json["error"]["code"] == "authentication_required"


def test_customer_api_lists_only_own_tickets(client, app):
    with app.app_context():
        customer = User(name="Customer", email="customer@example.com", role="customer")
        customer.set_password("Password123")
        other = User(name="Other", email="other@example.com", role="customer")
        other.set_password("Password123")
        db.session.add_all([customer, other])
        db.session.flush()
        db.session.add_all([
            Ticket(subject="My payment", category="Payment", priority="high", description="My issue", customer_id=customer.id),
            Ticket(subject="Private account", category="Account", priority="low", description="Other issue", customer_id=other.id),
        ])
        token, raw_token = ApiToken.issue(customer.id)
        db.session.add(token)
        db.session.commit()

    response = client.get("/api/v1/tickets", headers={"Authorization": f"Bearer {raw_token}"})
    assert response.status_code == 200
    assert response.json["pagination"]["total"] == 1
    assert response.json["data"][0]["subject"] == "My payment"


def test_customer_can_create_ticket_via_api(client, app):
    with app.app_context():
        customer = User(name="Customer", email="customer@example.com", role="customer")
        customer.set_password("Password123")
        db.session.add(customer)
        db.session.flush()
        token, raw_token = ApiToken.issue(customer.id)
        db.session.add(token)
        db.session.commit()

    response = client.post("/api/v1/tickets", headers={"Authorization": f"Bearer {raw_token}"}, json={
        "subject": "API payment issue", "category": "Payment", "priority": "critical", "description": "Payment failed."
    })
    assert response.status_code == 201
    assert response.json["data"]["priority"] == "critical"
