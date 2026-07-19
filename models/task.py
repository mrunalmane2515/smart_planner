from models import db
from datetime import date

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    priority = db.Column(
        db.String(30),
        default="Medium"
    )

    attachment = db.Column(
        db.String(255),
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="To Do"
    )

    due_date = db.Column(
        db.Date
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    comments = db.relationship(
        "Comment",
        backref="task",
        lazy=True,
        cascade="all, delete-orphan"
    )

    assigned_to = db.Column(
        db.Integer,
        db.ForeignKey("team_members.id"),
        nullable=True
    )

    assignee = db.relationship(
        "TeamMember",
        back_populates="tasks",
        foreign_keys=[assigned_to]
    )

    tags = db.relationship(
        "Tag",
        secondary="task_tags",
        back_populates="tasks"
    )



    @property
    def is_overdue(self):
        return (
                self.due_date is not None
                and self.due_date < date.today()
                and self.status != "Completed"
        )

