"""Interview preparation service — Gayle McDowell style comprehensive prep."""
from app.core.llm import call_agent
from app.core.database import async_session
from app.models.profile import Profile
from app.models.job import Job
from app.models.company import Company
from app.prompts.interview_coach import INTERVIEW_COACH_SYSTEM, INTERVIEW_PREP_TOOL
from sqlalchemy import select
from sqlalchemy.orm import selectinload


async def prepare_interview(
  user_id: str,
  job_id: str,
  interview_type: str = 'full_loop',
) -> dict:
  """Generate a comprehensive interview preparation plan."""
  async with async_session() as db:
    # Load job
    job_result = await db.execute(
      select(Job).where(Job.id == job_id, Job.user_id == user_id)
    )
    job = job_result.scalar_one_or_none()
    if not job:
      return {'error': 'Job not found'}

    # Load profile with skills
    profile_result = await db.execute(
      select(Profile).where(Profile.user_id == user_id).options(selectinload(Profile.skills))
    )
    profile = profile_result.scalar_one_or_none()

    # Load company
    company_result = await db.execute(
      select(Company).where(Company.user_id == user_id, Company.name == job.company)
    )
    company = company_result.scalar_one_or_none()

  # Build context for LLM
  context_parts = [f'## Interview Preparation Request\n']
  context_parts.append(f'Company: {job.company}')
  context_parts.append(f'Role: {job.title}')
  context_parts.append(f'Interview Type: {interview_type}')
  context_parts.append(f'Job Location: {job.location or "Unknown"}')

  if job.description:
    context_parts.append(f'\n### Job Description\n{job.description[:2000]}')

  if job.requirements:
    reqs = job.requirements
    skills_list = [r if isinstance(r, str) else r.get('name', str(r)) for r in reqs]
    context_parts.append(f'\n### Requirements\n{", ".join(skills_list)}')

  if profile:
    context_parts.append(f'\n### Candidate Profile')
    context_parts.append(f'Name: {profile.name or "N/A"}')
    context_parts.append(f'Current Role: {profile.current_role or "N/A"}')
    context_parts.append(f'Years of Experience: {profile.years_experience or "N/A"}')
    if profile.skills:
      skills = [f'{s.name} ({s.level}, {s.years}yr)' for s in profile.skills[:15]]
      context_parts.append(f'Skills: {", ".join(skills)}')
    if profile.summary:
      context_parts.append(f'Summary: {profile.summary[:500]}')

  if company and company.research_data:
    research = company.research_data
    if isinstance(research, dict):
      context_parts.append(f'\n### Company Research')
      context_parts.append(f'Industry: {company.industry or "N/A"}')
      context_parts.append(f'Financial Health: {company.financial_health or "N/A"}')
      if company.culture_summary:
        context_parts.append(f'Culture: {company.culture_summary[:300]}')
      if company.risk_signals:
        context_parts.append(f'Risk Signals: {len(company.risk_signals)}')
      if company.opportunity_signals:
        context_parts.append(f'Opportunity Signals: {len(company.opportunity_signals)}')

  user_message = '\n'.join(context_parts)

  result = await call_agent(
    agent_name='interview-coach',
    system_prompt=INTERVIEW_COACH_SYSTEM,
    user_message=user_message,
    tools=[INTERVIEW_PREP_TOOL],
    max_tokens=4096,
  )

  prep_data = result.get('tool_output')

  return {
    'company': job.company,
    'role': job.title,
    'interview_type': interview_type,
    'prep_plan': prep_data or result.get('content'),
    'usage': result.get('usage'),
    'has_company_research': bool(company and company.research_data),
  }


async def get_interview_questions(
  user_id: str,
  job_id: str,
  category: str = 'behavioral',
  difficulty: str = 'medium',
) -> dict:
  """Generate targeted interview questions for practice."""
  prep_result = await prepare_interview(user_id, job_id)
  if 'error' in prep_result:
    return prep_result

  prep_plan = prep_result.get('prep_plan', {})
  if isinstance(prep_plan, dict):
    questions = prep_plan.get('mock_interview_questions', [])
    filtered = [q for q in questions if q.get('category') == category and q.get('difficulty') == difficulty]
    if not filtered:
      filtered = questions[:5]
    return {
      'company': prep_result['company'],
      'role': prep_result['role'],
      'questions': filtered,
      'total_available': len(questions),
    }

  return {'message': 'No structured questions available — use the full prep plan', 'prep_plan': prep_plan}
