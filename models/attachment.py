from datetime import datetime

from models import db


class Attachment(db.Model):

    __tablename__ = "attachments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    task = db.relationship(
        "Task",
        backref=db.backref(
            "attachments",
            cascade="all, delete-orphan"
        )
    )

    user = db.relationship(
        "User",
        backref="attachments"
    )