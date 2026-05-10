"""Company research service — Jim Collins style deep company analysis."""
from app.core.llm import call_agent
from app.core.database import async_session
from app.models.company import Company
from app.models.job import Job
from app.prompts.company_researcher import COMPANY_RESEARCHER_SYSTEM, COMPANY_RESEARCH_TOOL
from sqlalchemy import select


async def research_company(user_id: str, company_name: str) -> dict:
  """Deep research on a single company using Sonnet."""
  if not company_name or len(company_name.strip()) < 2:
    return {'error': 'Company name required (min 2 chars)'}

  user_message = f"""Research this company thoroughly:

Company: {company_name}

Provide a comprehensive analysis covering:
1. Company culture and values (use Glassdoor, MaiMai, Reddit if available)
2. Financial health (funding rounds, revenue trajectory, layoff history)
3. Growth stage and headcount trajectory
4. Risk signals (executive departures, lawsuits, regulatory issues)
5. Opportunity signals (new products, market expansion, high-profile hires)
6. Tech stack and engineering culture
7. Employee satisfaction and turnover signals
8. Final recommendation: strong_buy / buy / hold / sell / strong_sell

Cite sources for every claim. Distinguish facts from informed speculation."""

  result = await call_agent(
    agent_name='company-researcher',
    system_prompt=COMPANY_RESEARCHER_SYSTEM,
    user_message=user_message,
    tools=[COMPANY_RESEARCH_TOOL],
    max_tokens=3072,
  )

  research_output = result.get('tool_output')

  # Save to database
  if research_output:
    async with async_session() as db:
      company_result = await db.execute(
        select(Company).where(
          Company.user_id == user_id,
          Company.name == company_name,
        )
      )
      company = company_result.scalar_one_or_none()

      if not company:
        company = Company(
          user_id=user_id,
          name=company_name,
          industry=research_output.get('industry', ''),
          size=research_output.get('size_estimate', ''),
          location=research_output.get('headquarters', ''),
          tech_stack=research_output.get('tech_stack', []),
          culture_summary=research_output.get('culture_summary', ''),
          financial_health=research_output.get('financial_health', 'unknown'),
          risk_signals=research_output.get('risk_signals', []),
          opportunity_signals=research_output.get('opportunity_signals', []),
          research_data=research_output,
        )
        db.add(company)
      else:
        company.industry = research_output.get('industry', company.industry)
        company.size = research_output.get('size_estimate', company.size)
        company.location = research_output.get('headquarters', company.location)
        company.tech_stack = research_output.get('tech_stack', company.tech_stack)
        company.culture_summary = research_output.get('culture_summary', company.culture_summary)
        company.financial_health = research_output.get('financial_health', company.financial_health)
        company.risk_signals = research_output.get('risk_signals', [])
        company.opportunity_signals = research_output.get('opportunity_signals', [])
        company.research_data = research_output

      await db.commit()

  return {
    'company': company_name,
    'research': research_output or result.get('content'),
    'usage': result.get('usage'),
  }


async def research_all_companies(user_id: str) -> dict:
  """Research all companies associated with the user's jobs."""
  async with async_session() as db:
    jobs_result = await db.execute(
      select(Job.company).where(Job.user_id == user_id).distinct()
    )
    companies = [row[0] for row in jobs_result.all() if row[0]]

  if not companies:
    return {'message': 'No companies found — import jobs first', 'researched': []}

  results = []
  for name in companies[:10]:  # limit to 10 per batch
    r = await research_company(user_id, name)
    results.append({'company': name, 'status': 'done' if 'error' not in r else 'failed'})

  return {
    'total_companies': len(companies),
    'researched': len(results),
    'results': results,
  }
