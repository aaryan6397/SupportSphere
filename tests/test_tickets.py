from io import BytesIO

from app.extensions import db
from app.models.ticket import Ticket
from app.models.user import User


def test_customer_can_create_ticket(client, app):
    with app.app_context():
        customer = User(
            name="Aryan Kumar",
            email="aryan@example.com",
            role="customer"
        )

        customer.set_password("Password123")

        db.session.add(customer)
        db.session.commit()

    client.post(
        "/auth/login",
        data={
            "email": "aryan@example.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    response = client.post(
        "/tickets/new",
        data={
            "subject": "Payment deducted but order failed",
            "category": "Payment",
            "priority": "high",
            "description": "Amount was deducted but order was not created."
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"was created successfully" in response.data

    with app.app_context():
        ticket = Ticket.query.first()

        assert ticket is not None
        assert ticket.category == "Payment"
        assert ticket.priority == "high"
        assert ticket.status == "open"
        assert ticket.sla_due_at is not None


def test_ticket_rejects_disguised_attachment(client, app):
    with app.app_context():
        customer = User(name="Aryan Kumar", email="aryan@example.com", role="customer")
        customer.set_password("Password123")
        db.session.add(customer)
        db.session.commit()

    client.post("/auth/login", data={"email": "aryan@example.com", "password": "Password123"})
    response = client.post(
        "/tickets/new",
        data={
            "subject": "Attachment check",
            "category": "Product",
            "priority": "medium",
            "description": "Testing upload validation.",
            "attachment": (BytesIO(b"not a real PNG file"), "malicious.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"File content does not match its extension" in response.data
    with app.app_context():
        assert Ticket.query.count() == 0
