from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
from flask import Response
from flask_login import login_required, current_user
from datetime import datetime, date
from flask_mail import Message
from email_utils import send_task_reminder
from models import db
from models.project import Project
from models.task import Task
from models.notification import Notification
from models.team_member import TeamMember
from models.tag import Tag
import os
from models.attachment import Attachment
from werkzeug.utils import secure_filename
from flask import current_app
from flask import send_file
from pdf_utils import generate_project_report
import tempfile
from flask import jsonify
from activity_utils import log_activity
from extensions import mail
from email_utils import send_task_assigned_email

UPLOAD_FOLDER = "static/uploads"

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "pdf",
    "doc",
    "docx",
    "xlsx",
    "ppt",
    "pptx",
    "txt",
    "zip"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )

task = Blueprint("task", __name__)


# ==============================
# View Tasks
# ==============================
@task.route("/projects/<int:project_id>/tasks")
@login_required
def view_tasks(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    search = request.args.get("search", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")

    query = Task.query.filter_by(
        project_id=project.id
    )

    if search:
        query = query.filter(
            Task.title.ilike(f"%{search}%")
        )

    if status:
        query = query.filter(
            Task.status == status
        )

    if priority:
        query = query.filter(
            Task.priority == priority
        )

    # Sort tasks by due date
    tasks = query.order_by(
        Task.due_date.asc()
    ).all()

    return render_template(
        "tasks/tasks.html",
        project=project,
        tasks=tasks,
        search=search,
        status=status,
        priority=priority
    )


# ==============================
# Add Task
# ==============================
@task.route("/projects/<int:project_id>/tasks/add", methods=["GET", "POST"])
@login_required
def add_task(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        due_date = None

        if request.form["due_date"]:
            due_date = datetime.strptime(
                request.form["due_date"],
                "%Y-%m-%d"
            ).date()

        # ---------------- File Upload ---------------- #

        filename = None

        file = request.files.get("attachment")

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads"
            )

            os.makedirs(upload_folder, exist_ok=True)

            file.save(
                os.path.join(upload_folder, filename)
            )

        # --------------------------------------------- #
        assigned_to = request.form.get("assigned_to")

        if assigned_to == "":
            assigned_to = None

        new_task = Task(
            title=request.form["title"],
            description=request.form["description"],
            priority=request.form["priority"],
            status=request.form["status"],
            due_date=due_date,
            attachment=filename,
            owner_id=current_user.id,
            project_id=project.id,
            assigned_to=assigned_to,
        )

        db.session.add(new_task)

        selected_tags = request.form.getlist("tags")

        for tag_id in selected_tags:

            tag = Tag.query.get(int(tag_id))

            if tag:
                new_task.tags.append(tag)

        db.session.commit()

        uploaded_file = request.files.get("attachment")

        if uploaded_file and uploaded_file.filename != "":

            if allowed_file(uploaded_file.filename):
                filename = secure_filename(
                    uploaded_file.filename
                )

                save_path = os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )

                uploaded_file.save(save_path)

                attachment = Attachment(

                    filename=filename,

                    original_filename=uploaded_file.filename,

                    task_id=new_task.id,

                    user_id=current_user.id

                )

                db.session.add(attachment)

                db.session.commit()

        # Create notification if task is assigned
        from email_utils import send_task_reminder

        if new_task.assigned_to:

            member = TeamMember.query.get(new_task.assigned_to)

            if member:
                notification = Notification(
                    user_id=current_user.id,
                    message=f'Task "{new_task.title}" assigned to {member.user.full_name}.'
                )

                db.session.add(notification)
                db.session.commit()

                # Send email to assigned member
                # try:
                #     send_task_reminder(
                #         user_email=member.user.email,
                #         task_title=new_task.title,
                #         due_date=new_task.due_date.strftime("%d %b %Y")
                #         if new_task.due_date else "No Due Date"
                #     )
                # except Exception as e:
                #     print("Email failed:", e)
                log_activity(
                    current_user.id,
                    f'Created task "{new_task.title}"'
                )

        flash("Task added successfully!", "success")

        return redirect(
            url_for(
                "task.view_tasks",
                project_id=project.id
            )
        )

    # ← This is OUTSIDE the POST block, but INSIDE add_task()

    members = project.team_members
    tags = Tag.query.order_by(Tag.name).all()

    print("Total Tags:", len(tags))

    for tag in tags:
        print(tag.id, tag.name)

    return render_template(
        "tasks/add_task.html",
        project=project,
        members=members,
        tags=tags
    )
# ==============================
# Edit Task
# ==============================
@task.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):

    task_item = Task.query.filter_by(
        id=task_id,
        owner_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        old_status = task_item.status
        old_assigned_to = task_item.assigned_to

        task_item.title = request.form["title"]
        task_item.description = request.form["description"]
        task_item.priority = request.form["priority"]
        task_item.status = request.form["status"]

        # Assign Team Member
        # Update assigned member
        assigned_to = request.form.get("assigned_to")

        if assigned_to and assigned_to.strip():
            task_item.assigned_to = int(assigned_to)
        else:
            task_item.assigned_to = None

        # Due Date
        if request.form["due_date"]:
            task_item.due_date = datetime.strptime(
                request.form["due_date"],
                "%Y-%m-%d"
            ).date()
        else:
            task_item.due_date = None

        # ---------------- Update Tags ---------------- #

        task_item.tags.clear()

        selected_tags = request.form.getlist("tags")

        for tag_id in selected_tags:

            tag = Tag.query.get(int(tag_id))

            if tag:
                task_item.tags.append(tag)

        # --------------------------------------------- #

        # File Upload
        file = request.files.get("attachment")

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads"
            )

            os.makedirs(upload_folder, exist_ok=True)

            file.save(
                os.path.join(upload_folder, filename)
            )

            task_item.attachment = filename

        db.session.commit()

        # Send email if assignee changed
        if old_assigned_to != task_item.assigned_to and task_item.assigned_to:

            member = TeamMember.query.get(task_item.assigned_to)

            if member:
                from email_utils import send_task_reminder
                try:
                    send_task_reminder(
                        user_email=member.user.email,
                        task_title=new_task.title,
                        due_date=new_task.due_date.strftime("%d %b %Y")
                        if new_task.due_date else "No Due Date"
                    )
                except Exception as e:
                    print("Email failed:", e)

                notification = Notification(
                    user_id=member.user.id,
                    message=f'You have been assigned task "{task_item.title}".'
                )

                db.session.add(notification)
                db.session.commit()

        log_activity(
            current_user.id,
            f'Updated task "{task_item.title}"'
        )

        flash("Task updated successfully!", "success")

        return redirect(
            url_for(
                "task.view_tasks",
                project_id=task_item.project_id
            )
        )

    tags = Tag.query.order_by(Tag.name).all()

    members = TeamMember.query.filter_by(
        project_id=task_item.project_id
    ).all()

    return render_template(
        "tasks/edit_task.html",
        task=task_item,
        members=members,
        tags=tags
    )
# ==============================
# Delete Task
# ==============================
@task.route("/tasks/<int:task_id>/delete")
@login_required
def delete_task(task_id):

    task_item = Task.query.filter_by(
        id=task_id,
        owner_id=current_user.id
    ).first_or_404()

    project_id = task_item.project_id

    task_title = task_item.title

    db.session.delete(task_item)
    db.session.commit()

    log_activity(
        current_user.id,
        f'Deleted task "{task_title}"'
    )

    flash("Task deleted successfully!", "success")

    return redirect(
        url_for(
            "task.view_tasks",
            project_id=project_id
        )
    )

@task.route("/projects/<int:project_id>/kanban")
@login_required
def kanban(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    todo = Task.query.filter_by(
        project_id=project.id,
        status="To Do"
    ).all()

    in_progress = Task.query.filter_by(
        project_id=project.id,
        status="In Progress"
    ).all()

    completed = Task.query.filter_by(
        project_id=project.id,
        status="Completed"
    ).all()

    return render_template(
        "tasks/kanban.html",
        project=project,
        todo=todo,
        in_progress=in_progress,
        completed=completed
    )

@task.route("/projects/<int:project_id>/tasks/export")
@login_required
def export_tasks(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    tasks = Task.query.filter_by(
        project_id=project.id
    ).all()

    def generate():

        yield "Title,Description,Priority,Status,Due Date\n"

        for task in tasks:

            yield (
                f"{task.title},"
                f"{task.description},"
                f"{task.priority},"
                f"{task.status},"
                f"{task.due_date}\n"
            )

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename={project.name}_tasks.csv"
        }
    )

@task.route("/projects/<int:project_id>/tasks/pdf")
@login_required
def export_pdf(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    tasks = Task.query.filter_by(
        project_id=project.id
    ).all()

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    generate_project_report(
        project,
        tasks,
        temp.name
    )

    return send_file(
        temp.name,
        as_attachment=True,
        download_name=f"{project.name}_Report.pdf"
    )

@task.route("/tasks/<int:task_id>/move", methods=["POST"])
@login_required
def move_task(task_id):

    task_item = Task.query.filter_by(
        id=task_id,
        owner_id=current_user.id
    ).first_or_404()

    new_status = request.form.get("status")

    if new_status in ["To Do", "In Progress", "Completed"]:
        task_item.status = new_status
        db.session.commit()

        log_activity(
            current_user.id,
            f'Moved "{task_item.title}" to {new_status}'
        )
    return "", 204

