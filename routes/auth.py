import flash
from flask import Blueprint, render_template, request, redirect, url_for, url_for

from werkzeug.security import generate_password_hash

from models import db
from models.user import User
from werkzeug.security import check_password_hash

from flask_login import login_user
from flask_login import logout_user
from flask_login import login_user, logout_user, login_required

auth = Blueprint("auth", __name__)



@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name")

        email = request.form.get("email")

        password = request.form.get("password")

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            flash(
                "An account with this email already exists. Please log in.",
                "warning"
            )

            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            full_name=full_name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)

        db.session.commit()

        return render_template("auth/register.html")

    return render_template("auth/register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            return redirect(url_for("dashboard.home"))

        return "Invalid Email or Password"

    return render_template("auth/login.html")

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return render_template("auth/login.html")