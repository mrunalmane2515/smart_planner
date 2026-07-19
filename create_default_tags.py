from app import app
from models import db
from models.tag import Tag

default_tags = [

    ("Bug", "danger"),
    ("Feature", "success"),
    ("UI", "primary"),
    ("Backend", "dark"),
    ("Documentation", "warning"),
    ("Testing", "info"),
    ("Urgent", "secondary")

]

with app.app_context():

    for name, color in default_tags:

        exists = Tag.query.filter_by(
            name=name
        ).first()

        if not exists:

            db.session.add(
                Tag(
                    name=name,
                    color=color
                )
            )

    db.session.commit()

print("Default Tags Created Successfully!")