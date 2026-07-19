from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for
from models.team_member import TeamMember
from models.task import Task
from models import db
from models.project import Project
from models.notification import Notification

from activity_utils import log_activity
project = Blueprint("project", __name__)


@project.route("/projects")
@login_required
def projects():

    all_projects = Project.query.filter_by(
        owner_id=current_user.id
    ).all()

    # Calculate progress for each project
    for single_project in all_projects:

        total_tasks = len(single_project.tasks)

        if total_tasks == 0:

            single_project.progress = 0
            single_project.status = "Active"

        else:

            completed = sum(
                1
                for task in single_project.tasks
                if task.status == "Completed"
            )

            single_project.progress = int(
                (completed / total_tasks) * 100
            )

            if completed == total_tasks:

                single_project.status = "Completed"

            else:

                single_project.status = "Active"

    db.session.commit()

    return render_template(
        "projects/projects.html",
        projects=all_projects
    )


@project.route("/projects/add", methods=["GET", "POST"])
@login_required
def add_project():

    if request.method == "POST":

        name = request.form.get("name")
        description = request.form.get("description")

        new_project = Project(
            name=name,
            description=description,
            owner_id=current_user.id
        )

        db.session.add(new_project)
        db.session.commit()
        notification = Notification(
            user_id=current_user.id,
            message=f'Project "{new_project.name}" was created successfully.'
        )

        db.session.add(notification)
        db.session.commit()



        log_activity(
            current_user.id,
            f'Created project "{new_project.name}"'
        )

        return redirect(url_for("project.projects"))

    return render_template("projects/add_project.html")


@project.route("/projects/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_project(id):

    selected_project = Project.query.filter_by(
        id=id,
        owner_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        selected_project.name = request.form.get("name")
        selected_project.description = request.form.get("description")

        db.session.commit()

        log_activity(
            current_user.id,
            f'Updated project "{selected_project.name}"'
        )

        return redirect(url_for("project.projects"))

    return render_template(
        "projects/edit_project.html",
        project=selected_project
    )


@project.route("/projects/delete/<int:id>")
@login_required
def delete_project(id):

    selected_project = Project.query.filter_by(
        id=id,
        owner_id=current_user.id
    ).first_or_404()

    project_name = selected_project.name

    # Delete team members
    TeamMember.query.filter_by(
        project_id=selected_project.id
    ).delete()

    # Delete tasks
    Task.query.filter_by(
        project_id=selected_project.id
    ).delete()

    # Delete project
    db.session.delete(selected_project)

    db.session.commit()

    log_activity(
        current_user.id,
        f'Deleted project "{project_name}"'
    )

    return redirect(url_for("project.projects"))