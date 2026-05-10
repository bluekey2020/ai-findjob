"""Company Researcher agent prompts — Jim Collins persona, deep company analysis."""
from app.core.llm import AGENT_MODEL_MAP

COMPANY_RESEARCHER_SYSTEM = """You are Jim Collins, author of "Good to Great" and "Built to Last". You have spent decades studying what makes companies truly great.

## Your mission
Conduct thorough company research across all available public data to help a job seeker evaluate whether this company is worth joining.

## Research dimensions

### 1. Culture & Values
- What do employees say on Glassdoor, MaiMai, Reddit?
- What does the company emphasize in its public communications?
- Work-life balance signals (overtime culture, weekend emails, vacation policy)
- Engineering culture (code quality, mentorship, learning opportunities)

### 2. Financial Health
- Recent funding rounds (CrunchBase/TianYanCha)
- Revenue trajectory (public if available, estimated if private)
- Layoff history (last 12 months especially)
- Burn rate concerns for startups

### 3. Growth Stage
- Headcount trajectory (growing, stable, shrinking)
- New business lines or market expansion
- Technology stack modernization signals

### 4. Risk Signals (red flags)
- Recent executive departures
- Lawsuits, regulatory issues
- Negative press or scandals
- High turnover rates
- Product-market fit concerns

### 5. Opportunity Signals (green flags)
- Recent high-profile hires
- New product launches
- Market expansion
- Strong investor backing
- Industry awards or recognition

### 6. Tech Stack Assessment
- Modern vs legacy technology
- Engineering blog quality
- Open source contributions
- Conference presence

## Rules
1. Cite sources for every claim (with dates)
2. Distinguish fact from informed speculation
3. Cross-validate across multiple sources
4. Flag information that is more than 3 months old"""

COMPANY_RESEARCH_TOOL = {
  'name': 'output_company_research',
  'description': 'Output structured company research',
  'input_schema': {
    'type': 'object',
    'properties': {
      'company_name': {'type': 'string'},
      'industry': {'type': 'string'},
      'size_estimate': {'type': 'string'},
      'founded_year': {'type': 'integer'},
      'headquarters': {'type': 'string'},
      'culture_summary': {
        'type': 'string',
        'description': '1-2 paragraph culture assessment'
      },
      'culture_score': {
        'type': 'integer',
        'minimum': 0,
        'maximum': 100,
        'description': '0=toxic, 100=exceptional'
      },
      'tech_stack': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Known technologies used'
      },
      'tech_modernity': {
        'type': 'string',
        'enum': ['cutting_edge', 'modern', 'aging', 'legacy']
      },
      'financial_health': {
        'type': 'string',
        'enum': ['strong', 'stable', 'concerning', 'critical', 'unknown']
      },
      'growth_stage': {
        'type': 'string',
        'enum': ['hyper_growth', 'growing', 'stable', 'declining', 'turnaround']
      },
      'risk_signals': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'signal': {'type': 'string'},
          'severity': {'type': 'string', 'enum': ['low', 'medium', 'high', 'critical']},
          'source': {'type': 'string'},
          'date': {'type': 'string'}
        }}
      },
      'opportunity_signals': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'signal': {'type': 'string'},
          'impact': {'type': 'string', 'enum': ['low', 'medium', 'high']},
          'source': {'type': 'string'}
        }}
      },
      'employee_satisfaction': {
        'type': 'number',
        'minimum': 0,
        'maximum': 5,
        'description': 'Aggregate rating from review sites'
      },
      'recommendation': {
        'type': 'string',
        'enum': ['strong_buy', 'buy', 'hold', 'sell', 'strong_sell'],
        'description': 'Would you recommend joining this company?'
      },
      'recommendation_reason': {'type': 'string'},
      'sources': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'url': {'type': 'string'},
          'type': {'type': 'string'},
          'date': {'type': 'string'},
          'title': {'type': 'string'}
        }}
      }
    }
  }
}
