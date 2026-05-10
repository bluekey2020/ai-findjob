from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix='/api/v1/offers', tags=['offers'])


@router.post('/evaluate')
async def evaluate_offers(
  offers: list[dict] = Body(..., description='List of offer objects to compare'),
  weights: dict | None = Body(None, description='Optional custom dimension weights'),
  current_user: User = Depends(get_current_user),
):
  """Multi-offer comparison with Daniel Kahneman cognitive bias correction (Opus)."""
  from app.services.offer_evaluation import evaluate_offers as _eval
  result = await _eval(current_user.id, offers, weights)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result


@router.post('/pairwise-weights')
async def compute_weights(
  comparisons: list[dict] = Body(..., description='List of {dim_a, dim_b, winner} pairwise comparisons'),
):
  """Compute dimension weights from pairwise comparisons (no LLM call)."""
  from app.services.offer_evaluation import compute_pairwise_weights
  return {'weights': compute_pairwise_weights(comparisons)}


@router.post('/calibrate')
async def calibrate_preferences(
  offer: dict = Body(..., description='Actual offer data for Loop D calibration'),
  current_user: User = Depends(get_current_user),
):
  """Trigger Loop D: calibrate salary expectations with real offer data."""
  from app.services.offer_evaluation import trigger_loop_d
  return await trigger_loop_d(current_user.id, offer)


@router.post('/negotiate')
async def negotiate(
  offer: dict = Body(..., description='Offer to negotiate'),
  market_data: dict | None = Body(None),
  batna: str = Body(''),
  current_user: User = Depends(get_current_user),
):
  """Generate Chris Voss FBI-style negotiation strategy (Opus)."""
  from app.services.salary_negotiation import generate_negotiation_strategy as _negotiate
  result = await _negotiate(offer, market_data, batna)
  if 'error' in result:
    raise HTTPException(status_code=400, detail=result['error'])
  return result
