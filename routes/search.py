from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import or_

from models.task import Task
from models.project import Project
from models.tag import Tag
from models.team_member import TeamMember

search = Blueprint("search", __name__)


@search.route("/search")
@login_required
def global_search():

    keyword = request.args.get("keyword", "")
    priority = request.args.get("priority", "")
    status = request.args.get("status", "")
    project_id = request.args.get("project", "")
    assignee = request.args.get("assignee", "")
    tag_id = request.args.get("tag", "")

    projects = Project.query.filter_by(
        owner_id=current_user.id
    ).all()

    members = TeamMember.query.all()

    tags = Tag.query.order_by(Tag.name).all()

    query = Task.query.filter_by(
        owner_id=current_user.id
    )

    # Keyword Search
    if keyword:

        query = query.filter(

            or_(

                Task.title.ilike(f"%{keyword}%"),

                Task.description.ilike(f"%{keyword}%")

            )

        )

    # Priority Filter
    if priority:

        query = query.filter_by(
            priority=priority
        )

    # Status Filter
    if status:

        query = query.filter_by(
            status=status
        )

    # Project Filter
    if project_id:

        query = query.filter_by(
            project_id=project_id
        )

    # Assignee Filter
    if assignee:

        query = query.filter_by(
            assigned_to=assignee
        )

    if tag_id:
        query = query.filter(
            Task.tags.any(Tag.id == int(tag_id))
        )

    tasks = query.order_by(
        Task.due_date.asc()
    ).all()

    return render_template(
        "search/search.html",

        tasks=tasks,
        projects=projects,
        members=members,
        tags=tags,

        keyword=keyword,
        priority=priority,
        status=status,
        project_id=project_id,
        assignee=assignee,
        tag_id=tag_id
    )