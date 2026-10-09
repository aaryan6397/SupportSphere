from datetime import datetime, timedelta
from hashlib import sha256

from app.extensions import db
from app.models.rate_limit_event import RateLimitEvent


def _key_hash(identifier):
    return sha256(identifier.encode("utf-8")).hexdigest()


def is_rate_limited(action, identifier, limit, window_seconds):
    cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
    count = RateLimitEvent.query.filter(
        RateLimitEvent.action == action,
        RateLimitEvent.key_hash == _key_hash(identifier),
        RateLimitEvent.created_at >= cutoff,
    ).count()
    return count >= limit


def record_rate_limit_event(action, identifier):
    db.session.add(RateLimitEvent(action=action, key_hash=_key_hash(identifier)))
    db.session.commit()
