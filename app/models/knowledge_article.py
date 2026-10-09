from datetime import datetime
from uuid import uuid4

from app.extensions import db


def article_slug(title):
    words = "".join(character.lower() if character.isalnum() else "-" for character in title)
    cleaned = "-".join(part for part in words.split("-") if part)
    return f"{cleaned[:110]}-{uuid4().hex[:8]}"


class KnowledgeArticle(db.Model):
    __tablename__ = "knowledge_articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(140), nullable=False, unique=True, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    summary = db.Column(db.String(400), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false(), index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = db.relationship("User", back_populates="knowledge_articles")
