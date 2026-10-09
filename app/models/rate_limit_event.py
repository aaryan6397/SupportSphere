from datetime import datetime

from app.extensions import db


class RateLimitEvent(db.Model):
    __tablename__ = "rate_limit_events"

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    key_hash = db.Column(db.String(64), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
