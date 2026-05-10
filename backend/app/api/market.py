from fastapi import APIRouter, Depends, Query
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix='/api/v1/market', tags=['market'])


@router.get('/analysis')
async def get_market_analysis(
  current_user: User = Depends(get_current_user),
):
  """Run comprehensive market analysis for user's target role/location (Opus LLM)."""
  from app.services.market_analysis import analyze_market
  return await analyze_market(current_user.id)


@router.get('/salary-estimate')
async def get_salary_estimate(
  role: str = Query(..., description='Job role/title'),
  city: str = Query('', description='City name'),
  experience_years: float = Query(3, description='Years of experience'),
  company_size: str = Query('mid', description='startup/small/mid/large/enterprise/unicorn'),
  skills: str = Query('', description='Comma-separated skill names for premium calculation'),
):
  """Zillow-style salary estimation (rule-based, no LLM call)."""
  from app.services.market_analysis import estimate_salary
  skill_list = [s.strip() for s in skills.split(',') if s.strip()] if skills else []
  return estimate_salary(role, city, experience_years, company_size, skill_list)
