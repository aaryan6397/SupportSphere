from datetime import datetime
from uuid import uuid4

from app.extensions import db
from app.services.sla_service import calculate_sla_due_at, ticket_sla_status


def generate_ticket_code():
    return f"SUP-{uuid4().hex[:8].upper()}"


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)

    ticket_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
        default=generate_ticket_code
    )

    subject = db.Column(
        db.String(200),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="medium"
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="open"
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    assigned_agent_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    sla_due_at = db.Column(db.DateTime, nullable=True)

    first_responded_at = db.Column(db.DateTime, nullable=True)

    resolved_at = db.Column(db.DateTime, nullable=True)

    customer = db.relationship(
        "User",
        foreign_keys=[customer_id],
        back_populates="created_tickets"
    )

    assigned_agent = db.relationship(
        "User",
        foreign_keys=[assigned_agent_id],
        back_populates="assigned_tickets"
    )

    comments = db.relationship(
        "TicketComment",
        back_populates="ticket",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="TicketComment.created_at"
    )

    attachments = db.relationship(
        "TicketAttachment",
        back_populates="ticket",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="TicketAttachment.created_at.desc()"
    )

    feedback = db.relationship(
        "TicketFeedback",
        back_populates="ticket",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ticket {self.ticket_code}>"

    @property
    def is_sla_breached(self):
        return ticket_sla_status(self) == "BREACHED"

    @property
    def sla_status(self):
        return ticket_sla_status(self)
