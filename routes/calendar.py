from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.task import Task

calendar = Blueprint("calendar", __name__)


@calendar.route("/calendar")
@login_required
def calendar_view():

    tasks = Task.query.filter_by(
        owner_id=current_user.id
    ).all()

    events = []

    for task in tasks:

        if task.due_date:

            color = "#0d6efd"

            if task.status == "Completed":
                color = "#198754"

            elif task.status == "In Progress":
                color = "#ffc107"

            elif task.status == "To Do":
                color = "#dc3545"

            events.append({
                "title": task.title,
                "start": task.due_date.strftime("%Y-%m-%d"),
                "color": color
            })

    return render_template(
        "calendar/calendar.html",
        events=events
    )