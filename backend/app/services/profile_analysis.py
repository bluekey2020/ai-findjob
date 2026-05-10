"""Profile analysis service — parse raw materials into structured profile via LLM."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.llm import call_agent
from app.core.database import async_session
from app.models.user import User
from app.models.profile import Profile, Skill, WorkExperience, Education, Project, Language, Certification
from app.prompts.profile_analyst import PROFILE_ANALYST_SYSTEM, PROFILE_EXTRACTION_TOOL


async def analyze_profile(user_id: str, raw_materials: str) -> dict:
  """
  Parse raw profile materials (resume text, self-intro, project docs) into structured JSON.

  Args:
    user_id: the user to associate the profile with
    raw_materials: concatenated raw text from uploaded files

  Returns:
    dict with extracted profile data and validation warnings
  """
  result = await call_agent(
    agent_name='profile-analyst',
    system_prompt=PROFILE_ANALYST_SYSTEM,
    user_message=f'Extract a structured profile from these career materials:\n\n{raw_materials}',
    tools=[PROFILE_EXTRACTION_TOOL],
    max_tokens=4096,
  )

  tool_output = result.get('tool_output')
  if not tool_output:
    return {'error': 'No structured output from LLM', 'raw_content': result.get('content')}

  # Save to database
  async with async_session() as db:
    await _save_profile(db, user_id, tool_output)

  return {
    'profile': tool_output,
    'validation_warnings': tool_output.get('validation_warnings', []),
    'usage': result.get('usage'),
  }


async def _save_profile(db: AsyncSession, user_id: str, data: dict):
  # Check existing
  existing = await db.execute(select(Profile).where(Profile.user_id == user_id))
  profile = existing.scalar_one_or_none()

  basics = data.get('basics', {})
  if not profile:
    profile = Profile(user_id=user_id)
    db.add(profile)

  profile.name = basics.get('name', profile.name)
  profile.email = basics.get('email', profile.email)
  profile.phone = basics.get('phone', profile.phone)
  profile.location = basics.get('location', profile.location)
  profile.city = basics.get('city', profile.city)
  profile.country = basics.get('country', profile.country)
  profile.years_of_experience = basics.get('years_of_experience', profile.years_of_experience)
  profile.current_role = basics.get('current_role', profile.current_role)
  profile.current_company = basics.get('current_company', profile.current_company)
  profile.summary = data.get('summary', profile.summary)
  profile.highlights = data.get('highlights', [])
  profile.gaps = data.get('gaps', [])
  profile.target_roles = data.get('target_roles', [])
  await db.flush()

  # Replace children
  for i, s in enumerate(data.get('skills', [])):
    db.add(Skill(profile_id=profile.id, name=s['name'], level=s.get('level'),
                  years=s.get('years'), category=s.get('category'), sort_order=i))

  for i, exp in enumerate(data.get('work_experience', [])):
    db.add(WorkExperience(
      profile_id=profile.id, company=exp.get('company', ''),
      title=exp.get('title', ''), start_date=exp.get('start_date', ''),
      end_date=exp.get('end_date', ''), description=exp.get('description', ''),
      highlights=exp.get('highlights', []), tech_stack=exp.get('tech_stack', []),
      role=exp.get('role', ''), sort_order=i
    ))

  for i, edu in enumerate(data.get('education', [])):
    db.add(Education(
      profile_id=profile.id, school=edu.get('school', ''),
      degree=edu.get('degree', ''), field=edu.get('field', ''),
      graduation=edu.get('graduation', ''), gpa=edu.get('gpa', ''),
      honors=edu.get('honors', []), sort_order=i
    ))

  for i, proj in enumerate(data.get('projects', [])):
    db.add(Project(
      profile_id=profile.id, name=proj.get('name', ''),
      description=proj.get('description', ''), url=proj.get('url', ''),
      highlights=proj.get('highlights', []), role=proj.get('role', ''),
      tech_stack=proj.get('tech_stack', []), duration=proj.get('duration', ''),
      sort_order=i
    ))

  for lang in data.get('languages', []):
    db.add(Language(profile_id=profile.id, name=lang.get('name', ''),
                     proficiency=lang.get('proficiency', '')))

  for cert in data.get('certifications', []):
    db.add(Certification(profile_id=profile.id, name=cert if isinstance(cert, str) else cert.get('name', '')))

  await db.commit()
