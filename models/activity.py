from datetime import datetime
from models import db


class Activity(db.Model):

    __tablename__ = "activities"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    action = db.Column(
        db.String(300),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )