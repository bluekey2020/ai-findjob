import uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Date, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON

from app.core.database import Base


class Application(Base):
  __tablename__ = 'applications'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'))
  job_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('jobs.id'))

  company: Mapped[str | None] = mapped_column(String(200))
  role: Mapped[str | None] = mapped_column(String(200))
  status: Mapped[str] = mapped_column(String(30), default='wishlist')
  resume_version: Mapped[str | None] = mapped_column(String(100))
  cover_letter_version: Mapped[str | None] = mapped_column(String(100))
  applied_date: Mapped[date | None] = mapped_column(Date)
  last_contact_date: Mapped[date | None] = mapped_column(Date)
  next_step: Mapped[str | None] = mapped_column(Text)
  notes: Mapped[str | None] = mapped_column(Text)
  batch_number: Mapped[int | None] = mapped_column(Integer)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

  events: Mapped[list['ApplicationEvent']] = relationship(back_populates='application', cascade='all, delete-orphan')


class ApplicationEvent(Base):
  __tablename__ = 'application_events'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  application_id: Mapped[str] = mapped_column(String(36), ForeignKey('applications.id'), nullable=False)
  event_date: Mapped[date] = mapped_column(Date, nullable=False)
  event_type: Mapped[str | None] = mapped_column(String(50))
  detail: Mapped[str | None] = mapped_column(Text)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

  application: Mapped['Application'] = relationship(back_populates='events')
