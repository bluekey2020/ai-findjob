from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
  return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
  expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
  return jwt.encode(
    {'sub': user_id, 'exp': expire, 'type': 'access'},
    settings.secret_key,
    algorithm='HS256'
  )


def create_refresh_token(user_id: str) -> str:
  expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
  return jwt.encode(
    {'sub': user_id, 'exp': expire, 'type': 'refresh'},
    settings.secret_key,
    algorithm='HS256'
  )


def decode_token(token: str) -> dict:
  return jwt.decode(token, settings.secret_key, algorithms=['HS256'])
