from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix='/api/v1/interviews', tags=['interviews'])


@router.post('/prep')
async def prepare_interview(
  job_id: str,
  interview_type: str = 'full_loop',
  current_user: User = Depends(get_current_user),
):
  """Generate a comprehensive interview preparation plan (Gayle McDowell style)."""
  from app.services.interview_prep import prepare_interview as _prep
  result = await _prep(current_user.id, job_id, interview_type)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result


@router.get('/questions')
async def get_questions(
  job_id: str = Query(...),
  category: str = Query('behavioral'),
  difficulty: str = Query('medium'),
  current_user: User = Depends(get_current_user),
):
  """Get practice interview questions filtered by category and difficulty."""
  from app.services.interview_prep import get_interview_questions as _get
  result = await _get(current_user.id, job_id, category, difficulty)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result
