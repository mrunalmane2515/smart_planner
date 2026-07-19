from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.project import Project

project_dashboard = Blueprint(
    "project_dashboard",
    __name__
)


@project_dashboard.route("/project-dashboard")
@login_required
def dashboard():

    projects = Project.query.filter_by(
        owner_id=current_user.id
    ).all()

    stats = []

    total_projects = len(projects)

    total_tasks = 0
    completed_tasks = 0
    pending_tasks = 0

    for project in projects:

        tasks = project.tasks

        total = len(tasks)

        completed = len([
            t for t in tasks
            if t.status == "Completed"
        ])

        pending = total - completed

        progress = 0

        if total:
            progress = round(
                completed * 100 / total
            )

        total_tasks += total
        completed_tasks += completed
        pending_tasks += pending

        stats.append({
            "project": project,
            "total": total,
            "completed": completed,
            "pending": pending,
            "progress": progress
        })

    return render_template(
        "projects/project_dashboard.html",
        stats=stats,
        total_projects=total_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks
    )