from datetime import datetime

from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    action = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(500),
        nullable=False
    )

    entity_type = db.Column(
        db.String(50),
        nullable=True
    )

    entity_id = db.Column(
        db.Integer,
        nullable=True
    )

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    actor = db.relationship(
        "User",
        foreign_keys=[actor_id]
    )

    def __repr__(self):
        return f"<AuditLog {self.action}>"