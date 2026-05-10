"""Celery task definitions — async background jobs for AI Job Hunter."""
import asyncio

from app.workers.celery_app import celery_app


def _run_async(coro):
  """Helper to run async service calls from sync Celery tasks."""
  return asyncio.run(coro)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def search_jobs(self, user_id: str, region: str = '', source_type: str = 'official') -> dict:
  """Search for jobs on configured platforms, score, and persist results."""
  from app.services.job_search import search_and_score_jobs
  return _run_async(search_and_score_jobs(user_id))


@celery_app.task(bind=True, max_retries=2)
def research_company(self, user_id: str, company_name: str) -> dict:
  """Deep research on a target company via LLM."""
  from app.services.company_research import research_company as _research
  return _run_async(_research(user_id, company_name))


@celery_app.task(bind=True, max_retries=2)
def generate_tailored_resume(self, user_id: str, job_id: str) -> dict:
  """Generate a resume tailored to a specific job description."""
  from app.services.resume_generation import generate_tailored_resume as _generate
  return _run_async(_generate(user_id, job_id))


@celery_app.task(bind=True, max_retries=2)
def generate_cover_letter(self, user_id: str, job_id: str, resume_id: str = '') -> dict:
  """Generate a cover letter for a job application."""
  from app.services.cover_letter import generate_cover_letter as _generate
  return _run_async(_generate(user_id, job_id))


@celery_app.task(bind=True, max_retries=2)
def analyze_profile(self, user_id: str, raw_materials: str = '') -> dict:
  """Parse raw profile materials into structured data via LLM."""
  from app.services.profile_analysis import analyze_profile as _analyze
  return _run_async(_analyze(user_id, raw_materials))


@celery_app.task(bind=True, max_retries=2)
def analyze_market(self, user_id: str) -> dict:
  """Analyze market conditions, salary benchmarks, and trends."""
  from app.services.market_analysis import analyze_market as _analyze
  return _run_async(_analyze(user_id))


@celery_app.task(bind=True, max_retries=1)
def trigger_feedback_loop(self, user_id: str, loop_type: str) -> dict:
  """Process a feedback loop event to update upstream data."""
  from app.services.feedback import process_loop_a, process_loop_b, process_all_pending_loops

  loop_map = {
    'A': process_loop_a,
    'B': process_loop_b,
    'ALL': process_all_pending_loops,
  }

  handler = loop_map.get(loop_type, process_all_pending_loops)
  return _run_async(handler(user_id))
