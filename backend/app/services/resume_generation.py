"""Resume generation service — default and JD-tailored resume creation."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.llm import call_agent
from app.core.database import async_session
from app.models.profile import Profile, Skill, WorkExperience, Education, Project
from app.models.job import Job
from app.models.tracking import ActivityLog
from app.prompts.resume_architect import RESUME_DEFAULT_SYSTEM, RESUME_TAILOR_SYSTEM, RESUME_OUTPUT_TOOL


async def _load_profile_for_prompt(db: AsyncSession, user_id: str) -> dict | None:
  result = await db.execute(
    select(Profile)
    .where(Profile.user_id == user_id)
    .options(
      selectinload(Profile.skills),
      selectinload(Profile.work_experiences),
      selectinload(Profile.education),
      selectinload(Profile.projects),
    )
  )
  profile = result.scalar_one_or_none()
  if not profile:
    return None

  return {
    'name': profile.name,
    'email': profile.email,
    'phone': profile.phone,
    'location': profile.location,
    'current_role': profile.current_role,
    'current_company': profile.current_company,
    'years_of_experience': profile.years_of_experience,
    'summary': profile.summary,
    'highlights': profile.highlights,
    'skills': [{'name': s.name, 'level': s.level, 'years': s.years, 'category': s.category}
               for s in (profile.skills or [])],
    'work_experience': [{
      'company': w.company, 'title': w.title,
      'start_date': w.start_date, 'end_date': w.end_date,
      'description': w.description, 'highlights': w.highlights,
      'tech_stack': w.tech_stack, 'role': w.role,
    } for w in (profile.work_experiences or [])],
    'education': [{'school': e.school, 'degree': e.degree, 'field': e.field,
                    'graduation': e.graduation} for e in (profile.education or [])],
    'projects': [{'name': p.name, 'description': p.description, 'url': p.url,
                   'tech_stack': p.tech_stack, 'highlights': p.highlights}
                  for p in (profile.projects or [])],
  }


async def generate_default_resume(user_id: str) -> dict:
  """Generate default resume from user profile (Phase 1)."""
  async with async_session() as db:
    profile_data = await _load_profile_for_prompt(db, user_id)
    if not profile_data:
      return {'error': 'Profile not found — run profile analysis first'}

  result = await call_agent(
    agent_name='resume-architect',
    system_prompt=RESUME_DEFAULT_SYSTEM,
    user_message=f'Generate a default resume for this profile:\n\n{json.dumps(profile_data, indent=2, ensure_ascii=False)}',
    tools=[RESUME_OUTPUT_TOOL],
    max_tokens=4096,
  )

  tool_output = result.get('tool_output')
  if not tool_output:
    return {'error': 'No structured output', 'raw_content': result.get('content')}

  return {
    'resume': tool_output,
    'usage': result.get('usage'),
  }


async def generate_tailored_resume(user_id: str, job_id: str) -> dict:
  """Generate a resume tailored to a specific job description (Phase 3)."""
  async with async_session() as db:
    profile_data = await _load_profile_for_prompt(db, user_id)
    if not profile_data:
      return {'error': 'Profile not found'}

    job_result = await db.execute(select(Job).where(Job.id == job_id, Job.user_id == user_id))
    job = job_result.scalar_one_or_none()
    if not job:
      return {'error': 'Job not found'}

  user_message = f"""Tailor a resume for this specific job.

## Job Description
**Title:** {job.title}
**Company:** {job.company}
**Location:** {job.location}
**Description:** {job.description}
**Requirements:** {json.dumps(job.requirements, ensure_ascii=False)}

## Candidate Profile
{json.dumps(profile_data, indent=2, ensure_ascii=False)}
"""

  result = await call_agent(
    agent_name='resume-architect',
    system_prompt=RESUME_TAILOR_SYSTEM,
    user_message=user_message,
    tools=[RESUME_OUTPUT_TOOL],
    max_tokens=4096,
  )

  tool_output = result.get('tool_output')
  if not tool_output:
    return {'error': 'No structured output', 'raw_content': result.get('content')}

  return {
    'resume': tool_output,
    'job_title': job.title,
    'company': job.company,
    'usage': result.get('usage'),
  }
