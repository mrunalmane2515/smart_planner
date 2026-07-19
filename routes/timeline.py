from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.project import Project
from models.task import Task

timeline = Blueprint(
    "timeline",
    __name__
)


@timeline.route("/projects/<int:project_id>/timeline")
@login_required
def view(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    tasks = Task.query.filter_by(
        project_id=project.id
    ).all()

    return render_template(
        "timeline/timeline.html",
        project=project,
        tasks=tasks
    )