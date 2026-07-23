from flask_mail import Message
from flask import render_template
from extensions import mail
from flask import current_app

def send_task_reminder(user_email, task_title, due_date):

    msg = Message(
        subject="📌 Smart Planner - Task Reminder",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user_email]
    )

    msg.html = render_template(
        "emails/task_reminder.html",
        task_title=task_title,
        due_date=due_date,
        dashboard_url="http://127.0.0.1:5001/"
    )

    mail.send(msg)


def send_task_assigned_email(user_email, task_title, due_date):

    msg = Message(
        subject="📌 Smart Planner - Task Reminder",
        sender="yourgmail@gmail.com",
        recipients=[user_email]
    )

    msg.html = render_template(
        "emails/task_assigned.html",
        task_title=task_title,
        due_date=due_date,
        dashboard_url="http://127.0.0.1:5001/"
    )

    mail.send(msg)