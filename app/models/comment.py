from datetime import datetime

from app.extensions import db


class TicketComment(db.Model):
    __tablename__ = "ticket_comments"

    id = db.Column(db.Integer, primary_key=True)

    message = db.Column(db.Text, nullable=False)

    is_internal = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=db.false()
    )

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False
    )

    author_id = db.Column(
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
        back_populates="comments"
    )

    author = db.relationship(
        "User",
        back_populates="comments"
    )

    def __repr__(self):
        return f"<TicketComment {self.id}>"
