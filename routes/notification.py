from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models.notification import Notification
from models import db
from flask import g

notification = Blueprint("notification", __name__)



@notification.route("/notifications")
@login_required
def notifications():

    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return render_template(
        "notifications/notifications.html",
        notifications=notifications
    )


@notification.route("/notifications/read/<int:id>")
@login_required
def mark_read(id):

    note = Notification.query.get_or_404(id)

    if note.user_id != current_user.id:
        return redirect(
            url_for("notification.notifications")
        )

    note.is_read = True

    db.session.commit()

    return redirect(
        url_for("notification.notifications")
    )

@notification.route("/notification-test")
def notification_test():
    return "Notification Blueprint Working"

@notification.app_context_processor
def inject_notification_count():

    if current_user.is_authenticated:

        unread_count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()

    else:

        unread_count = 0

    return dict(unread_notifications=unread_count)