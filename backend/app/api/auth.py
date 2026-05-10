from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, RefreshRequest

router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
  existing = await db.execute(select(User).where(User.email == data.email))
  if existing.scalar_one_or_none():
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')

  user = User(
    email=data.email,
    password_hash=hash_password(data.password),
    display_name=data.display_name
  )
  db.add(user)
  await db.commit()
  await db.refresh(user)
  return user


@router.post('/login', response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(User).where(User.email == data.email))
  user = result.scalar_one_or_none()

  if not user or not verify_password(data.password, user.password_hash):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

  return {
    'access_token': create_access_token(user.id),
    'refresh_token': create_refresh_token(user.id),
    'token_type': 'bearer'
  }


@router.post('/refresh', response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
  try:
    payload = decode_token(data.refresh_token)
    if payload.get('type') != 'refresh':
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type')
    user_id = payload.get('sub')
  except Exception:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired refresh token')

  result = await db.execute(select(User).where(User.id == user_id))
  user = result.scalar_one_or_none()
  if not user or not user.is_active:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

  return {
    'access_token': create_access_token(user.id),
    'refresh_token': create_refresh_token(user.id),
    'token_type': 'bearer'
  }
