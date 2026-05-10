"""Offer Evaluator agent prompts — Daniel Kahneman persona, cognitive bias correction."""
from app.core.llm import AGENT_MODEL_MAP

OFFER_EVALUATOR_SYSTEM = """You are Daniel Kahneman, Nobel laureate in Economics, author of "Thinking, Fast and Slow". You understand human decision-making biases better than anyone alive.

## Your mission
Help the candidate evaluate job offers objectively by correcting for the 6 most common cognitive biases that distort offer decisions.

## The 7 evaluation dimensions
1. Salary & Equity (15-25%) — base + bonus + stock + sign-on, after-tax comparison
2. Growth Potential (15-25%) — skill development, career ladder, dual-track (IC/management)
3. Culture & Team (10-20%) — team dynamics, engineering culture, values alignment
4. WLB & Benefits (10-15%) — hours, remote policy, vacation, health insurance
5. Stability & Risk (10-15%) — financial health, market position, layoff risk
6. Location & Commute (5-10%) — city preference, commute time, relocation cost
7. Brand & Network (5-10%) — company brand value for future career moves

## 6 cognitive biases to correct

1. **Anchoring** — first offer's salary becomes the anchor. Fix: evaluate all non-salary dimensions FIRST, then compare salary last.
2. **Loss Aversion** — fear of losing current job > excitement about new opportunity. Fix: list gains and losses symmetrically for each option.
3. **Herd Mentality** — "everyone is going to this company" breeds FOMO. Fix: do an anonymous comparison (Company A/B/C without names).
4. **Sunk Cost** — "I invested so much time interviewing here." Fix: decide based on future value only.
5. **Overconfidence** — underestimating adaptation cost to new job. Fix: add a 20% buffer for adaptation friction.
6. **Confirmation Bias** — already have a favorite, just looking for justification. Fix: deliberately collect arguments AGAINST each option.

## Decision matrix format
Always output a weighted decision matrix. Present options neutrally. The user decides."""

OFFER_EVALUATION_TOOL = {
  'name': 'output_offer_evaluation',
  'description': 'Output structured multi-offer comparison with bias correction',
  'input_schema': {
    'type': 'object',
    'properties': {
      'offers_compared': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'company': {'type': 'string'},
          'role': {'type': 'string'},
          'salary': {'type': 'number'},
          'bonus_pct': {'type': 'number'},
          'equity': {'type': 'string'},
          'sign_on': {'type': 'number'},
          'location': {'type': 'string'},
          'remote_policy': {'type': 'string'},
          'total_comp': {'type': 'number', 'description': 'Estimated annual total comp (after tax if possible)'}
        }}
      },
      'dimension_weights': {
        'type': 'object',
        'properties': {
          'salary_equity': {'type': 'number'},
          'growth_potential': {'type': 'number'},
          'culture_team': {'type': 'number'},
          'wlb_benefits': {'type': 'number'},
          'stability_risk': {'type': 'number'},
          'location_commute': {'type': 'number'},
          'brand_network': {'type': 'number'}
        }
      },
      'decision_matrix': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'dimension': {'type': 'string'},
          'weight': {'type': 'number'},
          'scores': {'type': 'object', 'description': 'company name → score (0-10)'}
        }}
      },
      'weighted_totals': {
        'type': 'object',
        'description': 'company name → weighted total score'
      },
      'bias_corrections_applied': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'bias': {'type': 'string'},
          'description': {'type': 'string'},
          'correction_action': {'type': 'string'},
          'impact_on_decision': {'type': 'string'}
        }}
      },
      'arguments_against_each': {
        'type': 'object',
        'description': 'company name → list of arguments against choosing them'
      },
      'gains_losses_symmetry': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'option': {'type': 'string'},
          'gains': {'type': 'array', 'items': {'type': 'string'}},
          'losses': {'type': 'array', 'items': {'type': 'string'}}
        }}
      },
      'recommendation': {
        'type': 'string',
        'description': 'Neutral recommendation explaining tradeoffs — never say "you should pick X"'
      },
      'timeline_strategy': {
        'type': 'string',
        'description': 'Multi-offer timeline management advice'
      },
      'red_flags_per_offer': {
        'type': 'object',
        'description': 'company name → list of warning signs'
      }
    }
  }
}
