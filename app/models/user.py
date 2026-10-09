from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.String(20),
        nullable=False,
        default="customer"
    )

    is_active_account = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    password_reset_version = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        server_default="0"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    created_tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.customer_id",
        back_populates="customer",
        lazy=True
    )

    assigned_tickets = db.relationship(
        "Ticket",
        foreign_keys="Ticket.assigned_agent_id",
        back_populates="assigned_agent",
        lazy=True
    )

    comments = db.relationship(
        "TicketComment",
        back_populates="author",
        lazy=True
    )

    uploaded_attachments = db.relationship(
        "TicketAttachment",
        back_populates="uploaded_by",
        lazy=True
    )

    feedback_entries = db.relationship(
        "TicketFeedback",
        back_populates="customer",
        lazy=True
    )

    notifications = db.relationship(
        "Notification",
        back_populates="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    knowledge_articles = db.relationship(
        "KnowledgeArticle",
        back_populates="created_by",
        lazy=True
    )

    api_tokens = db.relationship(
        "ApiToken",
        back_populates="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
