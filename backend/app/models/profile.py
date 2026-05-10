import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON

from app.core.database import Base


class Profile(Base):
  __tablename__ = 'profiles'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id'), unique=True, nullable=False)

  name: Mapped[str | None] = mapped_column(String(100))
  email: Mapped[str | None] = mapped_column(String(255))
  phone: Mapped[str | None] = mapped_column(String(50))
  location: Mapped[str | None] = mapped_column(String(100))
  city: Mapped[str | None] = mapped_column(String(100))
  country: Mapped[str | None] = mapped_column(String(100))
  years_of_experience: Mapped[int | None] = mapped_column(Integer)
  current_role: Mapped[str | None] = mapped_column(String(200))
  current_company: Mapped[str | None] = mapped_column(String(200))
  summary: Mapped[str | None] = mapped_column(Text)
  highlights: Mapped[dict | None] = mapped_column(JSON, default=list)
  gaps: Mapped[dict | None] = mapped_column(JSON, default=list)
  target_roles: Mapped[dict | None] = mapped_column(JSON, default=list)
  metadata_: Mapped[dict | None] = mapped_column('metadata', JSON, default=dict)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

  user: Mapped['User'] = relationship(back_populates='profile')
  skills: Mapped[list['Skill']] = relationship(back_populates='profile', cascade='all, delete-orphan')
  work_experiences: Mapped[list['WorkExperience']] = relationship(back_populates='profile', cascade='all, delete-orphan')
  education: Mapped[list['Education']] = relationship(back_populates='profile', cascade='all, delete-orphan')
  projects: Mapped[list['Project']] = relationship(back_populates='profile', cascade='all, delete-orphan')
  languages: Mapped[list['Language']] = relationship(back_populates='profile', cascade='all, delete-orphan')
  certifications: Mapped[list['Certification']] = relationship(back_populates='profile', cascade='all, delete-orphan')


class Skill(Base):
  __tablename__ = 'skills'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  profile_id: Mapped[str] = mapped_column(String(36), ForeignKey('profiles.id'), nullable=False)
  name: Mapped[str] = mapped_column(String(100), nullable=False)
  level: Mapped[str | None] = mapped_column(String(50))
  years: Mapped[float | None] = mapped_column(Float)
  category: Mapped[str | None] = mapped_column(String(100))
  sort_order: Mapped[int] = mapped_column(Integer, default=0)

  profile: Mapped['Profile'] = relationship(back_populates='skills')


class WorkExperience(Base):
  __tablename__ = 'work_experiences'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  profile_id: Mapped[str] = mapped_column(String(36), ForeignKey('profiles.id'), nullable=False)
  company: Mapped[str | None] = mapped_column(String(200))
  title: Mapped[str | None] = mapped_column(String(200))
  start_date: Mapped[str | None] = mapped_column(String(10))
  end_date: Mapped[str | None] = mapped_column(String(10))
  description: Mapped[str | None] = mapped_column(Text)
  highlights: Mapped[dict | None] = mapped_column(JSON, default=list)
  tech_stack: Mapped[dict | None] = mapped_column(JSON, default=list)
  role: Mapped[str | None] = mapped_column(String(200))
  sort_order: Mapped[int] = mapped_column(Integer, default=0)

  profile: Mapped['Profile'] = relationship(back_populates='work_experiences')


class Education(Base):
  __tablename__ = 'education'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  profile_id: Mapped[str] = mapped_column(String(36), ForeignKey('profiles.id'), nullable=False)
  school: Mapped[str | None] = mapped_column(String(200))
  degree: Mapped[str | None] = mapped_column(String(200))
  field: Mapped[str | None] = mapped_column(String(200))
  graduation: Mapped[str | None] = mapped_column(String(10))
  gpa: Mapped[str | None] = mapped_column(String(20))
  honors: Mapped[dict | None] = mapped_column(JSON, default=list)
  sort_order: Mapped[int] = mapped_column(Integer, default=0)

  profile: Mapped['Profile'] = relationship(back_populates='education')


class Project(Base):
  __tablename__ = 'projects'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  profile_id: Mapped[str] = mapped_column(String(36), ForeignKey('profiles.id'), nullable=False)
  name: Mapped[str | None] = mapped_column(String(300))
  description: Mapped[str | None] = mapped_column(Text)
  url: Mapped[str | None] = mapped_column(String(500))
  highlights: Mapped[dict | None] = mapped_column(JSON, default=list)
  role: Mapped[str | None] = mapped_column(String(200))
  tech_stack: Mapped[dict | None] = mapped_column(JSON, default=list)
  duration: Mapped[str | None] = mapped_column(String(100))
  sort_order: Mapped[int] = mapped_column(Integer, default=0)

  profile: Mapped['Profile'] = relationship(back_populates='projects')


class Language(Base):
  __tablename__ = 'languages'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  profile_id: Mapped[str] = mapped_column(String(36), ForeignKey('profiles.id'), nullable=False)
  name: Mapped[str | None] = mapped_column(String(50))
  proficiency: Mapped[str | None] = mapped_column(String(50))

  profile: Mapped['Profile'] = relationship(back_populates='languages')


class Certification(Base):
  __tablename__ = 'certifications'

  id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
  profile_id: Mapped[str] = mapped_column(String(36), ForeignKey('profiles.id'), nullable=False)
  name: Mapped[str | None] = mapped_column(String(200))

  profile: Mapped['Profile'] = relationship(back_populates='certifications')
