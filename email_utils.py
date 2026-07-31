from flask_mail import Message
from flask import render_template, current_app
from extensions import mail

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
        dashboard_url="https://smart-planner-x43e.onrender.com/"
    )

    try:
        mail.send(msg)
        print("✅ Email sent successfully")
    except Exception as e:
        print(f"❌ Email failed: {e}")
