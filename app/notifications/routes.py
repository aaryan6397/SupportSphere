from flask import abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.notification import Notification
from app.notifications import notifications_bp


@notifications_bp.route("/")
@login_required
def index():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()
    return render_template("notifications/index.html", notifications=notifications)


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    notification = db.get_or_404(Notification, notification_id)
    if notification.user_id != current_user.id:
        abort(403)
    notification.is_read = True
    db.session.commit()
    return redirect(notification.link or url_for("notifications.index"))


@notifications_bp.route("/read-all", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update(
        {Notification.is_read: True}, synchronize_session=False
    )
    db.session.commit()
    return redirect(request.referrer or url_for("notifications.index"))
