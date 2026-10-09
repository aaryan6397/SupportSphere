from app.extensions import db
from app.models.comment import TicketComment
from app.models.audit_log import AuditLog
from app.models.api_token import ApiToken
from app.models.attachment import TicketAttachment
from app.models.feedback import TicketFeedback
from app.models.notification import Notification
from app.models.ticket import Ticket
from app.models.user import User
from app.services.sla_service import calculate_sla_due_at


def _user(name, email, role):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, role=role)
        user.set_password("Password123")
        db.session.add(user)
        db.session.flush()
    return user


def seed_development_data():
    """Create idempotent, fictional data for local demos only."""
    admin = _user("Demo Admin", "admin@supportsphere.test", "admin")
    agent_one = _user("Aaryan Support", "aaryan@supportsphere.test", "agent")
    agent_two = _user("Priya Support", "priya@supportsphere.test", "agent")
    customer = _user("Demo Customer", "customer@supportsphere.test", "customer")

    samples = [
        ("Critical payment deduction", "Payment", "critical", "Payment was deducted but the order did not complete.", "assigned", agent_one),
        ("Cannot access account", "Account", "high", "Password is accepted but dashboard does not open.", "in_progress", agent_two),
        ("Update account phone number", "Account", "medium", "Please explain how to update a verified phone number.", "waiting_customer", agent_one),
        ("Product information request", "Product", "low", "I need compatibility information before placing an order.", "resolved", agent_two),
    ]
    created = 0
    for subject, category, priority, description, status, agent in samples:
        ticket = Ticket.query.filter_by(subject=subject, customer_id=customer.id).first()
        if ticket:
            continue
        ticket = Ticket(
            subject=subject, category=category, priority=priority, description=description,
            status=status, customer_id=customer.id, assigned_agent_id=agent.id,
            sla_due_at=calculate_sla_due_at(priority),
        )
        db.session.add(ticket)
        db.session.flush()
        db.session.add(TicketComment(
            message="We have received your request and are reviewing it.",
            ticket_id=ticket.id, author_id=agent.id,
        ))
        created += 1
    db.session.commit()
    return created


def purge_development_data():
    """Remove only records created by seed_development_data, preserving real accounts and tickets."""
    demo_users = User.query.filter(User.email.like("%@supportsphere.test")).all()
    demo_ids = [user.id for user in demo_users]
    if not demo_ids:
        return 0, 0

    demo_tickets = Ticket.query.filter(Ticket.customer_id.in_(demo_ids)).all()
    ticket_ids = [ticket.id for ticket in demo_tickets]

    # Preserve real tickets even if one happened to be assigned to a demo agent.
    Ticket.query.filter(
        Ticket.assigned_agent_id.in_(demo_ids),
        ~Ticket.id.in_(ticket_ids),
    ).update({Ticket.assigned_agent_id: None}, synchronize_session=False)

    if ticket_ids:
        for ticket in demo_tickets:
            db.session.delete(ticket)

    TicketComment.query.filter(TicketComment.author_id.in_(demo_ids)).delete(synchronize_session=False)
    TicketAttachment.query.filter(TicketAttachment.uploaded_by_id.in_(demo_ids)).delete(synchronize_session=False)
    TicketFeedback.query.filter(TicketFeedback.customer_id.in_(demo_ids)).delete(synchronize_session=False)
    Notification.query.filter(Notification.user_id.in_(demo_ids)).delete(synchronize_session=False)
    ApiToken.query.filter(ApiToken.user_id.in_(demo_ids)).delete(synchronize_session=False)
    AuditLog.query.filter(AuditLog.actor_id.in_(demo_ids)).delete(synchronize_session=False)

    for user in demo_users:
        db.session.delete(user)
    db.session.commit()
    return len(demo_ids), len(ticket_ids)
