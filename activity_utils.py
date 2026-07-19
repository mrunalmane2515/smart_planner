from models import db
from models.activity import Activity


def log_activity(user_id, action):

    activity = Activity(
        user_id=user_id,
        action=action
    )

    db.session.add(activity)
    db.session.commit()