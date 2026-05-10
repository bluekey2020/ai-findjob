from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_current_user
from app.models.user import User
from app.models.company import Company
from app.core.database import get_db

router = APIRouter(prefix='/api/v1/companies', tags=['companies'])


@router.get('')
async def list_companies(
  limit: int = Query(50, le=100),
  offset: int = Query(0),
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  q = select(Company).where(Company.user_id == current_user.id).offset(offset).limit(limit)
  result = await db.execute(q)
  companies = result.scalars().all()
  return [
    {
      'id': c.id,
      'name': c.name,
      'industry': c.industry,
      'size': c.size,
      'location': c.location,
      'website': c.website,
      'tech_stack': c.tech_stack,
      'culture_summary': c.culture_summary,
      'financial_health': c.financial_health,
      'risk_signals': c.risk_signals,
      'opportunity_signals': c.opportunity_signals,
      'created_at': c.created_at.isoformat() if c.created_at else None,
    }
    for c in companies
  ]


@router.get('/{company_id}')
async def get_company(
  company_id: str,
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  result = await db.execute(
    select(Company).where(Company.id == company_id, Company.user_id == current_user.id)
  )
  company = result.scalar_one_or_none()
  if not company:
    raise HTTPException(status_code=404, detail='Company not found')

  return {
    'id': company.id,
    'name': company.name,
    'industry': company.industry,
    'size': company.size,
    'location': company.location,
    'website': company.website,
    'tech_stack': company.tech_stack,
    'culture_summary': company.culture_summary,
    'financial_health': company.financial_health,
    'risk_signals': company.risk_signals,
    'opportunity_signals': company.opportunity_signals,
    'key_contacts': company.key_contacts,
    'notes': company.notes,
    'research_data': company.research_data,
    'created_at': company.created_at.isoformat() if company.created_at else None,
  }


@router.post('/research')
async def research_all_companies(
  current_user: User = Depends(get_current_user),
):
  """Research all companies associated with user's jobs (LLM-powered)."""
  from app.services.company_research import research_all_companies
  return await research_all_companies(current_user.id)


@router.post('/{company_id}/research')
async def research_one_company(
  company_id: str,
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  """Deep research on a specific company (LLM-powered)."""
  from app.services.company_research import research_company

  company_result = await db.execute(
    select(Company).where(Company.id == company_id, Company.user_id == current_user.id)
  )
  company = company_result.scalar_one_or_none()
  if not company:
    raise HTTPException(status_code=404, detail='Company not found')

  result = await research_company(current_user.id, company.name)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result
