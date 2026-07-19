from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import request, redirect, url_for, flash
from models import db
from models.project import Project
from models.team_member import TeamMember
from models.user import User
from models.notification import Notification

team = Blueprint("team", __name__)


# ==============================
# Manage Team
# ==============================
@team.route("/projects/<int:project_id>/team")
@login_required
def manage_team(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    members = TeamMember.query.filter_by(
        project_id=project.id
    ).all()

    return render_template(
        "team/manage_team.html",
        project=project,
        members=members
    )

@team.route("/projects/<int:project_id>/team/add", methods=["GET", "POST"])
@login_required
def add_member(project_id):

    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        email = request.form["email"]
        role = request.form["role"]

        # Find existing user
        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                "No registered user found with this email.",
                "danger"
            )

            return redirect(
                url_for(
                    "team.add_member",
                    project_id=project.id
                )
            )

        # Check duplicate member
        existing = TeamMember.query.filter_by(
            project_id=project.id,
            user_id=user.id
        ).first()

        if existing:

            flash(
                "User is already a team member.",
                "warning"
            )

            return redirect(
                url_for(
                    "team.manage_team",
                    project_id=project.id
                )
            )

        member = TeamMember(
            project_id=project.id,
            user_id=user.id,
            role=role
        )

        db.session.add(member)
        db.session.commit()

        # Notification for project owner
        notification = Notification(
            user_id=current_user.id,
            message=f'{user.full_name} joined project "{project.name}" as {role}.'
        )

        db.session.add(notification)
        db.session.commit()

        flash(
            "Team member added successfully!",
            "success"
        )

        return redirect(
            url_for(
                "team.manage_team",
                project_id=project.id
            )
        )

    return render_template(
        "team/add_member.html",
        project=project
    )

@team.route("/team/edit/<int:member_id>", methods=["GET", "POST"])
@login_required
def edit_member(member_id):

    member = TeamMember.query.get_or_404(member_id)

    # Security check
    if member.project.owner_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("project.projects"))

    if request.method == "POST":

        member.role = request.form["role"]

        db.session.commit()

        flash(
            "Team member updated successfully!",
            "success"
        )

        return redirect(
            url_for(
                "team.manage_team",
                project_id=member.project_id
            )
        )

    return render_template(
        "team/edit_member.html",
        member=member
    )

@team.route("/team/delete/<int:member_id>")
@login_required
def delete_member(member_id):

    member = TeamMember.query.get_or_404(member_id)

    # Security check
    if member.project.owner_id != current_user.id:

        flash(
            "Access denied.",
            "danger"
        )

        return redirect(
            url_for("project.projects")
        )

    project_id = member.project_id

    db.session.delete(member)
    db.session.commit()

    flash(
        "Team member removed successfully!",
        "success"
    )

    return redirect(
        url_for(
            "team.manage_team",
            project_id=project_id
        )
    )