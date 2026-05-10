from datetime import datetime
from pydantic import BaseModel


class SalaryExpectation(BaseModel):
  amount: int | None = None
  currency: str = 'CNY'
  period: str = 'monthly'


class PreferencesResponse(BaseModel):
  id: str
  user_id: str
  language: str = 'zh-CN'
  target_roles: list[str] = []
  target_regions: list[str] = []
  salary_amount: int | None = None
  salary_currency: str = 'CNY'
  salary_period: str = 'monthly'
  city_preference: str | None = None
  willing_to_relocate: bool = False
  visa_status: str | None = None
  company_size_preference: str = 'any'
  overtime_tolerance: str = 'some'
  notice_period_days: int = 30
  dealbreakers: list[str] = []
  job_freshness_days: int = 14
  preferred_platforms: list[str] = []
  dream_companies: list[str] = []
  timeline: str | None = None
  created_at: datetime | None = None
  updated_at: datetime | None = None

  model_config = {'from_attributes': True}


class PreferencesUpdate(BaseModel):
  language: str | None = None
  target_roles: list[str] | None = None
  target_regions: list[str] | None = None
  salary_amount: int | None = None
  salary_currency: str | None = None
  salary_period: str | None = None
  city_preference: str | None = None
  willing_to_relocate: bool | None = None
  visa_status: str | None = None
  company_size_preference: str | None = None
  overtime_tolerance: str | None = None
  notice_period_days: int | None = None
  dealbreakers: list[str] | None = None
  job_freshness_days: int | None = None
  preferred_platforms: list[str] | None = None
  dream_companies: list[str] | None = None
  timeline: str | None = None
