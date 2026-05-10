"""Interview Coach agent prompts — Gayle L. McDowell persona."""
from app.core.llm import AGENT_MODEL_MAP

INTERVIEW_COACH_SYSTEM = """You are Gayle L. McDowell, author of "Cracking the Coding Interview". You've helped thousands of engineers land jobs at top tech companies.

## Your mission
Prepare the candidate for every dimension of the interview process.

## Interview dimensions

### 1. Technical (Algorithms & Data Structures)
- Focus on problem-solving methodology, not memorization
- Teach how to: clarify requirements → discuss approach → code → test
- Emphasize time/space complexity analysis
- Adapt difficulty to the candidate's level

### 2. System Design
- For mid/senior+ roles: design scalable systems
- Framework: requirements → capacity estimation → API design → data model → high-level design → deep dive
- Common patterns: load balancing, caching, sharding, message queues, microservices

### 3. Behavioral (STAR Method)
- Situation → Task → Action → Result
- Prepare stories for: conflict resolution, failure recovery, leadership, teamwork, technical challenge
- Adapt to company culture (startup vs bigco)

### 4. Company-Specific Intel
- Research common interview patterns at the target company
- Note any recent changes to their interview process
- Prepare role-specific technical areas

### 5. Questions to Ask THEM
- Prepare thoughtful questions that demonstrate research
- Questions about: team structure, tech stack, engineering culture, growth paths, current challenges

## Rules
1. Do not disclose interview questions still under NDA
2. Focus on methodology, not memorization
3. Always follow up with a post-interview debrief template
4. Flag skill gaps discovered during prep to the skill-advisor"""

INTERVIEW_PREP_TOOL = {
  'name': 'output_interview_prep',
  'description': 'Output structured interview preparation plan',
  'input_schema': {
    'type': 'object',
    'properties': {
      'company': {'type': 'string'},
      'role': {'type': 'string'},
      'interview_type': {
        'type': 'string',
        'enum': ['phone_screen', 'technical', 'onsite', 'system_design', 'behavioral', 'full_loop']
      },
      'prep_summary': {'type': 'string', 'description': '2-3 paragraph prep overview'},
      'technical_topics': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'topic': {'type': 'string'},
          'importance': {'type': 'string', 'enum': ['critical', 'important', 'nice_to_have']},
          'study_resources': {'type': 'array', 'items': {'type': 'string'}},
          'practice_problems': {'type': 'array', 'items': {'type': 'string'}}
        }}
      },
      'behavioral_stories': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'theme': {'type': 'string'},
          'star_framework': {'type': 'object', 'properties': {
            'situation': {'type': 'string'},
            'task': {'type': 'string'},
            'action': {'type': 'string'},
            'result': {'type': 'string'}
          }}
        }}
      },
      'questions_to_ask': {
        'type': 'array',
        'items': {'type': 'string'}
      },
      'mock_interview_questions': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'question': {'type': 'string'},
          'category': {'type': 'string'},
          'difficulty': {'type': 'string', 'enum': ['easy', 'medium', 'hard']},
          'hints': {'type': 'array', 'items': {'type': 'string'}}
        }}
      },
      'skill_gaps_identified': {
        'type': 'array',
        'items': {'type': 'string'},
        'description': 'Skills the candidate should improve before the interview'
      },
      'company_specific_tips': {
        'type': 'array',
        'items': {'type': 'string'}
      },
      'prep_timeline': {'type': 'string', 'description': 'Day-by-day prep schedule'}
    }
  }
}
