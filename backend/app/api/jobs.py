from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_current_user
from app.models.user import User
from app.models.job import Job
from app.schemas.job import JobResponse, JobUpdate
from app.core.database import get_db

router = APIRouter(prefix='/api/v1/jobs', tags=['jobs'])


@router.get('', response_model=list[JobResponse])
async def list_jobs(
  status: str | None = Query(None),
  limit: int = Query(50, le=100),
  offset: int = Query(0),
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  q = select(Job).where(Job.user_id == current_user.id)
  if status:
    q = q.where(Job.status == status)
  q = q.order_by(Job.match_score.desc()).offset(offset).limit(limit)
  result = await db.execute(q)
  return result.scalars().all()


@router.get('/{job_id}', response_model=JobResponse)
async def get_job(
  job_id: str,
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  result = await db.execute(
    select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
  )
  job = result.scalar_one_or_none()
  if not job:
    raise HTTPException(status_code=404, detail='Job not found')
  return job


@router.put('/{job_id}', response_model=JobResponse)
async def update_job(
  job_id: str,
  data: JobUpdate,
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  result = await db.execute(
    select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
  )
  job = result.scalar_one_or_none()
  if not job:
    raise HTTPException(status_code=404, detail='Job not found')

  if data.status is not None:
    job.status = data.status
  if data.is_top_pick is not None:
    job.is_top_pick = data.is_top_pick

  await db.commit()
  await db.refresh(job)
  return job


@router.post('/import')
async def import_jobs(
  jobs: list[dict] = Body(..., description='Array of raw job objects'),
  current_user: User = Depends(get_current_user),
):
  """Batch import jobs from external sources (manual entry or scraper output)."""
  from app.services.job_search import batch_import_jobs
  return await batch_import_jobs(current_user.id, jobs)


@router.post('/parse-jd')
async def parse_jd_endpoint(
  raw_text: str = Body(..., embed=True),
  current_user: User = Depends(get_current_user),
):
  """Parse a raw job description into structured data using Haiku LLM."""
  from app.services.job_search import parse_jd
  result = await parse_jd(raw_text)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result


@router.post('/search')
async def search_jobs(
  current_user: User = Depends(get_current_user),
):
  """Run full job search pipeline: parse → fraud detect → match score → sort."""
  from app.services.job_search import search_and_score_jobs
  return await search_and_score_jobs(current_user.id)


@router.post('/{job_id}/swipe')
async def swipe_job(
  job_id: str,
  direction: str = Body(..., embed=True, description='"right" (interested) or "left" (skip)'),
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  """Record a Tinder-style swipe on a job. Left = skip, Right = interested."""
  if direction not in ('left', 'right'):
    raise HTTPException(status_code=400, detail='Direction must be "left" or "right"')

  result = await db.execute(
    select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
  )
  job = result.scalar_one_or_none()
  if not job:
    raise HTTPException(status_code=404, detail='Job not found')

  job.status = 'applied' if direction == 'right' else 'skipped'
  await db.commit()
  await db.refresh(job)

  return {'id': job.id, 'title': job.title, 'company': job.company, 'status': job.status}


@router.post('/{job_id}/apply')
async def apply_to_job(
  job_id: str,
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  """Composite apply: create application + tailor resume + generate cover letter."""
  from app.services.application import create_application
  from app.services.resume_generation import generate_tailored_resume
  from app.services.cover_letter import generate_cover_letter
  from app.engine.state_machine import try_auto_advance

  job_result = await db.execute(
    select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
  )
  job = job_result.scalar_one_or_none()
  if not job:
    raise HTTPException(status_code=404, detail='Job not found')

  results = {'job_id': job_id, 'title': job.title, 'company': job.company}

  app_result = await create_application(current_user.id, job_id)
  if 'error' in app_result:
    raise HTTPException(status_code=400, detail=app_result['error'])
  results['application'] = app_result

  try:
    resume_result = await generate_tailored_resume(current_user.id, job_id)
    if 'error' not in resume_result:
      results['tailored_resume'] = resume_result.get('resume')
  except Exception:
    results['tailored_resume'] = None

  try:
    cover_result = await generate_cover_letter(current_user.id, job_id)
    if 'error' not in cover_result:
      results['cover_letter'] = cover_result.get('cover_letter')
  except Exception:
    results['cover_letter'] = None

  job.status = 'applied'
  await db.commit()

  await try_auto_advance(db, current_user.id)

  return results
