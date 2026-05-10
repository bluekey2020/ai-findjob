"""Seed database with demo data from existing docs/data/*.json files."""
import asyncio
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.core.database import async_session, init_db, Base, engine
from app.core.security import hash_password
from app.models.user import User
from app.models.profile import Profile, Skill, WorkExperience, Education, Project, Language
from app.models.preferences import Preferences
from app.models.job import Job
from app.models.company import Company
from app.models.tracking import DashboardSnapshot

DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'docs' / 'data'


def _parse_date(val):
  if val and isinstance(val, str):
    try:
      return date.fromisoformat(val)
    except ValueError:
      return None
  return val


def load_json(name: str) -> dict:
  path = DATA_DIR / f'{name}.json'
  if path.exists():
    return json.loads(path.read_text(encoding='utf-8'))
  return {}


async def seed():
  await init_db()

  async with async_session() as db:
    existing = await db.execute(select(User).where(User.email == 'demo@aijob.com'))
    if existing.scalar_one_or_none():
      print('Seed data already exists, skipping.')
      return

    # Create demo user
    user = User(
      email='demo@aijob.com',
      password_hash=hash_password('demo123'),
      display_name='张三'
    )
    db.add(user)
    await db.flush()

    print(f'Created user: {user.id}')

    # Profile from docs/data/profile.json
    profile_data = load_json('profile')
    basics = profile_data.get('basics', {})
    profile = Profile(
      user_id=user.id,
      name=basics.get('name', ''),
      email=basics.get('email', ''),
      phone=basics.get('phone', ''),
      location=basics.get('location', ''),
      city=basics.get('city', ''),
      country=basics.get('country', ''),
      years_of_experience=basics.get('years_of_experience'),
      current_role=basics.get('current_role', ''),
      current_company=basics.get('current_company', ''),
      summary=profile_data.get('summary', ''),
      highlights=profile_data.get('highlights', []),
      gaps=profile_data.get('gaps', []),
      target_roles=profile_data.get('target_roles', []),
    )
    db.add(profile)
    await db.flush()

    # Skills
    for i, s in enumerate(profile_data.get('skills', [])):
      db.add(Skill(profile_id=profile.id, name=s['name'], level=s.get('level', ''),
                    years=s.get('years'), category=s.get('category', ''), sort_order=i))

    # Work experiences
    for i, exp in enumerate(profile_data.get('work_experience', [])):
      db.add(WorkExperience(
        profile_id=profile.id, company=exp.get('company', ''),
        title=exp.get('title', ''), start_date=exp.get('start_date', ''),
        end_date=exp.get('end_date', ''), description=exp.get('description', ''),
        highlights=exp.get('highlights', []), tech_stack=exp.get('tech_stack', []),
        role=exp.get('role', ''), sort_order=i
      ))

    # Education
    for i, edu in enumerate(profile_data.get('education', [])):
      db.add(Education(
        profile_id=profile.id, school=edu.get('school', ''),
        degree=edu.get('degree', ''), field=edu.get('field', ''),
        graduation=edu.get('graduation', ''), gpa=edu.get('gpa', ''),
        honors=edu.get('honors', []), sort_order=i
      ))

    # Projects
    for i, proj in enumerate(profile_data.get('projects', [])):
      db.add(Project(
        profile_id=profile.id, name=proj.get('name', ''),
        description=proj.get('description', ''), url=proj.get('url', ''),
        highlights=proj.get('highlights', []), role=proj.get('role', ''),
        tech_stack=proj.get('tech_stack', []), duration=proj.get('duration', ''),
        sort_order=i
      ))

    # Languages
    for lang in profile_data.get('languages', []):
      db.add(Language(profile_id=profile.id, name=lang.get('name', ''),
                       proficiency=lang.get('proficiency', '')))

    print(f'Created profile with {len(profile_data.get("skills", []))} skills')

    # Preferences
    prefs_data = load_json('preferences')
    prefs = Preferences(
      user_id=user.id,
      language=prefs_data.get('language', 'zh-CN'),
      target_roles=prefs_data.get('target_roles', []),
      target_regions=prefs_data.get('target_regions', []),
      salary_amount=prefs_data.get('salary_expectation', {}).get('amount'),
      salary_currency=prefs_data.get('salary_expectation', {}).get('currency', 'CNY'),
      salary_period=prefs_data.get('salary_expectation', {}).get('period', 'monthly'),
      city_preference=prefs_data.get('city_preference', ''),
      willing_to_relocate=prefs_data.get('willing_to_relocate', False),
      company_size_preference=prefs_data.get('company_size_preference', 'any'),
      overtime_tolerance=prefs_data.get('overtime_tolerance', 'some'),
      notice_period_days=prefs_data.get('notice_period_days', 30),
      dealbreakers=prefs_data.get('dealbreakers', []),
      job_freshness_days=prefs_data.get('job_freshness_days', 14),
      preferred_platforms=prefs_data.get('preferred_platforms', []),
      dream_companies=prefs_data.get('dream_companies', []),
    )
    db.add(prefs)

    # Jobs
    jobs_data = load_json('jobs')
    for job_entry in jobs_data.get('jobs', [])[:20]:  # first 20
      db.add(Job(
        user_id=user.id,
        title=job_entry.get('title', ''),
        company=job_entry.get('company', ''),
        location=job_entry.get('location', ''),
        region=job_entry.get('region', ''),
        salary_range=job_entry.get('salary_range', ''),
        platform=job_entry.get('platform', ''),
        url=job_entry.get('url', ''),
        description=job_entry.get('description', ''),
        source_type=job_entry.get('source_type', 'official'),
        posted_date=_parse_date(job_entry.get('posted_date')),
        found_date=_parse_date(job_entry.get('found_date')),
        match_score=job_entry.get('match_score', 0),
        match_reasons=job_entry.get('match_reasons', []),
        fraud_score=job_entry.get('fraud_score', 0),
        dealbreaker_flags=job_entry.get('dealbreaker_flags', []),
        is_top_pick=job_entry.get('id') in (jobs_data.get('top_picks', [])),
      ))

    print(f'Created {min(20, len(jobs_data.get("jobs", [])))} jobs')

    # Companies
    companies_data = load_json('companies')
    for comp in companies_data.get('companies', []):
      db.add(Company(
        user_id=user.id,
        name=comp.get('name', ''),
        industry=comp.get('industry', ''),
        size=comp.get('size', ''),
        location=comp.get('location', ''),
        tech_stack=comp.get('tech_stack', []),
        culture_summary=comp.get('culture_summary', ''),
        financial_health=comp.get('financial_health', 'unknown'),
        risk_signals=comp.get('risk_signals', []),
        opportunity_signals=comp.get('opportunity_signals', []),
        research_data=comp.get('notes', {}),
      ))

    print(f'Created {len(companies_data.get("companies", []))} companies')

    # Dashboard
    dashboard_data = load_json('dashboard')
    db.add(DashboardSnapshot(
      user_id=user.id,
      current_phase=0,
      days_active=0,
      avg_match_score=0,
      funnel_data=dashboard_data.get('funnel', {}),
    ))

    await db.commit()
    print('Seed complete! Demo login: demo@aijob.com / demo123')


if __name__ == '__main__':
  asyncio.run(seed())
