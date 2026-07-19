from models import db

# Association Table
task_tags = db.Table(
    "task_tags",

    db.Column(
        "task_id",
        db.Integer,
        db.ForeignKey("tasks.id"),
        primary_key=True
    ),

    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id"),
        primary_key=True
    )
)


class Tag(db.Model):

    __tablename__ = "tags"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    color = db.Column(
        db.String(20),
        default="primary"
    )

    tasks = db.relationship(
        "Task",
        secondary=task_tags,
        back_populates="tags"
    )