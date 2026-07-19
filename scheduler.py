from datetime import date

from models.task import Task
from email_utils import send_task_reminder


def send_due_task_reminders():

    print("=" * 50)
    print("Checking reminders...")

    tasks = Task.query.filter(
        Task.due_date <= date.today(),
        Task.status != "Completed",
    ).all()

    print(f"Found {len(tasks)} overdue/due task(s)")

    for task in tasks:

        print("=" * 40)
        print("Task:", task.title)
        print("Assigned_to ID:", task.assigned_to)
        print("Due Date:", task.due_date)
        print("Status:", task.status)

        if task.assignee:
            print("Team Member ID:", task.assignee.id)
            print("User:", task.assignee.user.full_name)
            print("Email:", task.assignee.user.email)
        else:
            print("No assignee found!")
            continue

        try:
            send_task_reminder(
                user_email=task.assignee.user.email,
                task_title=task.title,
                due_date=task.due_date.strftime("%d %b %Y")
            )

            print("✅ Email sent")

        except Exception as e:
            print("❌ Mail Error:", e)