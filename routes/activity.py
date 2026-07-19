from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.activity import Activity

activity = Blueprint("activity", __name__)


@activity.route("/activity")
@login_required
def activity_log():

    activities = Activity.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Activity.created_at.desc()
    ).all()

    return render_template(
        "activity/activity.html",
        activities=activities
    )