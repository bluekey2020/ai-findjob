import uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON

from app.core.database import Base


class DashboardSnapshot(Base):
  __tablename__ = 'dashboard_snapshots'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'))
  current_phase: Mapped[int] = mapped_column(Integer, default=0)
  days_active: Mapped[int] = mapped_column(Integer, default=0)
  avg_match_score: Mapped[float] = mapped_column(Float, default=0)
  funnel_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
  timeline: Mapped[dict | None] = mapped_column(JSON, default=list)
  recent_activity: Mapped[dict | None] = mapped_column(JSON, default=list)
  xp_total: Mapped[int] = mapped_column(Integer, default=0)
  achievements: Mapped[dict | None] = mapped_column(JSON, default=list)
  snapshot_date: Mapped[date] = mapped_column(Date, default=func.current_date())
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class FeedbackEvent(Base):
  __tablename__ = 'feedback_events'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'))
  event_type: Mapped[str | None] = mapped_column(String(50))
  phase: Mapped[int | None] = mapped_column(Integer)
  source_company: Mapped[str | None] = mapped_column(String(200))
  source_role: Mapped[str | None] = mapped_column(String(200))
  reason: Mapped[str | None] = mapped_column(String)
  lessons: Mapped[dict | None] = mapped_column(JSON, default=list)
  updates_triggered: Mapped[dict | None] = mapped_column(JSON, default=list)
  status: Mapped[str] = mapped_column(String(20), default='pending')
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AgentWeight(Base):
  __tablename__ = 'agent_weights'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'))
  agent_name: Mapped[str | None] = mapped_column(String(100))
  preference_vector: Mapped[dict | None] = mapped_column(JSON, default=dict)
  learning_rate: Mapped[float] = mapped_column(Float, default=0.1)
  total_feedback_received: Mapped[int] = mapped_column(Integer, default=0)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class FeedbackLog(Base):
  __tablename__ = 'feedback_log'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'))
  agent_name: Mapped[str | None] = mapped_column(String(100))
  feedback_type: Mapped[str | None] = mapped_column(String(20))
  signal: Mapped[str | None] = mapped_column(String)
  old_behavior: Mapped[str | None] = mapped_column(String)
  new_behavior: Mapped[str | None] = mapped_column(String)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AgentCheckpoint(Base):
  __tablename__ = 'agent_checkpoints'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'))
  agent_name: Mapped[str | None] = mapped_column(String(100))
  last_run: Mapped[datetime | None] = mapped_column(DateTime)
  status: Mapped[str | None] = mapped_column(String(50))
  input_hash: Mapped[str | None] = mapped_column(String(128))
  output_summary: Mapped[str | None] = mapped_column(String)
  next_trigger: Mapped[str | None] = mapped_column(String(200))
  snapshot_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ActivityLog(Base):
  __tablename__ = 'activity_log'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'))
  activity_date: Mapped[date] = mapped_column(Date, nullable=False)
  phase: Mapped[int | None] = mapped_column(Integer)
  activities: Mapped[dict | None] = mapped_column(JSON, default=list)
  jobs_discovered: Mapped[int] = mapped_column(Integer, default=0)
  applications_sent: Mapped[int] = mapped_column(Integer, default=0)
  interviews: Mapped[int] = mapped_column(Integer, default=0)
  key_decisions: Mapped[dict | None] = mapped_column(JSON, default=list)
  mood: Mapped[str | None] = mapped_column(String(20))
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
