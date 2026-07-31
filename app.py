from email.message import Message

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_login import current_user
from flask import Flask
from config import Config
from models import db
from models.user import User
from models.project import Project
from models.task import Task
from models.comment import Comment
from models.tag import Tag
from models.attachment import Attachment
from models.team_member import TeamMember
from models.activity import Activity
from models.notification import Notification
from routes.auth import auth
from routes.dashboard import dashboard
from routes.project import project
from routes.project_dashboard import project_dashboard
from routes.activity import activity
from routes.timeline import timeline
from routes.settings import settings
from routes.pdf_report import pdf_report
from routes.search import search
from routes.task import task
from routes.team import team
from routes.profile import profile
from routes.team_analytics import team_analytics
from routes.analytics import analytics
from routes.calendar import calendar
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler import send_due_task_reminders
from flask import session, request
from routes.notification import notification
from routes.export import export
from routes.attachment import attachment
from extensions import mail



app = Flask(__name__)
app.config.from_object(Config)
print("DATABASE_URL:", app.config["SQLALCHEMY_DATABASE_URI"])
print("SECRET_KEY loaded:", app.config["SECRET_KEY"] is not None)
mail.init_app(app)

app.register_blueprint(project)
db.init_app(app)
app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(task)
app.register_blueprint(profile)
app.register_blueprint(calendar)
app.register_blueprint(activity)
app.register_blueprint(team)
app.register_blueprint(analytics)
app.register_blueprint(notification)
app.register_blueprint(team_analytics)
app.register_blueprint(project_dashboard)
app.register_blueprint(timeline)
app.register_blueprint(search)
app.register_blueprint(settings)
app.register_blueprint(export)
app.register_blueprint(pdf_report)
app.register_blueprint(attachment)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth.login"
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    print("Tag Count:", Tag.query.count())


@app.route("/")
def home():
    return redirect(url_for("dashboard.home"))


@app.route("/toggle-theme")
def toggle_theme():

    current = session.get("theme", "light")

    if current == "light":
        session["theme"] = "dark"
    else:
        session["theme"] = "light"

    return redirect(request.referrer or "/")

@app.context_processor
def inject_notification_count():

    if current_user.is_authenticated:

        unread_count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()

    else:

        unread_count = 0

    return dict(
        unread_count=unread_count
    )

if __name__ == "__main__":
    scheduler = BackgroundScheduler()

    def scheduled_reminders():
        with app.app_context():
            send_due_task_reminders()

    scheduler.add_job(
        scheduled_reminders,
        trigger="interval",
        minutes=60
    )

    scheduler.start()

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
