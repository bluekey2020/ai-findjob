from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.engine.state_machine import (
  get_current_phase, advance_phase, get_phase_info,
  get_feedback_loop_status, get_demo_guide, PHASES
)

router = APIRouter(prefix='/api/v1/phases', tags=['phases'])


@router.get('')
async def current_phase(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  phase_num = await get_current_phase(db, current_user.id)
  pd = get_phase_info(phase_num)

  return {
    'current_phase': phase_num,
    'phase_name': pd.name if pd else 'Unknown',
    'description': pd.description if pd else '',
    'gate': pd.gate_description if pd else '',
    'agents': pd.agents if pd else [],
    'all_phases': [
      {'number': p.number, 'name': p.name, 'description': p.description, 'gate': p.gate_description}
      for p in PHASES
    ],
  }


@router.post('/advance')
async def do_advance(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  return await advance_phase(db, current_user.id)


@router.get('/feedback-loops')
async def feedback_loops(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  return await get_feedback_loop_status(db, current_user.id)


@router.get('/guide')
async def demo_guide(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  """6-step demo flow guide — shows what's done and what to do next."""
  return await get_demo_guide(db, current_user.id)


@router.post('/feedback-loops/process')
async def process_feedback_loops(
  current_user: User = Depends(get_current_user),
  loop: str = 'all',
):
  """Process pending feedback loops — A (interview→skills), B (rejection→profile), or all."""
  from app.services.feedback import process_loop_a, process_loop_b, process_all_pending_loops

  if loop == 'A':
    return await process_loop_a(current_user.id)
  elif loop == 'B':
    return await process_loop_b(current_user.id)
  else:
    return await process_all_pending_loops(current_user.id)
