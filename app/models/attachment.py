from datetime import datetime

from app.extensions import db


class TicketAttachment(db.Model):
    __tablename__ = "ticket_attachments"

    id = db.Column(db.Integer, primary_key=True)

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    content_type = db.Column(
        db.String(100),
        nullable=True
    )

    file_size = db.Column(
        db.Integer,
        nullable=True
    )

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False
    )

    uploaded_by_id = db.Column(
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
        back_populates="attachments"
    )

    uploaded_by = db.relationship(
        "User",
        back_populates="uploaded_attachments"
    )

    def __repr__(self):
        return f"<TicketAttachment {self.original_filename}>"