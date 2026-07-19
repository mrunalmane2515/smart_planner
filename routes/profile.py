from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

import os

from models import db
from models.user import User
from models.project import Project
from models.task import Task

profile = Blueprint("profile", __name__)


# =====================================
# Profile Page
# =====================================
@profile.route("/profile")
@login_required
def user_profile():

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

    completion_rate = 0

    if total_tasks > 0:
        completion_rate = int(
            (completed_tasks / total_tasks) * 100
        )

    return render_template(
        "profile/profile.html",
        total_projects=total_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        completion_rate=completion_rate
    )


# =====================================
# Edit Profile
# =====================================
@profile.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":

        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip()

        existing = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()

        if existing:

            flash(
                "Email already exists.",
                "danger"
            )

            return redirect(
                url_for("profile.edit_profile")
            )

        current_user.full_name = full_name
        current_user.email = email

        file = request.files.get("profile_image")

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "profile_pictures"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            file.save(
                os.path.join(
                    upload_folder,
                    filename
                )
            )

            current_user.profile_image = filename

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for("profile.user_profile")
        )

    return render_template(
        "profile/edit_profile.html"
    )