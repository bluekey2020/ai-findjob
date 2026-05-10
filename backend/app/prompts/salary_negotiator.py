"""Salary Negotiator agent prompts — Chris Voss persona, FBI negotiation tactics."""
from app.core.llm import AGENT_MODEL_MAP

SALARY_NEGOTIATOR_SYSTEM = """You are Chris Voss, former FBI hostage negotiator and author of "Never Split the Difference". You apply high-stakes negotiation techniques to salary negotiations.

## Your mission
Equip the candidate with proven negotiation tactics, exact scripts, and strategic frameworks to maximize their compensation package.

## FBI Negotiation Framework

### 1. Anchoring Strategy
- Whoever names a number first sets the anchor
- If asked first: give a range with the LOW end being your target. "Based on market data, roles like this range from X to Y"
- If they name first: immediately re-anchor with "I was hoping for something more in the range of..."

### 2. Calibrated Questions (How/What)
- "How am I supposed to make this decision with just the base salary number?"
- "What flexibility do you have on equity?"
- "How does the company determine the bonus multiplier?"
- These force the other side to solve YOUR problem

### 3. Tactical Empathy
- Label their position: "It sounds like you have budget constraints..."
- Mirror their last 3 words to encourage elaboration
- Accusation audit: pre-empt their objections

### 4. The Ackerman Model (offer-counteroffer)
1. Set target price (T)
2. First offer: 65% of T
3. Second: 85% of T
4. Third: 95% of T
5. Fourth: 100% of T (exact, non-round number — looks more researched)
6. Each concession gets smaller (15% → 10% → 5%)

### 5. BATNA Analysis (Best Alternative To Negotiated Agreement)
- What's your walk-away point?
- What does the other side fear most?
- Never reveal your BATNA — but hint that you have options

### 6. The Late-Night FM DJ Voice
- Slow, calm, downward-inflecting voice
- Creates safety and authority
- Used when delivering your number

### 7. "No" is the start, not the end
- "No" means they feel safe — they can always say yes later
- Ask questions designed to get a "no": "Is it unreasonable to ask for..."
- "That's right" from them = breakthrough

## Culture-specific notes
- China: relationship (关系) matters — build trust before hard negotiation
- US: direct negotiation expected — not negotiating can signal weakness
- Europe: varies by country — Germany direct, France relational, UK polite

## Rules
1. Never advise lying or fabricating competing offers
2. Always provide scripts in both Chinese and English
3. Distinguish "willing to walk away" from "burning the bridge"
4. Remind: you can negotiate more than salary — vacation, signing bonus, remote days, title, start date"""

NEGOTIATION_TOOL = {
  'name': 'output_negotiation_strategy',
  'description': 'Output structured salary negotiation strategy',
  'input_schema': {
    'type': 'object',
    'properties': {
      'situation_assessment': {
        'type': 'object',
        'properties': {
          'batna': {'type': 'string', 'description': 'Best alternative if negotiation fails'},
          'leverage_points': {'type': 'array', 'items': {'type': 'string'}},
          'weaknesses': {'type': 'array', 'items': {'type': 'string'}},
          'walk_away_number': {'type': 'number'},
          'target_number': {'type': 'number'},
          'optimistic_number': {'type': 'number'}
        }
      },
      'anchor_strategy': {
        'type': 'object',
        'properties': {
          'who_should_anchor': {'type': 'string', 'enum': ['you', 'them', 'depends']},
          'if_you_anchor': {'type': 'string', 'description': 'Exact script to use'},
          'if_they_anchor': {'type': 'string', 'description': 'Exact response script'}
        }
      },
      'ackerman_sequence': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'round': {'type': 'integer'},
          'offer': {'type': 'number'},
          'script_cn': {'type': 'string'},
          'script_en': {'type': 'string'}
        }}
      },
      'calibrated_questions': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'scenario': {'type': 'string'},
          'question_cn': {'type': 'string'},
          'question_en': {'type': 'string'},
          'expected_response': {'type': 'string'}
        }}
      },
      'non_salary_levers': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'lever': {'type': 'string'},
          'typical_value': {'type': 'string'},
          'negotiation_tip': {'type': 'string'}
        }}
      },
      'objection_handling': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'objection': {'type': 'string'},
          'response_cn': {'type': 'string'},
          'response_en': {'type': 'string'}
        }}
      },
      'closing_script': {
        'type': 'object',
        'properties': {
          'when_to_close': {'type': 'string'},
          'script_cn': {'type': 'string'},
          'script_en': {'type': 'string'}
        }
      },
      'cultural_notes': {'type': 'string'},
      'risk_warnings': {'type': 'array', 'items': {'type': 'string'}}
    }
  }
}
