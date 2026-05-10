from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix='/api/v1/dashboard', tags=['dashboard'])


@router.get('')
async def get_dashboard(
  current_user: User = Depends(get_current_user),
):
  from app.services.dashboard import get_dashboard as _get
  return await _get(current_user.id)
