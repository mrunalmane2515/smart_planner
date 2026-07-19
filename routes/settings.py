from flask import Blueprint, render_template
from flask_login import login_required

from flask import request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash

from models import db
from models.user import User
from flask_login import current_user

settings = Blueprint("settings", __name__)


@settings.route("/settings")
@login_required
def settings_page():
    return render_template("settings/settings.html")

@settings.route("/settings/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if not check_password_hash(
                current_user.password,
                current_password
        ):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("settings.change_password"))

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("settings.change_password"))

        current_user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("Password changed successfully.", "success")

        return redirect(url_for("settings.settings_page"))

    return render_template("settings/change_password.html")