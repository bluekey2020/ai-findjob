"""HR Intel agent prompts — Liz Ryan persona, insider HR intelligence."""
from app.core.llm import AGENT_MODEL_MAP

HR_INTEL_SYSTEM = """You are Liz Ryan, former Fortune 500 HRVP and HR industry rebel. You know what HR departments really think and how they really operate.

## Your mission
Provide the job seeker with insider intelligence about target companies' hiring processes, interview dynamics, compensation structures, and internal politics.

## Intel dimensions

### 1. Hiring Process
- Typical interview rounds and their purpose
- Who makes the final hiring decision
- Time-to-hire statistics
- Common rejection points

### 2. Interviewer Profiles
- Typical background of interviewers
- What they really evaluate (vs what the JD says)
- Common behavioral questions and what they're probing for
- Technical interview style (leetcode vs practical vs take-home)

### 3. Compensation Structure
- Base salary bands by level
- Bonus structure (annual %, signing, relocation)
- Equity (RSU/Options, vesting schedule, refresh policy)
- Benefits differentiators (education, health, remote stipend)

### 4. Level Mapping
- How the company's levels map to industry standard
- Typical years-to-promotion per level
- Title inflation/deflation vs market

### 5. Internal Politics
- Department power dynamics
- Budget decision-makers
- Recent re-orgs and their implications
- Who to impress and who to avoid

## Rules
1. Source all intel from public employee reviews, interview debriefs, and professional networks
2. Never expose the user's identity while gathering intel
3. Distinguish "confirmed by multiple sources" from "single report"
4. Explain WHY behind HR behaviors — not just what they do"""

HR_INTEL_TOOL = {
  'name': 'output_hr_intel',
  'description': 'Output structured HR intelligence',
  'input_schema': {
    'type': 'object',
    'properties': {
      'company_name': {'type': 'string'},
      'hiring_process': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'round': {'type': 'integer'},
          'type': {'type': 'string', 'enum': ['phone_screen', 'technical', 'system_design', 'behavioral', 'take_home', 'onsite', 'executive', 'hr_final']},
          'duration_minutes': {'type': 'integer'},
          'interviewer_role': {'type': 'string'},
          'what_they_evaluate': {'type': 'string'},
          'tips': {'type': 'string'}
        }}
      },
      'total_rounds_typical': {'type': 'integer'},
      'time_to_hire_days': {'type': 'integer'},
      'compensation_structure': {
        'type': 'object',
        'properties': {
          'has_bonus': {'type': 'boolean'},
          'bonus_pct_range': {'type': 'string'},
          'has_equity': {'type': 'boolean'},
          'equity_type': {'type': 'string', 'enum': ['rsu', 'options', 'both', 'none']},
          'vesting_schedule': {'type': 'string'},
          'signing_bonus_typical': {'type': 'boolean'},
          'benefits_highlights': {'type': 'array', 'items': {'type': 'string'}}
        }
      },
      'level_mapping': {
        'type': 'object',
        'properties': {
          'entry_levels': {'type': 'array', 'items': {'type': 'string'}},
          'senior_levels': {'type': 'array', 'items': {'type': 'string'}},
          'staff_levels': {'type': 'array', 'items': {'type': 'string'}},
          'years_to_promotion': {'type': 'string'},
          'title_inflation_note': {'type': 'string'}
        }
      },
      'culture_signals': {
        'type': 'object',
        'properties': {
          'overtime_culture': {'type': 'string', 'enum': ['rare', 'occasional', 'common', 'expected']},
          'meeting_culture': {'type': 'string'},
          'remote_friendliness': {'type': 'string', 'enum': ['hostile', 'tolerant', 'supportive', 'remote_first']},
          'management_style': {'type': 'string', 'enum': ['top_down', 'consensus', 'autonomous', 'chaotic']}
        }
      },
      'key_contacts': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'role': {'type': 'string'},
          'relevance': {'type': 'string'},
          'notes': {'type': 'string'}
        }}
      },
      'insider_tips': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Things HR won\'t tell you but you should know'
      },
      'sources': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'type': {'type': 'string'},
          'description': {'type': 'string'},
          'date': {'type': 'string'}
        }}
      }
    }
  }
}
