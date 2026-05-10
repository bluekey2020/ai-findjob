"""Skill gap analysis service — compute gaps between user skills and job requirements."""
import math
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import async_session
from app.models.profile import Profile, Skill
from app.models.job import Job


async def compute_skill_gaps(user_id: str) -> dict:
  """Compute skill gaps by comparing user skills with target job requirements."""
  async with async_session() as db:
    profile_result = await db.execute(
      select(Profile).where(Profile.user_id == user_id)
      .options(selectinload(Profile.skills))
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
      return {'error': 'Profile not found'}

    user_skills = profile.skills or []

    jobs_result = await db.execute(
      select(Job).where(Job.user_id == user_id, Job.status == 'new').limit(30)
    )
    jobs = jobs_result.scalars().all()

  if not jobs:
    return {
      'user_skills': [{'name': s.name, 'level': s.level, 'years': s.years, 'category': s.category}
                      for s in user_skills],
      'market_demand_skills': [],
      'gaps': [],
      'message': 'No jobs found — run job search first for gap analysis'
    }

  # Aggregate skill demand from all job requirements
  skill_demand: dict[str, int] = {}
  for job in jobs:
    for req in (job.requirements or []):
      skill_name = req if isinstance(req, str) else req.get('name', '')
      if skill_name:
        skill_demand[skill_name.lower()] = skill_demand.get(skill_name.lower(), 0) + 1

  user_skill_map = {s.name.lower(): s for s in user_skills}
  demand_max = max(skill_demand.values()) if skill_demand else 1

  gaps = []
  for skill_name, demand_count in sorted(skill_demand.items(), key=lambda x: -x[1]):
    user_skill = user_skill_map.get(skill_name.lower())
    importance = demand_count / demand_max  # 0-1

    if user_skill:
      level_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
      user_level = level_map.get(user_skill.level, 2)
      gap_size = max(0, 4 - user_level) / 4  # 0 = no gap, 1 = full gap
      heat = gap_size * importance * (demand_count / max(len(jobs), 1))
    else:
      gap_size = 1.0
      heat = importance * (demand_count / max(len(jobs), 1))

    heat_score = round(heat * 100, 1)

    if heat_score > 5:  # only include meaningful gaps
      priority = 'P0' if heat_score > 50 else 'P1' if heat_score > 20 else 'P2'
      gaps.append({
        'skill': skill_name,
        'demand_count': demand_count,
        'importance': round(importance, 2),
        'user_has': user_skill is not None,
        'user_level': user_skill.level if user_skill else None,
        'user_years': user_skill.years if user_skill else None,
        'gap_size': round(gap_size, 2),
        'heat_score': heat_score,
        'priority': priority,
      })

  return {
    'user_skills': [{'name': s.name, 'level': s.level, 'years': s.years, 'category': s.category}
                    for s in user_skills],
    'market_demand_skills': sorted(skill_demand.items(), key=lambda x: -x[1]),
    'gaps': gaps,
    'total_jobs_analyzed': len(jobs),
    'summary': {
      'p0_gaps': len([g for g in gaps if g['priority'] == 'P0']),
      'p1_gaps': len([g for g in gaps if g['priority'] == 'P1']),
      'p2_gaps': len([g for g in gaps if g['priority'] == 'P2']),
      'overall_readiness': round(
        100 - sum(g['heat_score'] for g in gaps) / max(len(gaps), 1), 1
      ),
    },
  }


async def generate_heatmap_data(user_id: str) -> dict:
  """Generate heatmap visualization data for the frontend."""
  gap_result = await compute_skill_gaps(user_id)
  if 'error' in gap_result:
    return gap_result

  gaps = gap_result.get('gaps', [])
  categories = {}
  for g in gaps:
    cat = g.get('skill', 'other')
    if cat not in categories:
      categories[cat] = []
    categories[cat].append(g)

  return {
    'categories': [
      {'name': cat, 'skills': skills, 'avg_heat': round(sum(s['heat_score'] for s in skills) / len(skills), 1)}
      for cat, skills in categories.items()
    ],
    'max_heat': max((g['heat_score'] for g in gaps), default=0),
    'summary': gap_result.get('summary', {}),
  }
