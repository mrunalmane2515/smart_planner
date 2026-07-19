from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.task import Task
from models.project import Project

from datetime import date, timedelta
from collections import Counter
from datetime import datetime

analytics = Blueprint("analytics", __name__)


@analytics.route("/analytics")
@login_required
def dashboard():

    projects = Project.query.filter_by(
        owner_id=current_user.id
    ).all()

    project_ids = [p.id for p in projects]

    tasks = Task.query.filter(
        Task.project_id.in_(project_ids)
    ).all()

    total_tasks = len(tasks)

    completed = len([
        t for t in tasks
        if t.status == "Completed"
    ])

    in_progress = len([
        t for t in tasks
        if t.status == "In Progress"
    ])

    todo = len([
        t for t in tasks
        if t.status == "To Do"
    ])

    overdue = len([
        t for t in tasks
        if t.is_overdue
    ])

    high_priority = len([
        t for t in tasks
        if t.priority == "High"
    ])

    completion_rate = 0

    if total_tasks > 0:
        completion_rate = round(
            completed * 100 / total_tasks,
            1
        )

    # ---------------- Priority Counts ---------------- #

    high = len([
        t for t in tasks
        if t.priority == "High"
    ])

    medium = len([
        t for t in tasks
        if t.priority == "Medium"
    ])

    low = len([
        t for t in tasks
        if t.priority == "Low"
    ])

    # ---------------- Weekly Productivity ---------------- #

    today = date.today()

    week_labels = []
    week_values = []

    for i in range(6, -1, -1):

        day = today - timedelta(days=i)

        week_labels.append(
            day.strftime("%a")
        )

        completed_today = len([
            t for t in tasks
            if t.status == "Completed"
            and t.due_date == day
        ])

        week_values.append(completed_today)

    # ---------------- Monthly Task Creation ---------------- #

    monthly_counter = Counter()

    for task in tasks:

        if task.due_date:
            month = task.due_date.strftime("%b")

            monthly_counter[month] += 1

    month_order = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    monthly_labels = month_order

    monthly_values = [
        monthly_counter.get(month, 0)
        for month in month_order
    ]

    # ---------------- Project Distribution ---------------- #

    project_labels = []

    project_values = []

    for project in projects:
        project_labels.append(project.name)

        project_values.append(

            Task.query.filter_by(
                project_id=project.id
            ).count()

        )

    # ---------------- Upcoming Deadlines ---------------- #

    upcoming_tasks = (
        Task.query.filter(
            Task.owner_id == current_user.id,
            Task.due_date != None,
            Task.status != "Completed"
        )
        .order_by(Task.due_date.asc())
        .limit(5)
        .all()
    )

    # ---------------- Project Leaderboard ---------------- #

    project_stats = []

    for project in projects:

        project_tasks = Task.query.filter_by(
            project_id=project.id
        ).all()

        total = len(project_tasks)

        completed_count = len([
            t for t in project_tasks
            if t.status == "Completed"
        ])

        pending = total - completed_count

        progress = 0

        if total > 0:
            progress = round(
                completed_count * 100 / total,
                1
            )

        project_stats.append({

            "name": project.name,

            "total": total,

            "completed": completed_count,

            "pending": pending,

            "progress": progress

        })

    project_stats.sort(
        key=lambda x: x["progress"],
        reverse=True
    )

    return render_template(
        "analytics/dashboard.html",

        total_tasks=total_tasks,
        completed=completed,
        in_progress=in_progress,
        todo=todo,
        overdue=overdue,
        high_priority=high_priority,
        completion_rate=completion_rate,
        upcoming_tasks=upcoming_tasks,
        project_stats=project_stats,

        high=high,
        medium=medium,
        low=low,

        week_labels=week_labels,
        week_values=week_values,

        monthly_labels=monthly_labels,
        monthly_values=monthly_values,

        project_labels=project_labels,
        project_values=project_values
    )