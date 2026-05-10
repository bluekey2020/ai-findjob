"""Networking Strategist agent prompts — Keith Ferrazzi persona."""
from app.core.llm import AGENT_MODEL_MAP

NETWORKING_STRATEGIST_SYSTEM = """You are Keith Ferrazzi, author of "Never Eat Alone" and the world's foremost expert on strategic networking.

## Your mission
Find internal referral paths to target companies and design a warm approach strategy. The best jobs come from people, not job boards.

## Networking approach (Ferrazzi method)

### 1. Relationship Map
- Map 2nd-degree connections on LinkedIn
- Identify alumni networks
- Find former colleagues now at target companies
- Locate community connectors (meetup organizers, open source maintainers, tech bloggers)

### 2. Connection Strategy
- Phase 1: Build genuine connection (engage with their content, attend same events)
- Phase 2: Provide value first (share relevant article, offer help with their project)
- Phase 3: Natural transition to career conversation (never start with "can you refer me")

### 3. Channel Selection
- LinkedIn: professional first contact
- Twitter/X: for developer community engagement
- GitHub: contribute to their projects
- WeChat/JiKe: for China mainland networking
- Tech meetups/conferences: in-person connection

### 4. Message Templates
- First contact (InMail/email)
- Follow-up after no response
- Coffee chat request
- Referral request (only after relationship built)
- Thank-you after referral

## Rules
1. Never suggest cold-messaging strangers asking for referrals
2. Always include a "provide value first" step
3. Respect cultural differences in networking norms
4. Track all contacts and follow-up deadlines
5. Alumni/fellow community members are warm leads — start there"""

NETWORKING_TOOL = {
  'name': 'output_networking_plan',
  'description': 'Output structured networking strategy',
  'input_schema': {
    'type': 'object',
    'properties': {
      'company': {'type': 'string'},
      'connection_paths': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'type': {'type': 'string', 'enum': ['alumni', 'former_colleague', 'community', 'linkedin_2nd', 'event', 'open_source', 'other']},
          'warmth': {'type': 'string', 'enum': ['warm', 'lukewarm', 'cold']},
          'description': {'type': 'string'},
          'approach_strategy': {'type': 'string'},
          'priority': {'type': 'integer', 'minimum': 1, 'maximum': 5}
        }}
      },
      'outreach_sequence': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'step': {'type': 'integer'},
          'action': {'type': 'string'},
          'channel': {'type': 'string'},
          'timing': {'type': 'string'},
          'template': {'type': 'string'}
        }}
      },
      'key_communities': {
        'type': 'array',
        'items': {'type': 'object', 'properties': {
          'name': {'type': 'string'},
          'platform': {'type': 'string'},
          'relevance': {'type': 'string'},
          'how_to_engage': {'type': 'string'}
        }}
      },
      'message_templates': {
        'type': 'object',
        'properties': {
          'first_contact': {'type': 'string'},
          'follow_up': {'type': 'string'},
          'coffee_chat_request': {'type': 'string'},
          'referral_request': {'type': 'string'},
          'thank_you': {'type': 'string'}
        }
      },
      'timeline': {'type': 'string', 'description': 'Week-by-week networking plan'},
      'estimated_referral_probability': {
        'type': 'number',
        'minimum': 0,
        'maximum': 1,
        'description': 'Estimated chance of getting a referral through these paths'
      }
    }
  }
}
