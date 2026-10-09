from datetime import datetime

from app.extensions import db


class TicketFeedback(db.Model):
    __tablename__ = "ticket_feedback"

    id = db.Column(db.Integer, primary_key=True)

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=True
    )

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False,
        unique=True
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    ticket = db.relationship(
        "Ticket",
        back_populates="feedback"
    )

    customer = db.relationship(
        "User",
        back_populates="feedback_entries"
    )

    def __repr__(self):
        return f"<TicketFeedback {self.rating}/5>"