from flask import Blueprint, send_file
from flask_login import login_required, current_user

from openpyxl import Workbook

from models.project import Project
from models.task import Task

import os

export = Blueprint("export", __name__)


@export.route("/export/tasks")
@login_required
def export_tasks():

    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Tasks"

    # Header Row
    sheet.append([
        "Task Title",
        "Project",
        "Priority",
        "Status",
        "Due Date",
        "Assigned To"
    ])

    tasks = Task.query.filter_by(
        owner_id=current_user.id
    ).all()

    for task in tasks:

        project = Project.query.get(task.project_id)

        assigned = "Unassigned"

        if task.assignee and task.assignee.user:
            assigned = task.assignee.user.full_name
            
        sheet.append([
            task.title,
            project.name if project else "",
            task.priority,
            task.status,
            str(task.due_date) if task.due_date else "",
            assigned
        ])

    export_folder = os.path.join(
        os.getcwd(),
        "exports"
    )

    os.makedirs(export_folder, exist_ok=True)

    file_path = os.path.join(
        export_folder,
        "tasks.xlsx"
    )

    workbook.save(file_path)

    return send_file(
        file_path,
        as_attachment=True
    )