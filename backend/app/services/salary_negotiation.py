"""Salary negotiation service — Chris Voss FBI-style negotiation strategy."""
from app.core.llm import call_agent
from app.prompts.salary_negotiator import SALARY_NEGOTIATOR_SYSTEM, NEGOTIATION_TOOL


async def generate_negotiation_strategy(
  offer: dict,
  market_data: dict | None = None,
  user_batna: str = '',
) -> dict:
  """Generate FBI-level salary negotiation strategy.

  Args:
    offer: dict with company, role, salary, bonus, equity, sign_on, location, remote_policy
    market_data: optional market salary benchmarks from market analysis
    user_batna: user's description of their best alternative
  """
  if not offer.get('salary'):
    return {'error': 'Offer must include at least a salary number'}

  context_parts = ['## Negotiation Target\n']

  context_parts.append(f"Company: {offer.get('company', 'Unknown')}")
  context_parts.append(f"Role: {offer.get('role', 'Unknown')}")
  context_parts.append(f"Base Salary: {offer.get('salary', 'N/A')}")
  context_parts.append(f"Bonus: {offer.get('bonus', 'N/A')}")
  context_parts.append(f"Equity: {offer.get('equity', 'N/A')}")
  context_parts.append(f"Sign-on: {offer.get('sign_on', 'N/A')}")
  context_parts.append(f"Location: {offer.get('location', 'N/A')}")
  context_parts.append(f"Remote: {offer.get('remote_policy', 'N/A')}")

  if market_data:
    context_parts.append(f'\n### Market Data\n{market_data}')

  if user_batna:
    context_parts.append(f'\n### User BATNA\n{user_batna}')

  user_message = '\n'.join(context_parts)

  result = await call_agent(
    agent_name='salary-negotiator',
    system_prompt=SALARY_NEGOTIATOR_SYSTEM,
    user_message=user_message,
    tools=[NEGOTIATION_TOOL],
    max_tokens=4096,
  )

  strategy = result.get('tool_output')

  return {
    'offer': {
      'company': offer.get('company'),
      'role': offer.get('role'),
      'salary': offer.get('salary'),
    },
    'negotiation_strategy': strategy or result.get('content'),
    'usage': result.get('usage'),
  }
