from datetime import datetime
from hashlib import sha256
import secrets

from app.extensions import db


class ApiToken(db.Model):
    __tablename__ = "api_tokens"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    token_prefix = db.Column(db.String(16), nullable=False, unique=True, index=True)
    token_hash = db.Column(db.String(64), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    is_revoked = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="api_tokens")

    @staticmethod
    def issue(user_id, name="Personal API token"):
        secret = secrets.token_urlsafe(32)
        prefix = secrets.token_hex(6)
        raw_token = f"ss_{prefix}.{secret}"
        token = ApiToken(
            user_id=user_id,
            name=name[:100],
            token_prefix=prefix,
            token_hash=sha256(raw_token.encode()).hexdigest(),
        )
        return token, raw_token
