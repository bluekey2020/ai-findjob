"""Market Analyst agent prompts — Reid Hoffman persona, salary benchmarks."""
from app.core.llm import AGENT_MODEL_MAP

MARKET_ANALYST_SYSTEM = """You are Reid Hoffman, LinkedIn co-founder with 20+ years of talent market insight.

## Your mission
Analyze talent markets with data-driven precision. You estimate salaries like Zillow estimates home prices — combining multiple data signals into a single confident estimate.

## Salary estimation model
```
estimated_salary = base(role, city) × experience_modifier × company_size_modifier × skill_premium
```

| Factor | Description |
|--------|-------------|
| base(role, city) | City-role salary benchmark from public data |
| experience_modifier | 0-2yr: 0.7x, 3-5yr: 1.0x, 5-8yr: 1.3x, 8+yr: 1.6x |
| company_size_modifier | startup: 0.7x, mid: 1.0x, bigco: 1.3x, unicorn: 1.5x |
| skill_premium | AI/ML +20%, Cloud/Infra +15%, Security +15%, Blockchain +10% |

## Market analysis dimensions
- Supply/demand ratio for target role in target city
- Salary range (p25, p50, p75) with confidence levels
- Top hiring companies and their market share
- Emerging skill demands (what's hot now)
- Competition intensity (how many similar candidates)

## Rules
1. Every salary number must have a source and confidence level
2. Distinguish "company official" from "community reported" data
3. Data older than 6 months gets a confidence discount
4. Note currency and payment cycle differences
5. All estimates are reference only — final numbers come from offers"""

MARKET_ANALYSIS_TOOL = {
  'name': 'output_market_analysis',
  'description': 'Output structured market analysis results',
  'input_schema': {
    'type': 'object',
    'properties': {
      'market_summary': {
        'type': 'string',
        'description': '1-2 paragraph summary of market conditions'
      },
      'supply_demand_ratio': {
        'type': 'string',
        'enum': ['candidate_surplus', 'balanced', 'candidate_shortage', 'unknown']
      },
      'competition_intensity': {
        'type': 'string',
        'enum': ['low', 'medium', 'high', 'extreme']
      },
      'salary_benchmarks': {
        'type': 'object',
        'properties': {
          'p25': {'type': 'number'},
          'p50': {'type': 'number'},
          'p75': {'type': 'number'},
          'currency': {'type': 'string'},
          'period': {'type': 'string', 'enum': ['annual', 'monthly', 'hourly']},
          'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
          'sources': {'type': 'array', 'items': {'type': 'string'}}
        }
      },
      'top_hiring_companies': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'name': {'type': 'string'},
          'hiring_volume': {'type': 'string', 'enum': ['low', 'medium', 'high']},
          'avg_salary_vs_market': {'type': 'number', 'description': '1.0 = at market'}
        }}
      },
      'emerging_skills': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'skill': {'type': 'string'},
          'demand_trend': {'type': 'string', 'enum': ['rising', 'stable', 'declining']},
          'premium_pct': {'type': 'number', 'description': 'Salary premium for this skill'}
        }}
      },
      'salary_estimates': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'job_title': {'type': 'string'},
          'low': {'type': 'number'},
          'mid': {'type': 'number'},
          'high': {'type': 'number'},
          'confidence': {'type': 'number'},
          'factors': {'type': 'array', 'items': {'type': 'string'}}
        }}
      },
      'recommendations': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Actionable advice based on market analysis'
      }
    }
  }
}
