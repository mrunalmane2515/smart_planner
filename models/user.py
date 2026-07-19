from models import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    profile_image = db.Column(
        db.String(255),
        default="default.png"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    projects = db.relationship(
        "Project",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )