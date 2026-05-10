from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
  email: str
  password: str
  display_name: str | None = None


class UserLogin(BaseModel):
  email: str
  password: str


class UserResponse(BaseModel):
  id: str
  email: str
  display_name: str | None
  is_active: bool
  created_at: datetime

  model_config = {'from_attributes': True}


class TokenResponse(BaseModel):
  access_token: str
  refresh_token: str
  token_type: str = 'bearer'


class RefreshRequest(BaseModel):
  refresh_token: str
