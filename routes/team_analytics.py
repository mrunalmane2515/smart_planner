from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.project import Project
from models.team_member import TeamMember

team_analytics = Blueprint(
    "team_analytics",
    __name__
)


@team_analytics.route("/projects/<int:project_id>/team-analytics")
@login_required
def dashboard(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    members = TeamMember.query.filter_by(
        project_id=project.id
    ).all()

    stats = []

    for member in members:

        assigned = len(member.tasks)

        completed = sum(
            1
            for t in member.tasks
            if t.status == "Completed"
        )

        pending = assigned - completed

        completion = round(
            (completed / assigned) * 100,
            1
        ) if assigned else 0

        stats.append({
            "member": member,
            "assigned": assigned,
            "completed": completed,
            "pending": pending,
            "completion": completion
        })

    # ----------- Move these OUTSIDE the loop -----------

    member_names = [
        item["member"].user.full_name
        for item in stats
    ]

    assigned_counts = [
        item["assigned"]
        for item in stats
    ]

    completed_counts = [
        item["completed"]
        for item in stats
    ]

    pending_counts = [
        item["pending"]
        for item in stats
    ]

    top_member = max(
        stats,
        key=lambda x: x["completed"]
    ) if stats else None

    return render_template(
        "team/team_analytics.html",
        project=project,
        stats=stats,
        member_names=member_names,
        assigned_counts=assigned_counts,
        completed_counts=completed_counts,
        pending_counts=pending_counts,
        top_member=top_member
    )