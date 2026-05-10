from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix='/api/v1/networking', tags=['networking'])


@router.post('/plan')
async def generate_plan(
  company_id: str,
  current_user: User = Depends(get_current_user),
):
  """Generate networking and referral strategy for a company (Keith Ferrazzi style)."""
  from app.services.networking import generate_networking_plan as _plan
  result = await _plan(current_user.id, company_id)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result
