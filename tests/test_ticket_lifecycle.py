from app.extensions import db
from app.models.comment import TicketComment
from app.models.notification import Notification
from app.models.ticket import Ticket
from app.models.user import User
from app.services.ticket_service import transition_ticket


def create_users_and_ticket(app):
    with app.app_context():
        customer = User(name="Customer", email="customer@example.com", role="customer")
        customer.set_password("Password123")
        agent = User(name="Agent", email="agent@example.com", role="agent")
        agent.set_password("Password123")
        db.session.add_all([customer, agent])
        db.session.flush()
        ticket = Ticket(
            subject="Login issue",
            category="Account",
            priority="high",
            description="I cannot log in.",
            customer_id=customer.id,
            assigned_agent_id=agent.id,
            status="assigned",
        )
        db.session.add(ticket)
        db.session.commit()
        return customer.id, agent.id, ticket.id


def test_ticket_rejects_invalid_transition(app):
    _, _, ticket_id = create_users_and_ticket(app)
    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)
        success, _ = transition_ticket(ticket, "closed")
        assert success is False
        assert ticket.status == "assigned"


def test_customer_cannot_see_internal_note(client, app):
    customer_id, agent_id, ticket_id = create_users_and_ticket(app)
    with app.app_context():
        db.session.add(TicketComment(
            message="Public update for the customer.",
            ticket_id=ticket_id,
            author_id=agent_id,
            is_internal=False,
        ))
        db.session.add(TicketComment(
            message="Private internal investigation note.",
            ticket_id=ticket_id,
            author_id=agent_id,
            is_internal=True,
        ))
        db.session.commit()

    client.post("/auth/login", data={
        "email": "customer@example.com", "password": "Password123"
    })
    response = client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200
    assert b"Public update for the customer." in response.data
    assert b"Private internal investigation note." not in response.data


def test_customer_can_reopen_resolved_ticket(client, app):
    customer_id, _, ticket_id = create_users_and_ticket(app)
    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)
        ticket.status = "resolved"
        db.session.commit()

    client.post("/auth/login", data={
        "email": "customer@example.com", "password": "Password123"
    })
    response = client.post(f"/tickets/{ticket_id}/reopen", follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        assert db.session.get(Ticket, ticket_id).status == "reopened"


def test_dashboard_search_is_role_scoped(client, app):
    _, _, ticket_id = create_users_and_ticket(app)

    client.post("/auth/login", data={
        "email": "customer@example.com", "password": "Password123"
    })
    customer_response = client.get("/dashboard?q=Login")
    assert customer_response.status_code == 200
    assert b"Login issue" in customer_response.data

    client.post("/auth/logout")
    client.post("/auth/login", data={
        "email": "agent@example.com", "password": "Password123"
    })
    agent_response = client.get("/agent/dashboard?q=Login")
    assert agent_response.status_code == 200
    assert b"Login issue" in agent_response.data


def test_status_change_creates_customer_notification(client, app):
    customer_id, _, ticket_id = create_users_and_ticket(app)
    client.post("/auth/login", data={
        "email": "agent@example.com", "password": "Password123"
    })
    response = client.post(
        f"/agent/tickets/{ticket_id}/status",
        data={"status": "in_progress"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    with app.app_context():
        notification = Notification.query.filter_by(user_id=customer_id).first()
        assert notification is not None
        assert notification.title == "Ticket status updated"
