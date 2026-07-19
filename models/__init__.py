from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models AFTER db is created
from models.user import User
from models.project import Project
from models.task import Task
from models.activity import Activity
from models.team_member import TeamMember
from models.notification import Notification