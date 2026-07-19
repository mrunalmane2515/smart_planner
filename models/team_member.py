from datetime import datetime
from models import db


class TeamMember(db.Model):

    __tablename__ = "team_members"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="Member"
    )

    joined_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    project = db.relationship(
        "Project",
        back_populates="team_members"
    )

    user = db.relationship(
        "User",
        backref="joined_projects"
    )

    tasks = db.relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assigned_to",
        lazy=True
    )