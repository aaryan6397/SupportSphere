from app.extensions import db
from app.models.audit_log import AuditLog


def log_event(action, description, actor_id=None, entity_type=None, entity_id=None):
    """Add an explicit business-event audit record to the current transaction."""
    db.session.add(AuditLog(
        action=action,
        description=description[:500],
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
    ))
