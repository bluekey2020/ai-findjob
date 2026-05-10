from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix='/api/v1/resumes', tags=['resumes'])


@router.post('/generate')
async def generate_default(
  current_user: User = Depends(get_current_user),
):
  """Generate a default resume from user profile (Phase 1)."""
  from app.services.resume_generation import generate_default_resume
  result = await generate_default_resume(current_user.id)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result


@router.post('/tailor')
async def tailor_resume(
  job_id: str,
  current_user: User = Depends(get_current_user),
):
  """Generate a resume tailored to a specific job (Phase 3)."""
  from app.services.resume_generation import generate_tailored_resume
  result = await generate_tailored_resume(current_user.id, job_id)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result
