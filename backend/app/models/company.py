import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON

from app.core.database import Base


class Company(Base):
  __tablename__ = 'companies'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'))

  name: Mapped[str] = mapped_column(String(200), nullable=False)
  industry: Mapped[str | None] = mapped_column(String(200))
  size: Mapped[str | None] = mapped_column(String(100))
  location: Mapped[str | None] = mapped_column(String(200))
  website: Mapped[str | None] = mapped_column(String(500))
  tech_stack: Mapped[dict | None] = mapped_column(JSON, default=list)
  culture_summary: Mapped[str | None] = mapped_column(Text)
  financial_health: Mapped[str] = mapped_column(String(20), default='unknown')
  risk_signals: Mapped[dict | None] = mapped_column(JSON, default=list)
  opportunity_signals: Mapped[dict | None] = mapped_column(JSON, default=list)
  key_contacts: Mapped[dict | None] = mapped_column(JSON, default=list)
  notes: Mapped[str | None] = mapped_column(Text)
  research_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
