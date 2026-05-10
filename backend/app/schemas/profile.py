from datetime import datetime
from pydantic import BaseModel


class SkillSchema(BaseModel):
  id: str | None = None
  name: str
  level: str | None = None
  years: float | None = None
  category: str | None = None
  sort_order: int = 0

  model_config = {'from_attributes': True}


class WorkExperienceSchema(BaseModel):
  id: str | None = None
  company: str | None = None
  title: str | None = None
  start_date: str | None = None
  end_date: str | None = None
  description: str | None = None
  highlights: list[str] = []
  tech_stack: list[str] = []
  role: str | None = None
  sort_order: int = 0

  model_config = {'from_attributes': True}


class EducationSchema(BaseModel):
  id: str | None = None
  school: str | None = None
  degree: str | None = None
  field: str | None = None
  graduation: str | None = None
  gpa: str | None = None
  honors: list[str] = []
  sort_order: int = 0

  model_config = {'from_attributes': True}


class ProjectSchema(BaseModel):
  id: str | None = None
  name: str | None = None
  description: str | None = None
  url: str | None = None
  highlights: list[str] = []
  role: str | None = None
  tech_stack: list[str] = []
  duration: str | None = None
  sort_order: int = 0

  model_config = {'from_attributes': True}


class LanguageSchema(BaseModel):
  id: str | None = None
  name: str | None = None
  proficiency: str | None = None

  model_config = {'from_attributes': True}


class CertificationSchema(BaseModel):
  id: str | None = None
  name: str | None = None

  model_config = {'from_attributes': True}


class ProfileResponse(BaseModel):
  id: str
  user_id: str
  name: str | None = None
  email: str | None = None
  phone: str | None = None
  location: str | None = None
  city: str | None = None
  country: str | None = None
  years_of_experience: int | None = None
  current_role: str | None = None
  current_company: str | None = None
  summary: str | None = None
  highlights: list[str] = []
  gaps: list[str] = []
  target_roles: list[str] = []
  skills: list[SkillSchema] = []
  work_experiences: list[WorkExperienceSchema] = []
  education: list[EducationSchema] = []
  projects: list[ProjectSchema] = []
  languages: list[LanguageSchema] = []
  certifications: list[CertificationSchema] = []
  created_at: datetime | None = None
  updated_at: datetime | None = None

  model_config = {'from_attributes': True}


class ProfileUpdate(BaseModel):
  name: str | None = None
  email: str | None = None
  phone: str | None = None
  location: str | None = None
  city: str | None = None
  country: str | None = None
  years_of_experience: int | None = None
  current_role: str | None = None
  current_company: str | None = None
  summary: str | None = None
  highlights: list[str] | None = None
  gaps: list[str] | None = None
  target_roles: list[str] | None = None
  skills: list[SkillSchema] | None = None
  work_experiences: list[WorkExperienceSchema] | None = None
  education: list[EducationSchema] | None = None
  projects: list[ProjectSchema] | None = None
  languages: list[LanguageSchema] | None = None
  certifications: list[CertificationSchema] | None = None
