"""Market analysis service — Reid Hoffman style market intelligence."""
from app.core.database import async_session
from app.core.llm import call_agent
from app.models.profile import Profile
from app.models.preferences import Preferences
from app.models.job import Job
from app.prompts.market_analyst import MARKET_ANALYST_SYSTEM, MARKET_ANALYSIS_TOOL
from sqlalchemy import select


async def analyze_market(user_id: str) -> dict:
  """Run comprehensive market analysis for the user's target role and location."""
  async with async_session() as db:
    profile_result = await db.execute(
      select(Profile).where(Profile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    prefs_result = await db.execute(
      select(Preferences).where(Preferences.user_id == user_id)
    )
    prefs = prefs_result.scalar_one_or_none()

    jobs_result = await db.execute(
      select(Job).where(Job.user_id == user_id).limit(50)
    )
    jobs = jobs_result.scalars().all()

  if not profile and not prefs:
    return {'error': 'Profile and preferences not found — complete Phase 0 and Phase 1 first'}

  # Build context for LLM
  context_parts = ['## Market Analysis Request\n']

  if prefs:
    target_roles = prefs.target_roles or []
    target_locations = prefs.target_locations or []
    salary_exp = prefs.salary_expectation or {}

    context_parts.append(f'Target roles: {", ".join(target_roles) if target_roles else "Not specified"}')
    context_parts.append(f'Target locations: {", ".join(str(l) for l in target_locations) if target_locations else "Not specified"}')
    if salary_exp:
      context_parts.append(f'Salary expectation: {salary_exp}')

  if profile:
    skills_summary = [f'{s.name} ({s.level}, {s.years}yr)' for s in (profile.skills or [])]
    context_parts.append(f'Current skills: {", ".join(skills_summary[:10])}')
    context_parts.append(f'Years of experience: {profile.years_experience or "unknown"}')
    context_parts.append(f'Current role: {profile.current_role or "unknown"}')

  if jobs:
    job_summaries = []
    for j in jobs[:20]:
      job_summaries.append(
        f'- {j.title} at {j.company} — {j.location} — {j.salary_range or "no salary listed"} '
        f'[platform: {j.platform}]'
      )
    context_parts.append(f'\nAvailable jobs ({len(jobs)} total, showing {len(job_summaries)}):')
    context_parts.extend(job_summaries)

  user_message = '\n'.join(context_parts)

  result = await call_agent(
    agent_name='market-analyst',
    system_prompt=MARKET_ANALYST_SYSTEM,
    user_message=user_message,
    tools=[MARKET_ANALYSIS_TOOL],
    max_tokens=3072,
  )

  return {
    'analysis': result.get('tool_output') or result.get('content'),
    'usage': result.get('usage'),
    'context': {
      'has_profile': bool(profile),
      'has_preferences': bool(prefs),
      'jobs_count': len(jobs),
    }
  }


def estimate_salary(
  role: str,
  city: str = '',
  experience_years: float = 3,
  company_size: str = 'mid',
  skill_premiums: list[str] | None = None,
) -> dict:
  """Zillow-style salary estimation using heuristic model.

  estimated = base(role, city) × exp_mod × company_mod × skill_premium
  """
  # Base salary benchmarks (annual CNY, approximate)
  ROLE_BASES = {
    'frontend': 250000,
    'backend': 280000,
    'fullstack': 300000,
    'devops': 320000,
    'data_engineer': 300000,
    'data_scientist': 350000,
    'machine_learning': 400000,
    'mobile': 280000,
    'ios': 280000,
    'android': 270000,
    'security': 350000,
    'qa': 200000,
    'sre': 350000,
    'product_manager': 300000,
    'engineering_manager': 450000,
    'cto': 800000,
    'software_engineer': 280000,
    'python': 280000,
    'java': 270000,
    'golang': 300000,
    'rust': 350000,
    'ai_engineer': 450000,
  }

  CITY_MODIFIERS = {
    'beijing': 1.0, '北京': 1.0,
    'shanghai': 0.95, '上海': 0.95,
    'shenzhen': 0.9, '深圳': 0.9,
    'hangzhou': 0.85, '杭州': 0.85,
    'guangzhou': 0.8, '广州': 0.8,
    'chengdu': 0.7, '成都': 0.7,
    'nanjing': 0.7, '南京': 0.7,
    'wuhan': 0.65, '武汉': 0.65,
    'xian': 0.6, '西安': 0.6,
    'remote': 0.85,
  }

  # Find best matching role base
  role_lower = role.lower()
  base = ROLE_BASES.get(role_lower, 250000)
  for key in ROLE_BASES:
    if key in role_lower or role_lower in key:
      base = ROLE_BASES[key]
      break

  # City modifier
  city_lower = city.lower()
  city_mod = 0.8  # default
  for key, mod in CITY_MODIFIERS.items():
    if key in city_lower:
      city_mod = mod
      break

  # Experience modifier
  if experience_years < 1:
    exp_mod = 0.6
  elif experience_years < 3:
    exp_mod = 0.8
  elif experience_years < 5:
    exp_mod = 1.0
  elif experience_years < 8:
    exp_mod = 1.3
  else:
    exp_mod = 1.6

  # Company size modifier
  size_mods = {'startup': 0.7, 'small': 0.85, 'mid': 1.0, 'large': 1.3, 'enterprise': 1.3, 'unicorn': 1.5}
  size_mod = size_mods.get(company_size, 1.0)

  # Skill premiums
  SKILL_PREMIUMS = {
    'ai': 0.20, 'ml': 0.20, 'machine_learning': 0.20, 'deep_learning': 0.20,
    'cloud': 0.15, 'aws': 0.15, 'azure': 0.12, 'gcp': 0.12,
    'security': 0.15, 'cybersecurity': 0.15,
    'blockchain': 0.10, 'web3': 0.10,
    'rust': 0.08, 'golang': 0.05,
    'kubernetes': 0.10, 'k8s': 0.10,
    'distributed_systems': 0.10,
  }
  skill_mult = 1.0
  factors = []
  for sp in (skill_premiums or []):
    sp_lower = sp.lower()
    for key, premium in SKILL_PREMIUMS.items():
      if key in sp_lower:
        skill_mult += premium
        factors.append(f'{sp} skill premium +{int(premium * 100)}%')
        break

  # Compute estimate
  mid = base * city_mod * exp_mod * size_mod * skill_mult
  low = mid * 0.75
  high = mid * 1.35

  return {
    'role': role,
    'city': city,
    'experience_years': experience_years,
    'company_size': company_size,
    'estimate': {
      'low': round(low, -3),
      'mid': round(mid, -3),
      'high': round(high, -3),
      'confidence': 0.7 if city and role else 0.5,
      'factors': factors,
      'currency': 'CNY',
      'period': 'annual',
    },
    'breakdown': {
      'base': base,
      'city_modifier': city_mod,
      'experience_modifier': exp_mod,
      'company_size_modifier': size_mod,
      'skill_multiplier': round(skill_mult, 2),
    },
  }
