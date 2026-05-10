from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.models.user import User
from app.services.skill_gap import compute_skill_gaps, generate_heatmap_data

router = APIRouter(prefix='/api/v1/skill-gaps', tags=['skill_gaps'])


@router.get('')
async def get_skill_gaps(
  current_user: User = Depends(get_current_user),
):
  return await compute_skill_gaps(current_user.id)


@router.get('/heatmap')
async def get_heatmap(
  current_user: User = Depends(get_current_user),
):
  return await generate_heatmap_data(current_user.id)
