from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.api import auth, users, profile, preferences, jobs, dashboard, companies, phases
from app.api import resumes, cover_letters, skill_gaps, market, applications, interviews, networking, offers, export as export_api


@asynccontextmanager
async def lifespan(app: FastAPI):
  await init_db()
  yield


app = FastAPI(
  title='AI Job Hunter',
  version='1.0.0',
  lifespan=lifespan
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=['http://localhost:5173'],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(profile.router)
app.include_router(preferences.router)
app.include_router(jobs.router)
app.include_router(dashboard.router)
app.include_router(companies.router)
app.include_router(phases.router)
app.include_router(resumes.router)
app.include_router(cover_letters.router)
app.include_router(skill_gaps.router)
app.include_router(market.router)
app.include_router(applications.router)
app.include_router(interviews.router)
app.include_router(networking.router)
app.include_router(offers.router)
app.include_router(export_api.router)


@app.get('/api/health')
async def health():
  return {'status': 'ok'}
