from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from models.project import Project
from models.task import Task
from models.activity import Activity

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
@login_required
def home():

    total_projects = Project.query.filter_by(
        owner_id=current_user.id
    ).count()

    total_tasks = Task.query.filter_by(
        owner_id=current_user.id
    ).count()

    completed_tasks = Task.query.filter_by(
        owner_id=current_user.id,
        status="Completed"
    ).count()

    pending_tasks = Task.query.filter(
        Task.owner_id == current_user.id,
        Task.status != "Completed"
    ).count()

    recent_projects = Project.query.filter_by(
        owner_id=current_user.id
    ).order_by(
        Project.created_at.desc()
    ).limit(5).all()

    recent_tasks = Task.query.filter_by(
        owner_id=current_user.id
    ).order_by(
        Task.id.desc()
    ).limit(5).all()

    # All tasks for AI Assistant

    tasks = Task.query.filter_by(
        owner_id=current_user.id
    ).all()

    completed = Task.query.filter_by(
        owner_id=current_user.id,
        status="Completed"
    ).count()

    in_progress = Task.query.filter_by(
        owner_id=current_user.id,
        status="In Progress"
    ).count()

    todo = Task.query.filter_by(
        owner_id=current_user.id,
        status="To Do"
    ).count()

    recent_activity = Activity.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Activity.created_at.desc()
    ).limit(5).all()

    # ==============================
    # AI DAILY ASSISTANT
    # ==============================

    today = date.today()
    tomorrow = today + timedelta(days=1)

    overdue_tasks = [
        task for task in tasks
        if task.due_date
           and task.due_date < today
           and task.status != "Completed"
    ]

    due_today = [
        task for task in tasks
        if task.due_date == today
           and task.status != "Completed"
    ]

    due_tomorrow = [
        task for task in tasks
        if task.due_date == tomorrow
           and task.status != "Completed"
    ]

    completed_task_list = [
        task for task in tasks
        if task.status == "Completed"
    ]

    high_priority_tasks = [
        task for task in tasks
        if task.priority == "High"
           and task.status != "Completed"
    ]

    ai_suggestions = []

    if overdue_tasks:
        ai_suggestions.append(
            f"⚠️ You have {len(overdue_tasks)} overdue task(s). Complete them first."
        )

    if due_today:
        ai_suggestions.append(
            f"📅 {len(due_today)} task(s) are due today. Try to finish them before the deadline."
        )

    if due_tomorrow:
        ai_suggestions.append(
            f"🗓️ {len(due_tomorrow)} task(s) are due tomorrow. Starting today can reduce tomorrow's workload."
        )

    if high_priority_tasks:
        ai_suggestions.append(
            f"🔥 {len(high_priority_tasks)} high-priority task(s) need your attention."
        )

    # Celebration message
    if len(completed_task_list) >= 5:
        ai_suggestions.append(
            f"🎉 Great job! You've completed {len(completed_task_list)} tasks."
        )

    if not tasks:
        ai_suggestions.append(
            "✨ You have no tasks. Create your first task and stay productive!"
        )

    if not overdue_tasks and not due_today and tasks:
        ai_suggestions.append(
            "✅ You're on track. Keep up the good work!"
        )
    # Greeting

    current_hour = datetime.now().hour

    if current_hour < 12:

        greeting = "Good Morning ☀️"

    elif current_hour < 17:

        greeting = "Good Afternoon 🌤️"

    else:

        greeting = "Good Evening 🌙"

    # ===================================
    # AI ADVANCED INSIGHTS
    # ===================================

    # Top 3 priority tasks
    top_tasks = sorted(
        [
            task for task in tasks
            if task.status != "Completed"
        ],
        key=lambda t: (
            t.priority != "High",
            t.due_date if t.due_date else date.max
        )
    )[:3]

    # AI Recommended Task
    recommended_task = top_tasks[0] if top_tasks else None

    # Productivity Score
    productivity_score = 100

    productivity_score -= len(overdue_tasks) * 10

    productivity_score += completed_tasks * 2

    if productivity_score > 100:
        productivity_score = 100

    if productivity_score < 0:
        productivity_score = 0

    # Workload Level
    pending = len(tasks) - completed_tasks

    if pending <= 5:
        workload = "Low"

    elif pending <= 15:
        workload = "Medium"

    else:
        workload = "High"

    # Motivation Message

    if productivity_score >= 90:

        motivation = "🔥 Excellent work! You're highly productive."

    elif productivity_score >= 70:

        motivation = "👏 Great progress. Keep the momentum going."

    elif productivity_score >= 50:

        motivation = "💪 You're doing well. Finish today's important tasks."

    else:

        motivation = "⚠️ Your workload is increasing. Focus on overdue tasks first."

    # =====================================
    # AI INSIGHT OF THE DAY
    # =====================================

    insight = "Everything looks balanced today."

    if len(overdue_tasks) >= 5:
        insight = "You have several overdue tasks. Completing them first will improve your productivity."

    elif len(high_priority_tasks) >= 3:
        insight = "Your workload contains several high-priority tasks. Focus on those before low-priority work."

    elif productivity_score >= 90:
        insight = "Excellent productivity! Maintain this pace."

    elif completed_tasks >= 5:
        insight = "You're completing tasks consistently. Great progress."

    # =====================================
    # SMART SCHEDULE
    # =====================================

    schedule = []

    if overdue_tasks:
        schedule.append("Complete overdue tasks first.")

    if due_today:
        schedule.append("Finish today's deadlines.")

    if high_priority_tasks:
        schedule.append("Work on High Priority tasks before Medium and Low.")

    if not overdue_tasks and not due_today:
        schedule.append("Use today for planning upcoming work.")

    # =====================================
    # BURNOUT WARNING
    # =====================================

    burnout = None

    pending = len(tasks) - completed_tasks

    if pending >= 20:

        burnout = "High"

    elif pending >= 10:

        burnout = "Medium"

    else:

        burnout = "Low"

    # =====================================
    # WEEKLY GOAL
    # =====================================

    weekly_goal = 10

    weekly_progress = completed_tasks

    weekly_percent = min(
        round((weekly_progress / weekly_goal) * 100),
        100
    )

    # =====================================
    # ACHIEVEMENTS
    # =====================================

    badges = []

    if completed_tasks >= 5:
        badges.append("🏅 Task Finisher")

    if productivity_score >= 90:
        badges.append("🚀 Productivity Master")

    if not overdue_tasks:
        badges.append("⏰ Deadline Keeper")

    if total_projects >= 5:
        badges.append("📁 Project Organizer")

    if total_tasks >= 20:
        badges.append("💼 Task Manager")

    return render_template(
        "dashboard/dashboard.html",
        total_projects=total_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        recent_projects=recent_projects,
        recent_tasks=recent_tasks,
        completed=completed,
        in_progress=in_progress,
        todo=todo,
        recent_activity=recent_activity,
        greeting=greeting,
        ai_suggestions=ai_suggestions,
        overdue_tasks=overdue_tasks,
        due_today=due_today,
        due_tomorrow=due_tomorrow,
        completed_task_list=completed_task_list,
        top_tasks=top_tasks,
        recommended_task=recommended_task,
        productivity_score=productivity_score,
        workload=workload,
        motivation=motivation,
        insight=insight,
        schedule=schedule,
        burnout=burnout,
        weekly_goal=weekly_goal,
        weekly_progress=weekly_progress,
        weekly_percent=weekly_percent,
        badges=badges,

    )