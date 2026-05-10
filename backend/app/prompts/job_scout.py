"""Job Scout agent prompts — JD parsing, fraud detection, job matching."""
from app.core.llm import AGENT_MODEL_MAP

JOB_SCOUT_SYSTEM = """You are Nick Corcodilos, author of "Ask The Headhunter". You excel at finding hidden jobs and seeing through fake job postings.

## Your approach
1. Parse job descriptions with surgical precision — extract what the role actually does, not the HR fluff
2. Detect ghost jobs (perpetually reposted), fake jobs (too good to be true), and bait-and-switch postings
3. Map requirements to real skills, not buzzwords
4. Flag dealbreakers immediately (unpaid trial periods, resume harvesting, multi-level marketing)

## Fraud detection framework
- Ghost job: same role reposted 30+ days, vague requirements, company with hiring freeze
- Fake job: asks for payment, no company address, personal email contact, salary way off market
- Low quality: missing salary, generic description, clearly a staffing agency fishing
- Trust signals: specific tech stack, named team, clear responsibilities, company email domain

## Output always in JSON via the tool provided."""

JD_PARSE_TOOL = {
  'name': 'parse_job_description',
  'description': 'Extract structured job data from a raw job description',
  'input_schema': {
    'type': 'object',
    'properties': {
      'title': {'type': 'string', 'description': 'Normalized job title'},
      'company': {'type': 'string'},
      'location': {'type': 'string'},
      'salary_range': {'type': 'string'},
      'description': {'type': 'string', 'description': 'Cleaned description'},
      'requirements': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Extracted skill/experience requirements'
      },
      'preferred': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Nice-to-have qualifications'
      },
      'tech_stack': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Technologies mentioned'
      },
      'seniority_level': {
        'type': 'string',
        'enum': ['intern', 'junior', 'mid', 'senior', 'staff', 'principal', 'cto']
      },
      'employment_type': {
        'type': 'string',
        'enum': ['full-time', 'part-time', 'contract', 'freelance', 'internship']
      },
      'remote_policy': {
        'type': 'string',
        'enum': ['onsite', 'hybrid', 'remote', 'unknown']
      },
      'industry': {'type': 'string'},
      'company_size_estimate': {
        'type': 'string',
        'enum': ['startup', 'small', 'mid', 'large', 'enterprise', 'unknown']
      },
      'fraud_flags': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'flag': {'type': 'string'},
          'severity': {'type': 'string', 'enum': ['low', 'medium', 'high']},
          'reason': {'type': 'string'}
        }},
        'description': 'Detected fraud/ghost-job indicators'
      },
      'fraud_score': {
        'type': 'integer',
        'minimum': 0,
        'maximum': 100,
        'description': '0=clean, 100=definite fraud'
      },
      'quality_score': {
        'type': 'integer',
        'minimum': 0,
        'maximum': 100,
        'description': 'JD quality: clarity, specificity, detail'
      },
      'dealbreaker_flags': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Items matching user dealbreakers'
      },
      'keywords': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Key search terms for matching'
      },
      'source_credibility': {
        'type': 'string',
        'enum': ['official', 'community', 'third_party', 'unknown']
      }
    },
    'required': ['title', 'requirements', 'fraud_score'],
  }
}

BATCH_PARSE_TOOL = {
  'name': 'parse_job_batch',
  'description': 'Parse multiple job descriptions in one pass',
  'input_schema': {
    'type': 'object',
    'properties': {
      'jobs': {
        'type': 'array',
        'items': JD_PARSE_TOOL['input_schema'],
        'minItems': 1,
        'maxItems': 10
      }
    },
    'required': ['jobs']
  }
}
