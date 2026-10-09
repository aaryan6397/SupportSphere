from app.extensions import db
from app.models.notification import Notification


def create_notification(user_id, title, message, link=None):
    """Queue an in-app notification in the current database transaction."""
    notification = Notification(
        user_id=user_id,
        title=title[:160],
        message=message[:500],
        link=link,
    )
    db.session.add(notification)
    return notification
