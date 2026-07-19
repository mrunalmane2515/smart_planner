from flask import Blueprint, send_file
from flask_login import login_required, current_user
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from models.project import Project
from models.task import Task

import os

pdf_report = Blueprint("pdf_report", __name__)


@pdf_report.route("/report/pdf")
@login_required
def generate_pdf():

    reports_folder = os.path.join(
        os.getcwd(),
        "reports"
    )

    os.makedirs(reports_folder, exist_ok=True)

    file_path = os.path.join(
        reports_folder,
        "Smart_Task_Report.pdf"
    )

    doc = SimpleDocTemplate(file_path)

    styles = getSampleStyleSheet()

    elements = []

    # ---------------- Header ---------------- #

    title = Paragraph(
        "<b><font size=20>Smart Task Manager</font></b>",
        styles["Title"]
    )

    subtitle = Paragraph(
        "Project & Task Report",
        styles["Heading2"]
    )

    report_date = Paragraph(
        f"<b>Generated:</b> {datetime.now().strftime('%d %B %Y %I:%M %p')}",
        styles["Normal"]
    )

    elements.append(title)
    elements.append(subtitle)
    elements.append(report_date)
    elements.append(Spacer(1, 0.30 * inch))
    # ---------------- User Info ---------------- #

    user_info = [
        ["User", current_user.full_name],
        ["Email", current_user.email]
    ]

    table = Table(user_info)

    table.setStyle(TableStyle([

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("BACKGROUND", (0,0), (0,-1), colors.lightblue),

        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0,0), (-1,-1), 8)

    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.25 * inch))

    # ---------------- Statistics ---------------- #

    total_projects = Project.query.filter_by(
        owner_id=current_user.id
    ).count()

    total_tasks = Task.query.filter_by(
        owner_id=current_user.id
    ).count()

    completed = Task.query.filter_by(
        owner_id=current_user.id,
        status="Completed"
    ).count()

    completion_rate = 0

    if total_tasks > 0:
        completion_rate = round(
            (completed / total_tasks) * 100,
            1
        )

    in_progress = Task.query.filter_by(
        owner_id=current_user.id,
        status="In Progress"
    ).count()

    todo = Task.query.filter_by(
        owner_id=current_user.id,
        status="To Do"
    ).count()

    overdue = len([
        t for t in Task.query.filter_by(
            owner_id=current_user.id
        ).all()
        if t.is_overdue
    ])

    stats = [

        ["Metric", "Value"],

        ["Projects", total_projects],

        ["Tasks", total_tasks],

        ["Completed", completed],

        ["In Progress", in_progress],

        ["To Do", todo],

        ["Overdue", overdue],
        ["Completion", f"{completion_rate}%"]

    ]

    stats_table = Table(stats)

    stats_table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold")

    ]))

    elements.append(stats_table)
    elements.append(Spacer(1,0.35*inch))

    # ---------------- Task List ---------------- #

    elements.append(
        Paragraph(
            "<b>Task Details</b>",
            styles["Heading2"]
        )
    )

    task_data = [[
        "Title",
        "Project",
        "Priority",
        "Status",
        "Due Date"
    ]]

    tasks = Task.query.filter_by(
        owner_id=current_user.id
    ).all()

    for task in tasks:

        project = Project.query.get(task.project_id)

        task_data.append([

            task.title,

            project.name if project else "",

            task.priority,

            task.status,

            str(task.due_date) if task.due_date else "-"

        ])

    task_table = Table(task_data)

    task_table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.green),

        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke),

        ("FONTSIZE",(0,0),(-1,-1),9)

    ]))

    elements.append(task_table)

    elements.append(Spacer(1,0.40*inch))

    footer = Paragraph(

        "Generated automatically by Smart Task Manager",

        styles["Italic"]

    )

    elements.append(footer)

    doc.build(elements)

    return send_file(
        file_path,
        as_attachment=True
    )