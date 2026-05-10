from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  app_name: str = 'AI Job Hunter'
  debug: bool = True

  # Database
  database_url: str = 'sqlite+aiosqlite:///./aijob.db'

  # JWT
  secret_key: str = 'dev-secret-change-in-production'
  access_token_expire_minutes: int = 30
  refresh_token_expire_days: int = 7

  # Redis
  redis_url: str = 'redis://localhost:6379/0'

  # Anthropic
  anthropic_api_key: str = ''

  # Celery
  celery_broker_url: str = 'redis://localhost:6379/1'
  celery_result_backend: str = 'redis://localhost:6379/2'

  # SMTP (optional)
  smtp_host: str = ''
  smtp_port: int = 587
  smtp_user: str = ''
  smtp_password: str = ''
  smtp_from: str = 'noreply@aijobhunter.local'

  model_config = {'env_file': '.env', 'env_file_encoding': 'utf-8', 'extra': 'ignore'}


settings = Settings()
