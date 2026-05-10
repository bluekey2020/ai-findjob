from fastapi import APIRouter, Depends, HTTPException, Form
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix='/api/v1/cover-letters', tags=['cover_letters'])


@router.post('/generate')
async def generate(
  job_id: str = Form(...),
  current_user: User = Depends(get_current_user),
):
  """Generate a cover letter for a specific job (Phase 3)."""
  from app.services.cover_letter import generate_cover_letter
  result = await generate_cover_letter(current_user.id, job_id)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result
