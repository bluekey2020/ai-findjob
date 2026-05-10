from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.preferences import Preferences
from app.schemas.preferences import PreferencesResponse, PreferencesUpdate

router = APIRouter(prefix='/api/v1/preferences', tags=['preferences'])


@router.get('', response_model=PreferencesResponse)
async def get_preferences(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  result = await db.execute(select(Preferences).where(Preferences.user_id == current_user.id))
  prefs = result.scalar_one_or_none()
  if not prefs:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Preferences not found')
  return prefs


@router.put('', response_model=PreferencesResponse)
async def update_preferences(
  data: PreferencesUpdate,
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  result = await db.execute(select(Preferences).where(Preferences.user_id == current_user.id))
  prefs = result.scalar_one_or_none()

  if not prefs:
    prefs = Preferences(user_id=current_user.id)
    db.add(prefs)

  for field in ['language', 'city_preference', 'visa_status', 'company_size_preference',
                'overtime_tolerance', 'timeline']:
    val = getattr(data, field, None)
    if val is not None:
      setattr(prefs, field, val)

  for int_field in ['salary_amount', 'notice_period_days', 'job_freshness_days']:
    val = getattr(data, int_field, None)
    if val is not None:
      setattr(prefs, int_field, val)

  for bool_field in ['willing_to_relocate']:
    val = getattr(data, bool_field, None)
    if val is not None:
      setattr(prefs, bool_field, val)

  for list_field in ['target_roles', 'target_regions', 'dealbreakers',
                     'preferred_platforms', 'dream_companies']:
    val = getattr(data, list_field, None)
    if val is not None:
      setattr(prefs, list_field, val)

  if data.salary_currency is not None:
    prefs.salary_currency = data.salary_currency
  if data.salary_period is not None:
    prefs.salary_period = data.salary_period

  await db.commit()
  await db.refresh(prefs)
  return prefs
