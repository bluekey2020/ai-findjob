from datetime import date, datetime
from pydantic import BaseModel


class JobResponse(BaseModel):
  id: str
  title: str
  company: str | None = None
  location: str | None = None
  region: str | None = None
  salary_range: str | None = None
  platform: str | None = None
  url: str | None = None
  description: str | None = None
  requirements: list[str] = []
  source_type: str = 'official'
  posted_date: date | None = None
  found_date: date | None = None
  status: str = 'new'
  match_score: int = 0
  match_reasons: list[str] = []
  fraud_score: int = 0
  fraud_flags: list[str] = []
  dealbreaker_flags: list[str] = []
  tags: list[str] = []
  salary_estimate: dict = {}
  is_top_pick: bool = False
  created_at: datetime | None = None

  model_config = {'from_attributes': True}


class JobUpdate(BaseModel):
  status: str | None = None
  is_top_pick: bool | None = None
  notes: str | None = None
