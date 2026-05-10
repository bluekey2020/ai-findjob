"""Networking strategy service — Keith Ferrazzi style connection building."""
from app.core.llm import call_agent
from app.core.database import async_session
from app.models.company import Company
from app.prompts.networking_strategist import NETWORKING_STRATEGIST_SYSTEM, NETWORKING_TOOL
from sqlalchemy import select


async def generate_networking_plan(user_id: str, company_id: str) -> dict:
  """Generate a networking and referral strategy for a target company."""
  async with async_session() as db:
    company_result = await db.execute(
      select(Company).where(Company.id == company_id, Company.user_id == user_id)
    )
    company = company_result.scalar_one_or_none()
    if not company:
      return {'error': 'Company not found'}

    company_name = company.name
    company_industry = company.industry or ''
    company_location = company.location or ''

  user_message = f"""Create a networking strategy for:

Company: {company_name}
Industry: {company_industry}
Location: {company_location}

Design a complete outreach plan including:
1. Connection paths (LinkedIn 2nd-degree, alumni, former colleagues, communities)
2. Multi-step outreach sequence with timing
3. Key communities to engage
4. Message templates for each stage
5. Estimated referral probability

Start with the warmest paths (alumni, former colleagues) before suggesting cold outreach.
For China mainland, prioritize WeChat groups, JiKe, and tech community channels."""

  result = await call_agent(
    agent_name='networking-strategist',
    system_prompt=NETWORKING_STRATEGIST_SYSTEM,
    user_message=user_message,
    tools=[NETWORKING_TOOL],
    max_tokens=3072,
  )

  plan = result.get('tool_output')

  # Save to company notes
  if plan and isinstance(plan, dict):
    async with async_session() as db:
      c_result = await db.execute(
        select(Company).where(Company.id == company_id)
      )
      c = c_result.scalar_one_or_none()
      if c:
        c.notes = (c.notes or '') + '\n\n[Networking Plan]\n' + str(plan.get('timeline', ''))
        if plan.get('key_contacts'):
          existing_contacts = c.key_contacts or []
          new_contacts = plan.get('key_contacts', [])
          c.key_contacts = existing_contacts + new_contacts
        await db.commit()

  return {
    'company': company_name,
    'networking_plan': plan or result.get('content'),
    'usage': result.get('usage'),
  }
