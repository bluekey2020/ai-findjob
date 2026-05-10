import uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Text, Date, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON

from app.core.database import Base


class Job(Base):
  __tablename__ = 'jobs'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'))

  title: Mapped[str] = mapped_column(String(300), nullable=False)
  company: Mapped[str | None] = mapped_column(String(200))
  location: Mapped[str | None] = mapped_column(String(200))
  region: Mapped[str | None] = mapped_column(String(100))
  salary_range: Mapped[str | None] = mapped_column(String(100))
  platform: Mapped[str | None] = mapped_column(String(100))
  url: Mapped[str | None] = mapped_column(String(1000))
  description: Mapped[str | None] = mapped_column(Text)
  requirements: Mapped[dict | None] = mapped_column(JSON, default=list)
  source_type: Mapped[str] = mapped_column(String(50), default='official')
  posted_date: Mapped[date | None] = mapped_column(Date)
  found_date: Mapped[date] = mapped_column(Date, default=func.current_date())
  status: Mapped[str] = mapped_column(String(50), default='new')
  match_score: Mapped[int] = mapped_column(Integer, default=0)
  match_reasons: Mapped[dict | None] = mapped_column(JSON, default=list)
  fraud_score: Mapped[int] = mapped_column(Integer, default=0)
  fraud_flags: Mapped[dict | None] = mapped_column(JSON, default=list)
  dealbreaker_flags: Mapped[dict | None] = mapped_column(JSON, default=list)
  tags: Mapped[dict | None] = mapped_column(JSON, default=list)
  salary_estimate: Mapped[dict | None] = mapped_column(JSON, default=dict)
  is_top_pick: Mapped[bool] = mapped_column(Boolean, default=False)
  raw_jd: Mapped[dict | None] = mapped_column(JSON, default=dict)
  duplicate_of: Mapped[str | None] = mapped_column(String(36), ForeignKey('jobs.id'))
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
