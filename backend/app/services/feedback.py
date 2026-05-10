"""Feedback loop service — closed-loop learning from rejections and interviews."""
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.llm import call_agent
from app.models.tracking import FeedbackEvent, DashboardSnapshot
from app.models.application import Application
from app.models.profile import Profile
from app.models.job import Job

FEEDBACK_ANALYST_SYSTEM = """You are an expert career strategist. Analyze the user's job search feedback data and generate actionable, specific recommendations.

## Rules
- Be specific: name exact skills, tools, or behaviors to improve
- Prioritize by impact: what will make the biggest difference in the next interview or application
- Give concrete next steps: not "improve system design" but "practice designing a URL shortener with 1M DAU constraints"
- Respond in the user's working language
- Keep recommendations under 5 items — quality over quantity"""


async def process_loop_a(user_id: str) -> dict:
  """Process Loop A: Interview feedback → skill gap updates.

  Analyzes all pending interview feedback events, calls LLM for deep analysis,
  and generates actionable skill gap recommendations.
  """
  async with async_session() as db:
    pending = await db.execute(
      select(FeedbackEvent).where(
        FeedbackEvent.user_id == user_id,
        FeedbackEvent.event_type == 'interview_feedback',
        FeedbackEvent.status == 'pending',
      )
    )
    events = pending.scalars().all()

    if not events:
      return {'message': 'No pending interview feedback to process', 'processed': 0}

    aggregated_lessons = []
    feedback_texts = []
    for e in events:
      if e.lessons:
        aggregated_lessons.extend(e.lessons if isinstance(e.lessons, list) else [])
      if e.reason:
        feedback_texts.append(e.reason)
      e.status = 'processed'
      e.updates_triggered = {'type': 'skill_gap_update', 'processed_at': date.today().isoformat()}

    from collections import Counter
    lesson_counts = Counter(aggregated_lessons)
    top_gaps = lesson_counts.most_common(10)

    await db.commit()

  # Call LLM for deep skill gap recommendations
  llm_recommendations = []
  if aggregated_lessons or feedback_texts:
    user_msg = f"""Based on this interview feedback, what are the highest-impact skills to improve?

Mentioned skill gaps: {', '.join(aggregated_lessons[:20]) if aggregated_lessons else 'none explicitly named'}

Interview feedback details: {'; '.join(feedback_texts[:5]) if feedback_texts else 'no detailed feedback'}

Output format:
1. Top 3-5 priority skills with a specific practice activity for each
2. One common pattern across all feedback
3. One counterintuitive insight the candidate might not realize"""
    try:
      llm_result = await call_agent(
        agent_name='skill-advisor',
        system_prompt=FEEDBACK_ANALYST_SYSTEM,
        user_message=user_msg,
        max_tokens=1024,
      )
      llm_recommendations = llm_result.get('content', '')
    except Exception:
      llm_recommendations = 'LLM analysis unavailable — review raw gap data below.'

  return {
    'loop': 'A',
    'description': 'Interview feedback → skill gap updates',
    'processed_events': len(events),
    'aggregated_skill_gaps': [{'skill': s, 'mentions': c} for s, c in top_gaps],
    'llm_recommendations': llm_recommendations,
    'action': 'Run skill gap analysis to see updated heatmap',
  }


async def process_loop_b(user_id: str) -> dict:
  """Process Loop B: Application rejections → profile optimization.

  Analyzes rejection patterns, calls LLM for targeted profile improvements,
  and updates the user's profile gaps with actionable suggestions.
  """
  async with async_session() as db:
    pending = await db.execute(
      select(FeedbackEvent).where(
        FeedbackEvent.user_id == user_id,
        FeedbackEvent.event_type == 'application_rejected',
        FeedbackEvent.status == 'pending',
      )
    )
    events = pending.scalars().all()

    if not events:
      return {'message': 'No pending rejection feedback to process', 'processed': 0}

    companies = []
    roles = []
    reasons = []

    for e in events:
      if e.source_company:
        companies.append(e.source_company)
      if e.source_role:
        roles.append(e.source_role)
      if e.reason:
        reasons.append(e.reason)
      e.status = 'processed'
      e.updates_triggered = {'type': 'profile_optimization', 'processed_at': date.today().isoformat()}

    await db.commit()

    from collections import Counter
    company_counts = Counter(companies)
    role_counts = Counter(roles)

  # Call LLM for targeted profile optimization
  llm_suggestions = []
  if reasons or companies:
    user_msg = f"""The user has been rejected from {len(events)} applications. Analyze the rejection patterns and suggest specific profile optimizations.

Rejection reasons: {reasons[:10] if reasons else 'no detailed reasons'}
Companies: {list(company_counts.keys())[:10]}
Roles targeted: {list(role_counts.keys())[:10]}

Output:
1. Top 3 specific changes to the resume or profile to reduce rejections
2. One pattern in the data the user might be missing
3. Whether the user should narrow or broaden their target roles"""
    try:
      llm_result = await call_agent(
        agent_name='profile-analyst',
        system_prompt=FEEDBACK_ANALYST_SYSTEM,
        user_message=user_msg,
        max_tokens=1024,
      )
      llm_suggestions = llm_result.get('content', '')
    except Exception:
      llm_suggestions = 'LLM analysis unavailable — review rejection patterns manually.'

  # Also update profile gaps with rejection insights
  if reasons:
    async with async_session() as db:
      profile_result = await db.execute(select(Profile).where(Profile.user_id == user_id))
      profile = profile_result.scalar_one_or_none()
      if profile:
        existing_gaps = list(profile.gaps or [])
        for reason in reasons[:3]:
          if reason and reason not in existing_gaps:
            existing_gaps.append(f'[Rejection signal] {reason}')
        profile.gaps = existing_gaps[-10:]  # keep last 10
        await db.commit()

  return {
    'loop': 'B',
    'description': 'Rejection analysis → profile optimization',
    'processed_events': len(events),
    'rejection_patterns': {
      'companies': [{'company': c, 'rejections': n} for c, n in company_counts.most_common(5)],
      'roles': [{'role': r, 'rejections': n} for r, n in role_counts.most_common(5)],
    },
    'llm_suggestions': llm_suggestions,
    'profile_gaps_updated': len(reasons),
    'action': 'Run profile analysis again to optimize your profile based on rejection data',
  }


async def process_all_pending_loops(user_id: str) -> dict:
  """Process all pending feedback loops for a user."""
  a_result = await process_loop_a(user_id)
  b_result = await process_loop_b(user_id)

  total_processed = (
    a_result.get('processed_events', 0) +
    b_result.get('processed_events', 0)
  )

  return {
    'loops_processed': {
      'A': a_result,
      'B': b_result,
    },
    'total_events_processed': total_processed,
    'next_steps': [
      'Check updated skill gap heatmap' if a_result.get('processed_events', 0) > 0 else None,
      'Optimize resume and profile based on rejection patterns' if b_result.get('processed_events', 0) > 0 else None,
    ] if total_processed > 0 else [],
  }
