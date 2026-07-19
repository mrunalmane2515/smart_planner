from models import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    text = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id"),
        nullable=False
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )