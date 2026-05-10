import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON

from app.core.database import Base


class Preferences(Base):
  __tablename__ = 'preferences'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id'), unique=True, nullable=False)

  language: Mapped[str] = mapped_column(String(10), default='zh-CN')
  target_roles: Mapped[dict | None] = mapped_column(JSON, default=list)
  target_regions: Mapped[dict | None] = mapped_column(JSON, default=list)
  salary_amount: Mapped[int | None] = mapped_column(Integer)
  salary_currency: Mapped[str] = mapped_column(String(10), default='CNY')
  salary_period: Mapped[str] = mapped_column(String(10), default='monthly')
  city_preference: Mapped[str | None] = mapped_column(String(100))
  willing_to_relocate: Mapped[bool] = mapped_column(Boolean, default=False)
  visa_status: Mapped[str | None] = mapped_column(String(100))
  company_size_preference: Mapped[str] = mapped_column(String(20), default='any')
  overtime_tolerance: Mapped[str] = mapped_column(String(10), default='some')
  notice_period_days: Mapped[int] = mapped_column(Integer, default=30)
  dealbreakers: Mapped[dict | None] = mapped_column(JSON, default=list)
  job_freshness_days: Mapped[int] = mapped_column(Integer, default=14)
  preferred_platforms: Mapped[dict | None] = mapped_column(JSON, default=list)
  dream_companies: Mapped[dict | None] = mapped_column(JSON, default=list)
  timeline: Mapped[str | None] = mapped_column(String(100))
  inferential_fields: Mapped[dict | None] = mapped_column(JSON, default=dict)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

  user: Mapped['User'] = relationship(back_populates='preferences')
