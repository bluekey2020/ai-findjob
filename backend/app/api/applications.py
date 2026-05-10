from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.models.user import User
from app.core.database import get_db

router = APIRouter(prefix='/api/v1/applications', tags=['applications'])


@router.get('/kanban')
async def get_kanban(
  current_user: User = Depends(get_current_user),
):
  """Get applications organized by Kanban column."""
  from app.services.application import get_kanban as _get_kanban
  return await _get_kanban(current_user.id)


@router.post('')
async def create_application(
  job_id: str = Body(...),
  resume_version: str | None = Body(None),
  cover_letter_version: str | None = Body(None),
  current_user: User = Depends(get_current_user),
):
  """Create a new application from a job — moves to 'applied' column."""
  from app.services.application import create_application as _create
  result = await _create(current_user.id, job_id, resume_version, cover_letter_version)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result


@router.put('/{app_id}/status')
async def update_status(
  app_id: str,
  new_status: str = Body(..., embed=True),
  detail: str | None = Body(None, embed=True),
  current_user: User = Depends(get_current_user),
):
  """Move application to a new Kanban column."""
  from app.services.application import update_application_status as _update
  result = await _update(app_id, current_user.id, new_status, detail)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result


@router.post('/{app_id}/interview-feedback')
async def add_feedback(
  app_id: str,
  feedback: str = Body(...),
  skill_gaps: list[str] = Body(default=[]),
  current_user: User = Depends(get_current_user),
):
  """Record interview feedback — triggers Feedback Loop A."""
  from app.services.application import add_interview_feedback as _add
  return await _add(app_id, current_user.id, {
    'feedback': feedback,
    'skill_gaps': skill_gaps,
  })


@router.get('/batch-status')
async def get_batch_status(
  current_user: User = Depends(get_current_user),
):
  """Get current batch progress and rhythm info."""
  from app.services.application import get_batch_status as _status
  return await _status(current_user.id)
