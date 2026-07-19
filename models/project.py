from models import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(120),
        nullable=False
    )


    description = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        default="Active"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    tasks = db.relationship(
        "Task",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan"
    )

    team_members = db.relationship(
        "TeamMember",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy=True
    )