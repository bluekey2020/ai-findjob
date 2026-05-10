"""Job search service — JD parsing, fraud detection, matching, batch import."""
import json
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.llm import call_agent
from app.models.job import Job
from app.models.profile import Profile, Skill
from app.models.preferences import Preferences
from app.prompts.job_scout import JOB_SCOUT_SYSTEM, JD_PARSE_TOOL


async def parse_jd(raw_text: str) -> dict:
  """Parse a raw job description into structured data using Haiku."""
  if not raw_text or len(raw_text.strip()) < 50:
    return {'error': 'Job description too short (min 50 chars)'}

  result = await call_agent(
    agent_name='job-scout',
    system_prompt=JOB_SCOUT_SYSTEM,
    user_message=f'Parse this job description and extract all structured fields. Detect any fraud or ghost job signals:\n\n{raw_text}',
    tools=[JD_PARSE_TOOL],
    max_tokens=2048,
  )

  if result.get('tool_output'):
    return {'parsed': result['tool_output'], 'usage': result['usage']}
  return {'parsed': None, 'raw_content': result['content'], 'usage': result['usage']}


async def parse_jd_batch(raw_texts: list[str]) -> dict:
  """Parse multiple JDs in parallel using Haiku's batch capability."""
  results = []
  for text in raw_texts:
    if text and len(text.strip()) >= 50:
      results.append(await parse_jd(text))

  return {
    'total': len(raw_texts),
    'parsed': len([r for r in results if 'parsed' in r and r['parsed']]),
    'results': results,
  }


def compute_fraud_score(job_data: dict) -> tuple[int, list[str], list[str]]:
  """Compute fraud score using heuristics without LLM.

  Returns (fraud_score, fraud_flags, dealbreaker_flags).
  """
  flags = []
  dealbreakers = []

  desc = (job_data.get('description') or '').lower()
  title = (job_data.get('title') or '').lower()

  # Ghost job detection
  vague_indicators = [
    'looking for', 'seeking', 'we are hiring', 'multiple positions',
    'various roles', 'open positions'
  ]
  vague_count = sum(1 for w in vague_indicators if w in desc)
  has_requirements = bool(job_data.get('requirements'))
  if vague_count >= 2 and not has_requirements:
    flags.append('Vague description with no specific requirements — possible ghost job')

  # Fake job detection
  payment_red_flags = ['training fee', 'deposit', 'registration fee', 'processing fee']
  for pf in payment_red_flags:
    if pf in desc:
      dealbreakers.append(f'Requests payment: "{pf}"')

  if job_data.get('source_credibility') == 'third_party':
    flags.append('Posted by third-party, not official company source')

  # Salary red flags
  salary = job_data.get('salary_range', '')
  if salary:
    try:
      parts = salary.lower().replace('k', '000').replace('万', '0000').split('-')
      if len(parts) == 2:
        low = float(parts[0].strip().replace('￥', '').replace('$', ''))
        high = float(parts[1].strip().replace('￥', '').replace('$', ''))
        ratio = high / max(low, 1)
        if ratio >= 4:
          flags.append(f'Salary range unusually wide ({ratio:.1f}x) — possible bait pricing')
    except (ValueError, ZeroDivisionError):
      pass

  # Contact method check
  if 'wechat' in desc or '微信' in desc:
    flags.append('Personal WeChat contact instead of company email')

  # No company address
  has_address = any(w in desc for w in ['address', '地址', 'located at', 'headquarters'])
  if not has_address and not job_data.get('location'):
    flags.append('No company address provided')

  # Score calculation
  score = 0
  high_severity = [f for f in flags if 'payment' in f.lower() or 'personal contact' in f.lower()]
  score += len(high_severity) * 30
  score += len(flags) * 10
  score += len(dealbreakers) * 40

  return min(score, 100), flags, dealbreakers


async def _load_user_context(db: AsyncSession, user_id: str) -> dict:
  """Load user profile and preferences for matching."""
  from sqlalchemy.orm import selectinload

  profile_result = await db.execute(
    select(Profile).where(Profile.user_id == user_id).options(selectinload(Profile.skills))
  )
  profile = profile_result.scalar_one_or_none()

  prefs_result = await db.execute(
    select(Preferences).where(Preferences.user_id == user_id)
  )
  prefs = prefs_result.scalar_one_or_none()

  return {
    'profile': profile,
    'prefs': prefs,
    'skills': {s.name.lower(): s for s in (profile.skills or [])} if profile else {},
  }


def _compute_bidirectional_match(job: dict, context: dict) -> dict:
  """Tinder-style bidirectional matching.

  Score = JD match (50%) + preference match (30%) + company health (10%) + freshness (10%)
  """
  profile = context['profile']
  prefs = context['prefs']
  user_skills = context['skills']

  if not profile:
    return {'bidirectional_score': 0, 'match_reasons': [], 'match_breakdown': {}}

  # 1. JD Match (50%) — How well does user match the job requirements?
  requirements = job.get('requirements', []) or []
  jd_score = 0
  matched_skills = []
  missing_skills = []

  if requirements:
    for req in requirements:
      req_name = req if isinstance(req, str) else req.get('name', req.get('skill', ''))
      req_lower = req_name.lower()
      if req_lower in user_skills:
        skill = user_skills[req_lower]
        level_map = {'beginner': 0.5, 'intermediate': 0.75, 'advanced': 0.9, 'expert': 1.0}
        level_weight = level_map.get(skill.level, 0.5)
        jd_score += 1.0 * level_weight
        matched_skills.append(req_name)
      else:
        jd_score += 0
        missing_skills.append(req_name)
    jd_score = (jd_score / len(requirements)) * 100
  else:
    jd_score = 50  # neutral if no requirements parsed

  # 2. Preference Match (30%) — How well does the job match user preferences?
  pref_score = 50  # neutral baseline
  pref_details = []

  if prefs:
    # Salary match
    if prefs.salary_expectation and job.get('salary_range'):
      try:
        exp = prefs.salary_expectation
        if isinstance(exp, dict):
          exp_min = exp.get('min', 0) or 0
        else:
          exp_min = 0
        salary_str = str(job['salary_range']).lower().replace('k', '000')
        # Extract numbers from salary string
        import re
        nums = re.findall(r'\d+', salary_str)
        if nums and exp_min:
          job_mid = sum(int(n) for n in nums) // len(nums)
          if job_mid >= exp_min * 0.8:
            pref_score = min(100, pref_score + 20)
            pref_details.append('Salary meets expectations')
          else:
            pref_score = max(0, pref_score - 20)
            pref_details.append('Salary below expectation')
      except (ValueError, TypeError):
        pass

    # Location match
    if prefs.target_locations and job.get('location'):
      job_loc = job['location'].lower()
      for target in prefs.target_locations:
        target_lower = (target if isinstance(target, str) else target.get('city', '')).lower()
        if target_lower and target_lower in job_loc:
          pref_score = min(100, pref_score + 15)
          pref_details.append(f'Location matches target: {target_lower}')
          break

    # Company size preference
    if prefs.company_size_preference and job.get('company_size_estimate'):
      size_map = {
        'startup': ['startup'],
        'small': ['startup', 'small'],
        'mid': ['small', 'mid'],
        'large': ['mid', 'large'],
        'enterprise': ['large', 'enterprise'],
      }
      pref_sizes = size_map.get(prefs.company_size_preference, [])
      if job['company_size_estimate'] in pref_sizes:
        pref_score = min(100, pref_score + 10)
        pref_details.append('Company size matches preference')

    # Dealbreaker check — instant -50
    if prefs.dealbreakers:
      dealbreakers = prefs.dealbreakers if isinstance(prefs.dealbreakers, list) else []
      job_text = json.dumps(job).lower()
      for db in dealbreakers:
        db_lower = (db if isinstance(db, str) else db.get('label', '')).lower()
        if db_lower and db_lower in job_text:
          pref_score -= 50
          pref_details.append(f'Hit dealbreaker: {db_lower}')

  # 3. Company Health (10%)
  health_details = []
  fraud_score = job.get('fraud_score', 0)
  company_score = max(0, 100 - fraud_score)
  if fraud_score > 20:
    health_details.append(f'Fraud concerns (score: {fraud_score})')

  quality_score = job.get('quality_score', 0)
  if quality_score > 0:
    company_score = (company_score + quality_score) / 2

  # 4. Freshness (10%)
  posted = job.get('posted_date')
  freshness_score = 50
  if posted:
    try:
      if isinstance(posted, str):
        posted_date = date.fromisoformat(posted)
      else:
        posted_date = posted
      days_old = (date.today() - posted_date).days
      if days_old <= 3:
        freshness_score = 100
      elif days_old <= 7:
        freshness_score = 80
      elif days_old <= 14:
        freshness_score = 60
      elif days_old <= 30:
        freshness_score = 30
      else:
        freshness_score = 10
    except (ValueError, TypeError):
      pass

  # Weighted total
  weighted = (
    jd_score * 0.50 +
    max(0, pref_score) * 0.30 +
    company_score * 0.10 +
    freshness_score * 0.10
  )

  return {
    'bidirectional_score': round(weighted, 1),
    'match_breakdown': {
      'jd_match': round(jd_score, 1),
      'preference_match': round(max(0, pref_score), 1),
      'company_health': round(company_score, 1),
      'freshness': round(freshness_score, 1),
    },
    'match_reasons': matched_skills[:5],
    'missing_skills': missing_skills[:5],
    'pref_details': pref_details,
    'health_details': health_details,
  }


async def search_and_score_jobs(user_id: str) -> dict:
  """Run full job search: parse → fraud detect → match score → sort."""
  async with async_session() as db:
    context = await _load_user_context(db, user_id)

    # Get all new/unprocessed jobs
    jobs_result = await db.execute(
      select(Job).where(Job.user_id == user_id, Job.status == 'new').limit(100)
    )
    jobs = jobs_result.scalars().all()

    if not jobs:
      return {
        'message': 'No unprocessed jobs found. Import jobs first via POST /api/v1/jobs/import.',
        'jobs': [],
        'stats': {},
      }

    scored = []
    for job in jobs:
      job_data = {
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'salary_range': job.salary_range,
        'requirements': job.requirements or [],
        'source_type': job.source_type,
        'posted_date': job.posted_date.isoformat() if job.posted_date else None,
        'platform': job.platform,
      }

      # Compute fraud score from existing flags
      fraud_score, fraud_flags, dealbreaker_flags = compute_fraud_score({
        'description': job.description or '',
        'title': job.title,
        'requirements': job.requirements or [],
        'salary_range': job.salary_range or '',
        'source_credibility': 'third_party' if job.source_type == 'underground' else 'official',
      })

      # Compute bidirectional match
      match_result = _compute_bidirectional_match(job_data, context)

      # Update job record
      job.match_score = int(match_result['bidirectional_score'])
      job.match_reasons = match_result.get('match_reasons', [])
      job.fraud_score = fraud_score
      job.fraud_flags = fraud_flags
      job.dealbreaker_flags = dealbreaker_flags

      scored.append({
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'platform': job.platform,
        'salary_range': job.salary_range,
        'match_score': job.match_score,
        'match_breakdown': match_result.get('match_breakdown', {}),
        'match_reasons': match_result.get('match_reasons', []),
        'missing_skills': match_result.get('missing_skills', []),
        'fraud_score': fraud_score,
        'fraud_flags': fraud_flags,
        'dealbreaker_flags': dealbreaker_flags,
        'status': job.status,
      })

    await db.commit()

    # Sort by bidirectional score descending
    scored.sort(key=lambda j: j['match_score'], reverse=True)

    # Energy bottleneck: categorize
    top_tier = [j for j in scored if j['match_score'] >= 70 and j['fraud_score'] < 20]
    mid_tier = [j for j in scored if 40 <= j['match_score'] < 70 and j['fraud_score'] < 50]
    low_tier = [j for j in scored if j['match_score'] < 40 or j['fraud_score'] >= 50]

    return {
      'total': len(scored),
      'top_picks': len(top_tier),
      'mid_tier': len(mid_tier),
      'flagged': len(low_tier),
      'jobs': scored,
      'stats': {
        'avg_match_score': round(sum(j['match_score'] for j in scored) / max(len(scored), 1), 1),
        'avg_fraud_score': round(sum(j['fraud_score'] for j in scored) / max(len(scored), 1), 1),
        'top_tier_count': len(top_tier),
        'mid_tier_count': len(mid_tier),
        'flagged_count': len(low_tier),
      },
    }


async def batch_import_jobs(user_id: str, raw_jobs: list[dict]) -> dict:
  """Import jobs from external sources (manual entry or scraper output)."""
  if not raw_jobs:
    return {'imported': 0, 'message': 'Empty job list'}

  async with async_session() as db:
    imported = 0
    skipped = 0
    duplicates = 0

    for raw in raw_jobs:
      title = raw.get('title', '')
      company = raw.get('company', '')

      if not title:
        skipped += 1
        continue

      # Check for duplicates
      existing = await db.execute(
        select(Job).where(
          Job.user_id == user_id,
          Job.title == title,
          Job.company == company,
        )
      )
      if existing.scalar_one_or_none():
        duplicates += 1
        continue

      # Build job record
      job = Job(
        user_id=user_id,
        title=title,
        company=company,
        location=raw.get('location', ''),
        region=raw.get('region', ''),
        salary_range=raw.get('salary_range', ''),
        platform=raw.get('platform', 'manual'),
        url=raw.get('url', ''),
        description=raw.get('description', ''),
        requirements=raw.get('requirements', []),
        source_type=raw.get('source_type', 'official'),
        posted_date=raw.get('posted_date'),
        status='new',
        tags=raw.get('tags', []),
        raw_jd=raw.get('raw_jd', {}),
      )
      db.add(job)
      imported += 1

    await db.commit()

  return {
    'imported': imported,
    'skipped': skipped,
    'duplicates': duplicates,
    'message': f'Imported {imported} jobs ({skipped} skipped, {duplicates} duplicates)',
  }
