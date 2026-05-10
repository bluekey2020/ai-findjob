"""Dashboard service — gamification, XP, achievements, mood tracking."""
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.tracking import DashboardSnapshot, ActivityLog
from app.models.application import Application
from app.models.job import Job

ACHIEVEMENTS = {
  'first_phase': {'name': 'First Step', 'description': 'Complete Phase 0 onboarding', 'xp': 50},
  'profile_built': {'name': 'Know Thyself', 'description': 'Complete Phase 1 profile', 'xp': 100},
  'first_job_search': {'name': 'Hunter Initiate', 'description': 'Complete first job search', 'xp': 150},
  '10_jobs': {'name': 'Scout', 'description': 'Discover 10+ jobs', 'xp': 100},
  '50_jobs': {'name': 'Veteran Scout', 'description': 'Discover 50+ jobs', 'xp': 200},
  'first_application': {'name': 'First Shot', 'description': 'Send your first application', 'xp': 100},
  '7_applications': {'name': 'On a Roll', 'description': 'Send 7 applications in a week', 'xp': 150},
  'first_interview': {'name': 'In the Arena', 'description': 'Land your first interview', 'xp': 200},
  'first_offer': {'name': 'The Prize', 'description': 'Receive your first offer', 'xp': 500},
  'accepted_offer': {'name': 'Winner', 'description': 'Accept an offer and complete the journey', 'xp': 1000},
  'perfect_match': {'name': 'Perfect Match', 'description': 'Find a job with 90%+ match score', 'xp': 100},
  'skill_master': {'name': 'Skill Master', 'description': 'Close 3+ P0 skill gaps', 'xp': 200},
  'company_researcher': {'name': 'Due Diligence', 'description': 'Research 5+ companies', 'xp': 100},
  'feedback_learner': {'name': 'Growth Mindset', 'description': 'Process 5+ feedback loop events', 'xp': 150},
  '3_day_streak': {'name': 'Consistent', 'description': '3-day activity streak', 'xp': 50},
  '7_day_streak': {'name': 'Dedicated', 'description': '7-day activity streak', 'xp': 150},
  '30_day_streak': {'name': 'Unstoppable', 'description': '30-day activity streak', 'xp': 500},
}


async def get_dashboard(user_id: str) -> dict:
  """Get dashboard with gamification stats."""
  async with async_session() as db:
    # Latest snapshot
    snap_result = await db.execute(
      select(DashboardSnapshot)
      .where(DashboardSnapshot.user_id == user_id)
      .order_by(DashboardSnapshot.snapshot_date.desc())
      .limit(1)
    )
    snapshot = snap_result.scalar_one_or_none()

    # Activity log
    activity_result = await db.execute(
      select(ActivityLog)
      .where(ActivityLog.user_id == user_id)
      .order_by(ActivityLog.activity_date.desc())
      .limit(30)
    )
    activities = activity_result.scalars().all()

    # Application stats
    app_count_result = await db.execute(
      select(func.count(Application.id)).where(Application.user_id == user_id)
    )
    total_apps = app_count_result.scalar() or 0

    interview_result = await db.execute(
      select(func.count(Application.id)).where(
        Application.user_id == user_id,
        Application.status.in_(['phone_screen', 'onsite', 'offer'])
      )
    )
    interviews = interview_result.scalar() or 0

    offer_result = await db.execute(
      select(func.count(Application.id)).where(
        Application.user_id == user_id,
        Application.status.in_(['offer', 'accepted'])
      )
    )
    offers = offer_result.scalar() or 0

    # Job stats
    job_count_result = await db.execute(
      select(func.count(Job.id)).where(Job.user_id == user_id)
    )
    total_jobs = job_count_result.scalar() or 0

    avg_match_result = await db.execute(
      select(func.avg(Job.match_score)).where(
        Job.user_id == user_id,
        Job.match_score > 0,
      )
    )
    avg_match = avg_match_result.scalar() or 0

  # Compute XP and achievements
  xp = 0
  earned = []

  if snapshot:
    xp = snapshot.xp_total or 0
    if snapshot.current_phase >= 1:
      earned.append(ACHIEVEMENTS['first_phase'])
    if snapshot.current_phase >= 2:
      earned.append(ACHIEVEMENTS['profile_built'])
    if snapshot.current_phase >= 3:
      earned.append(ACHIEVEMENTS['first_job_search'])
  else:
    xp = 0

  if total_jobs >= 10:
    earned.append(ACHIEVEMENTS['10_jobs'])
  if total_jobs >= 50:
    earned.append(ACHIEVEMENTS['50_jobs'])
  if total_apps >= 1:
    earned.append(ACHIEVEMENTS['first_application'])
  if total_apps >= 7:
    earned.append(ACHIEVEMENTS['7_applications'])
  if interviews >= 1:
    earned.append(ACHIEVEMENTS['first_interview'])
  if offers >= 1:
    earned.append(ACHIEVEMENTS['first_offer'])

  # Compute streak
  streak = 0
  today = date.today()

  if activities:
    sorted_dates = sorted(set(a.activity_date for a in activities), reverse=True)
    streak = 1
    for i in range(len(sorted_dates) - 1):
      if (sorted_dates[i] - sorted_dates[i + 1]).days == 1:
        streak += 1
      else:
        break
    if (today - sorted_dates[0]).days > 1:
      streak = 0  # broke streak

  if streak >= 3:
    earned.append(ACHIEVEMENTS['3_day_streak'])
  if streak >= 7:
    earned.append(ACHIEVEMENTS['7_day_streak'])
  if streak >= 30:
    earned.append(ACHIEVEMENTS['30_day_streak'])

  # Deduplicate earned achievements
  seen = set()
  unique_earned = []
  for a in earned:
    if a['name'] not in seen:
      seen.add(a['name'])
      unique_earned.append(a)

  total_xp = xp + sum(a['xp'] for a in unique_earned)

  # Funnel data
  funnel = {
    'discovered': total_jobs,
    'screened': total_jobs,
    'shortlisted': sum(1 for _ in []),
    'applied': total_apps,
    'interview': interviews,
    'offer': offers,
    'accepted': sum(1 for _ in []),
  }

  return {
    'current_phase': snapshot.current_phase if snapshot else 0,
    'days_active': len(set(a.activity_date for a in activities)) if activities else 0,
    'streak': streak,
    'avg_match_score': round(float(avg_match), 1),
    'funnel_data': funnel,
    'xp_total': total_xp,
    'achievements': unique_earned,
    'all_achievements': list(ACHIEVEMENTS.values()),
    'timeline': [
      {
        'date': a.activity_date.isoformat(),
        'phase': a.phase,
        'activities': a.activities,
        'mood': a.mood,
      }
      for a in activities[:14]
    ] if activities else [],
    'recent_activity': snapshot.recent_activity if snapshot else [],
  }
