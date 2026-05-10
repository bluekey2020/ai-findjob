"""Offer evaluation service — Daniel Kahneman style multi-offer comparison with bias correction."""
import json
from app.core.llm import call_agent
from app.core.database import async_session
from app.models.profile import Profile
from app.models.preferences import Preferences
from app.models.tracking import FeedbackEvent
from app.prompts.offer_evaluator import OFFER_EVALUATOR_SYSTEM, OFFER_EVALUATION_TOOL
from sqlalchemy import select


async def evaluate_offers(
  user_id: str,
  offers: list[dict],
  user_weights: dict | None = None,
) -> dict:
  """Compare multiple offers with cognitive bias correction.

  Args:
    user_id: user ID for loading context
    offers: list of offer dicts with keys: company, role, salary, bonus_pct, equity, sign_on, location, remote_policy
    user_weights: optional custom dimension weights; if None, uses pairwise comparison defaults
  """
  if len(offers) < 1:
    return {'error': 'At least 1 offer required for evaluation'}
  if len(offers) > 5:
    return {'error': 'Maximum 5 offers for meaningful comparison'}

  async with async_session() as db:
    profile_result = await db.execute(
      select(Profile).where(Profile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    prefs_result = await db.execute(
      select(Preferences).where(Preferences.user_id == user_id)
    )
    prefs = prefs_result.scalar_one_or_none()

  # Build offer summary
  offers_text = []
  for i, o in enumerate(offers):
    total = o.get('salary', 0)
    if o.get('bonus_pct'):
      total += total * (o['bonus_pct'] / 100)
    if o.get('sign_on'):
      total += o['sign_on'] / 4  # amortize sign-on over ~4 years
    offers_text.append(
      f"Offer {chr(65 + i)}: {o.get('company', 'Unknown')} — {o.get('role', 'Unknown')}\n"
      f"  Base: {o.get('salary', 'N/A')}\n"
      f"  Bonus: {o.get('bonus_pct', 'N/A')}%\n"
      f"  Equity: {o.get('equity', 'N/A')}\n"
      f"  Sign-on: {o.get('sign_on', 'N/A')}\n"
      f"  Location: {o.get('location', 'N/A')} ({o.get('remote_policy', 'N/A')})\n"
      f"  Est. Total Comp: ~{total:.0f}"
    )

  context = '\n\n'.join(offers_text)

  if profile:
    context += f'\n\nCandidate Background:\n'
    context += f'Role: {profile.current_role or "N/A"}\n'
    context += f'Experience: {profile.years_experience or "N/A"} years\n'
    context += f'Location: {profile.location or "N/A"}\n'

  if prefs and prefs.salary_expectation:
    exp = prefs.salary_expectation
    context += f'\nSalary Expectation: {exp}\n'

  if user_weights:
    context += f'\nUser-defined weights: {json.dumps(user_weights)}\n'

  result = await call_agent(
    agent_name='offer-evaluator',
    system_prompt=OFFER_EVALUATOR_SYSTEM,
    user_message=f'Evaluate these job offers using the 7-dimension framework with full cognitive bias correction:\n\n{context}',
    tools=[OFFER_EVALUATION_TOOL],
    max_tokens=4096,
  )

  evaluation = result.get('tool_output')

  return {
    'offers_count': len(offers),
    'evaluation': evaluation or result.get('content'),
    'usage': result.get('usage'),
  }


def compute_pairwise_weights(comparisons: list[dict]) -> dict:
  """Compute dimension weights from pairwise comparisons.

  Args:
    comparisons: list of {dim_a, dim_b, winner} entries.
      e.g., [{'dim_a': 'salary_equity', 'dim_b': 'growth_potential', 'winner': 'salary_equity'}, ...]
  """
  dimensions = [
    'salary_equity', 'growth_potential', 'culture_team',
    'wlb_benefits', 'stability_risk', 'location_commute', 'brand_network',
  ]
  scores = {d: 0 for d in dimensions}

  if not comparisons:
    # Equal distribution when no pairwise data
    equal = round(100 / len(dimensions))
    weights = {d: equal for d in dimensions}
    diff = 100 - sum(weights.values())
    if diff:
      weights[dimensions[0]] += diff
    return weights

  for comp in comparisons:
    winner = comp.get('winner', '')
    if winner in scores:
      scores[winner] += 1

  total = sum(scores.values()) or 1
  weights = {d: round(s / total * 100) for d, s in scores.items()}

  # Ensure weights sum to 100
  diff = 100 - sum(weights.values())
  if diff != 0:
    max_dim = max(weights, key=weights.get)
    weights[max_dim] += diff

  return weights


async def trigger_loop_d(user_id: str, offer_data: dict) -> dict:
  """Trigger Feedback Loop D: actual offer data → preference calibration.

  When a user receives a real offer, use it to calibrate salary expectations
  and preferences for more accurate future searches.
  """
  async with async_session() as db:
    prefs_result = await db.execute(
      select(Preferences).where(Preferences.user_id == user_id)
    )
    prefs = prefs_result.scalar_one_or_none()

    if prefs and prefs.salary_expectation and offer_data.get('salary'):
      old_exp = prefs.salary_expectation
      if isinstance(old_exp, dict):
        new_exp = {
          **old_exp,
          'market_calibrated': True,
          'last_offer': {
            'company': offer_data.get('company', ''),
            'salary': offer_data.get('salary', 0),
            'total_comp': offer_data.get('total_comp', offer_data.get('salary', 0)),
          },
        }
        prefs.salary_expectation = new_exp

    # Create feedback event
    fb = FeedbackEvent(
      user_id=user_id,
      event_type='offer_received',
      phase=5,
      source_company=offer_data.get('company', ''),
      source_role=offer_data.get('role', ''),
      reason=f"Offer received: {offer_data.get('salary', 'N/A')}",
      lessons=[{
        'calibration': 'Salary expectations updated based on real offer data',
        'company': offer_data.get('company', ''),
        'salary': offer_data.get('salary', 0),
      }],
      status='processed',
    )
    db.add(fb)
    await db.commit()

  return {
    'loop': 'D',
    'description': 'Offer data → preference calibration',
    'action': 'salary_expectation updated with market calibration',
    'message': 'Future job searches will use market-calibrated expectations',
  }
