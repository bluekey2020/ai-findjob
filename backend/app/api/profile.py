from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.profile import Profile, Skill, WorkExperience, Education, Project, Language, Certification
from app.schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter(prefix='/api/v1/profile', tags=['profile'])


async def _get_profile(db: AsyncSession, user_id: str) -> Profile | None:
  result = await db.execute(
    select(Profile)
    .where(Profile.user_id == user_id)
    .options(
      selectinload(Profile.skills),
      selectinload(Profile.work_experiences),
      selectinload(Profile.education),
      selectinload(Profile.projects),
      selectinload(Profile.languages),
      selectinload(Profile.certifications),
    )
  )
  return result.scalar_one_or_none()


@router.get('', response_model=ProfileResponse)
async def get_profile(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  profile = await _get_profile(db, current_user.id)
  if not profile:
    raise HTTPException(status_code=404, detail='Profile not found')
  return profile


@router.put('', response_model=ProfileResponse)
async def update_profile(
  data: ProfileUpdate,
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  profile = await _get_profile(db, current_user.id)
  if not profile:
    profile = Profile(user_id=current_user.id)
    db.add(profile)

  for field in ['name', 'email', 'phone', 'location', 'city', 'country',
                'years_of_experience', 'current_role', 'current_company', 'summary']:
    val = getattr(data, field, None)
    if val is not None:
      setattr(profile, field, val)
  if data.highlights is not None:
    profile.highlights = data.highlights
  if data.gaps is not None:
    profile.gaps = data.gaps
  if data.target_roles is not None:
    profile.target_roles = data.target_roles

  await db.flush()

  if data.skills is not None:
    await _replace_children(db, profile, Skill, data.skills)
  if data.work_experiences is not None:
    await _replace_children(db, profile, WorkExperience, data.work_experiences)
  if data.education is not None:
    await _replace_children(db, profile, Education, data.education)
  if data.projects is not None:
    await _replace_children(db, profile, Project, data.projects)
  if data.languages is not None:
    await _replace_children(db, profile, Language, data.languages)
  if data.certifications is not None:
    await _replace_children(db, profile, Certification, data.certifications)

  await db.commit()
  return await _get_profile(db, current_user.id)


@router.post('/analyze')
async def analyze_profile_endpoint(
  raw_text: str = Form(''),
  file: UploadFile | None = File(None),
  current_user: User = Depends(get_current_user),
):
  """Upload raw materials or paste text, then extract structured profile via LLM."""
  content = raw_text
  if file:
    try:
      content = (await file.read()).decode('utf-8')
    except UnicodeDecodeError:
      content = (await file.read()).decode('gbk', errors='replace')

  if not content.strip():
    raise HTTPException(status_code=400, detail='请提供文本内容或上传文件')

  from app.services.profile_analysis import analyze_profile
  result = await analyze_profile(current_user.id, content)
  return result


async def _replace_children(db: AsyncSession, profile: Profile, model, items: list):
  existing = (await db.execute(
    select(model).where(model.profile_id == profile.id)
  )).scalars().all()
  for item in existing:
    await db.delete(item)

  for i, item in enumerate(items):
    item_data = item.model_dump(exclude={'id'}) if hasattr(item, 'model_dump') else dict(item)
    item_data['profile_id'] = profile.id
    item_data['sort_order'] = i
    db.add(model(**item_data))
