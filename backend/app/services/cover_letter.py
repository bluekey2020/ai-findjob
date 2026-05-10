"""Cover letter generation service."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.llm import call_agent
from app.core.database import async_session
from app.models.profile import Profile
from app.models.job import Job
from app.models.company import Company
from app.prompts.cover_letter_writer import COVER_LETTER_SYSTEM, COVER_LETTER_OUTPUT_TOOL


async def _load_context(db: AsyncSession, user_id: str, job_id: str) -> dict | None:
  profile_result = await db.execute(
    select(Profile).where(Profile.user_id == user_id)
    .options(selectinload(Profile.skills), selectinload(Profile.work_experiences))
  )
  profile = profile_result.scalar_one_or_none()
  if not profile:
    return None

  job_result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user_id))
  job = job_result.scalar_one_or_none()
  if not job:
    return None

  company_result = await db.execute(
    select(Company).where(Company.user_id == user_id, Company.name == job.company)
  )
  company = company_result.scalar_one_or_none()

  return {
    'candidate_name': profile.name,
    'candidate_current_role': profile.current_role,
    'candidate_current_company': profile.current_company,
    'candidate_highlights': profile.highlights[:5] if profile.highlights else [],
    'candidate_summary': profile.summary,
    'job_title': job.title,
    'job_company': job.company,
    'job_description': job.description,
    'company_culture': company.culture_summary if company else '',
    'company_opportunities': company.opportunity_signals if company else [],
  }


async def generate_cover_letter(user_id: str, job_id: str) -> dict:
  """Generate a cover letter for a specific job application (Phase 3)."""
  async with async_session() as db:
    ctx = await _load_context(db, user_id, job_id)
    if not ctx:
      return {'error': 'Profile or job not found'}

  user_message = f"""Write a cover letter for this job application.

## Candidate Context
{json.dumps(ctx, indent=2, ensure_ascii=False)}

Generate both a full cover letter and a short cold outreach message.
"""
  result = await call_agent(
    agent_name='cover-letter-writer',
    system_prompt=COVER_LETTER_SYSTEM,
    user_message=user_message,
    tools=[COVER_LETTER_OUTPUT_TOOL],
    max_tokens=2048,
  )

  tool_output = result.get('tool_output')
  if not tool_output:
    return {'error': 'No structured output', 'raw_content': result.get('content')}

  return {
    'cover_letter': tool_output,
    'job_title': ctx['job_title'],
    'company': ctx['job_company'],
    'narrative_angles': tool_output.get('narrative_angles', []),
    'usage': result.get('usage'),
  }
