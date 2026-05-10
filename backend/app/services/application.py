"""Application tracking service — Kanban board, batch rhythm, status management."""
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.application import Application, ApplicationEvent
from app.models.job import Job

KANBAN_COLUMNS = ['wishlist', 'applied', 'phone_screen', 'onsite', 'offer', 'accepted', 'rejected', 'withdrawn']

BATCH_RHYTHM = {
  'batch_1': 3,   # Monday: send 3 applications
  'batch_2': 2,   # Wednesday: send 2 more
  'batch_3': 2,   # Friday: send 2 more
  'total_per_week': 7,
}


async def get_kanban(user_id: str) -> dict:
  """Get applications organized by Kanban column."""
  async with async_session() as db:
    result = await db.execute(
      select(Application)
      .where(Application.user_id == user_id)
      .order_by(Application.updated_at.desc())
      .limit(200)
    )
    apps = result.scalars().all()

  columns = {col: [] for col in KANBAN_COLUMNS}
  for app in apps:
    col = app.status if app.status in columns else 'wishlist'
    columns[col].append({
      'id': app.id,
      'job_id': app.job_id,
      'company': app.company,
      'role': app.role,
      'status': app.status,
      'resume_version': app.resume_version,
      'cover_letter_version': app.cover_letter_version,
      'applied_date': app.applied_date.isoformat() if app.applied_date else None,
      'last_contact_date': app.last_contact_date.isoformat() if app.last_contact_date else None,
      'next_step': app.next_step,
      'notes': app.notes,
      'batch_number': app.batch_number,
      'updated_at': app.updated_at.isoformat() if app.updated_at else None,
    })

  counts = {col: len(items) for col, items in columns.items()}

  return {
    'columns': columns,
    'counts': counts,
    'total': sum(counts.values()),
    'active': sum(counts[c] for c in ['applied', 'phone_screen', 'onsite']),
    'rhythm': BATCH_RHYTHM,
  }


async def create_application(
  user_id: str,
  job_id: str,
  resume_version: str | None = None,
  cover_letter_version: str | None = None,
) -> dict:
  """Create a new application from a job."""
  async with async_session() as db:
    # Get job details
    job_result = await db.execute(
      select(Job).where(Job.id == job_id, Job.user_id == user_id)
    )
    job = job_result.scalar_one_or_none()
    if not job:
      return {'error': 'Job not found'}

    # Check for existing application
    existing = await db.execute(
      select(Application).where(
        Application.user_id == user_id,
        Application.job_id == job_id,
      )
    )
    if existing.scalar_one_or_none():
      return {'error': 'Application already exists for this job'}

    # Determine batch number
    count_result = await db.execute(
      select(func.count(Application.id)).where(
        Application.user_id == user_id,
        Application.status == 'applied',
        Application.applied_date == date.today(),
      )
    )
    today_count = count_result.scalar() or 0

    # Determine which batch
    if today_count < BATCH_RHYTHM['batch_1']:
      batch = 1
    elif today_count < BATCH_RHYTHM['batch_1'] + BATCH_RHYTHM['batch_2']:
      batch = 2
    else:
      batch = 3

    app = Application(
      user_id=user_id,
      job_id=job_id,
      company=job.company,
      role=job.title,
      status='applied',
      resume_version=resume_version,
      cover_letter_version=cover_letter_version,
      applied_date=date.today(),
      batch_number=batch,
    )
    db.add(app)

    # Add initial event
    event = ApplicationEvent(
      application_id=app.id,
      event_date=date.today(),
      event_type='applied',
      detail=f'Application submitted — batch {batch}',
    )
    db.add(event)

    # Update job status
    job.status = 'applied'

    await db.commit()
    await db.refresh(app)

  return {
    'id': app.id,
    'company': app.company,
    'role': app.role,
    'status': app.status,
    'batch_number': batch,
    'applied_date': app.applied_date.isoformat(),
  }


async def update_application_status(
  app_id: str,
  user_id: str,
  new_status: str,
  detail: str | None = None,
) -> dict:
  """Move an application to a new Kanban column."""
  if new_status not in KANBAN_COLUMNS:
    return {'error': f'Invalid status. Must be one of: {KANBAN_COLUMNS}'}

  async with async_session() as db:
    result = await db.execute(
      select(Application).where(Application.id == app_id, Application.user_id == user_id)
    )
    app = result.scalar_one_or_none()
    if not app:
      return {'error': 'Application not found'}

    old_status = app.status
    app.status = new_status
    app.last_contact_date = date.today()

    # Add status change event
    event = ApplicationEvent(
      application_id=app.id,
      event_date=date.today(),
      event_type=new_status,
      detail=detail or f'Status changed: {old_status} → {new_status}',
    )
    db.add(event)

    # If rejected, create feedback event for Loop B
    if new_status == 'rejected':
      from app.models.tracking import FeedbackEvent
      fb = FeedbackEvent(
        user_id=user_id,
        event_type='application_rejected',
        phase=3,
        source_company=app.company,
        source_role=app.role,
        reason=detail or 'Rejected — no feedback provided',
        lessons=[],
        status='pending',
      )
      db.add(fb)

    await db.commit()
    await db.refresh(app)

  return {
    'id': app.id,
    'company': app.company,
    'role': app.role,
    'old_status': old_status,
    'new_status': app.status,
    'updated_at': app.updated_at.isoformat(),
  }


async def add_interview_feedback(
  app_id: str,
  user_id: str,
  feedback_data: dict,
) -> dict:
  """Record interview feedback — triggers Feedback Loop A."""
  async with async_session() as db:
    result = await db.execute(
      select(Application).where(Application.id == app_id, Application.user_id == user_id)
    )
    app = result.scalar_one_or_none()
    if not app:
      return {'error': 'Application not found'}

    # Update notes
    feedback_text = feedback_data.get('feedback', '')
    app.notes = (app.notes or '') + f'\n\n[Interview Feedback] {feedback_text}'

    # Record event
    event = ApplicationEvent(
      application_id=app.id,
      event_date=date.today(),
      event_type='interview_feedback',
      detail=feedback_text,
    )
    db.add(event)

    # Create feedback event for Loop A
    from app.models.tracking import FeedbackEvent
    skill_gaps = feedback_data.get('skill_gaps', [])
    fb = FeedbackEvent(
      user_id=user_id,
      event_type='interview_feedback',
      phase=4,
      source_company=app.company,
      source_role=app.role,
      reason=feedback_text,
      lessons=skill_gaps if isinstance(skill_gaps, list) else [],
      status='pending',
    )
    db.add(fb)

    await db.commit()

  return {
    'application_id': app.id,
    'feedback_recorded': True,
    'skill_gaps_identified': len(skill_gaps) if isinstance(skill_gaps, list) else 0,
    'message': 'Feedback recorded. Loop A will update skill gaps automatically.',
  }


async def get_batch_status(user_id: str) -> dict:
  """Get current batch progress for the week."""
  today = date.today()
  async with async_session() as db:
    result = await db.execute(
      select(Application).where(
        Application.user_id == user_id,
        Application.status == 'applied',
      )
    )
    apps = result.scalars().all()

    today_sent = sum(1 for a in apps if a.applied_date == today)

  return {
    'today': today.isoformat(),
    'rhythm': BATCH_RHYTHM,
    'today_sent': today_sent,
    'remaining_today': max(0, BATCH_RHYTHM['batch_1'] - today_sent) if today.weekday() < 5 else 0,
    'total_week': len(apps),
    'weekly_target': BATCH_RHYTHM['total_per_week'],
  }
