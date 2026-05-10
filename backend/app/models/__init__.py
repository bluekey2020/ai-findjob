from app.core.database import Base

# Import all models so Alembic can discover them
from app.models.user import User
from app.models.profile import Profile, Skill, WorkExperience, Education, Project, Language, Certification
from app.models.preferences import Preferences
from app.models.job import Job
from app.models.company import Company
from app.models.application import Application, ApplicationEvent
from app.models.tracking import (
  DashboardSnapshot, FeedbackEvent, AgentWeight, FeedbackLog,
  AgentCheckpoint, ActivityLog
)

__all__ = [
  'Base', 'User',
  'Profile', 'Skill', 'WorkExperience', 'Education', 'Project', 'Language', 'Certification',
  'Preferences', 'Job', 'Company',
  'Application', 'ApplicationEvent',
  'DashboardSnapshot', 'FeedbackEvent', 'AgentWeight', 'FeedbackLog',
  'AgentCheckpoint', 'ActivityLog',
]
