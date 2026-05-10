"""Anthropic SDK integration layer — model routing, prompt caching, structured output."""
import json
import hashlib
from functools import lru_cache
from anthropic import Anthropic, AsyncAnthropic

from app.core.config import settings

# Model routing table — maps agent roles to model IDs
AGENT_MODEL_MAP: dict[str, str] = {
  # Strategic layer → Opus
  'career-coach': 'claude-opus-4-20250514',
  'market-analyst': 'claude-opus-4-20250514',
  'offer-evaluator': 'claude-opus-4-20250514',
  'salary-negotiator': 'claude-opus-4-20250514',
  'interview-coach': 'claude-opus-4-20250514',

  # Execution layer → Sonnet
  'profile-analyst': 'claude-sonnet-4-20250514',
  'resume-architect': 'claude-sonnet-4-20250514',
  'company-researcher': 'claude-sonnet-4-20250514',
  'hr-intel': 'claude-sonnet-4-20250514',
  'cover-letter-writer': 'claude-sonnet-4-20250514',
  'networking-strategist': 'claude-sonnet-4-20250514',
  'skill-advisor': 'claude-sonnet-4-20250514',

  # High-frequency → Haiku
  'job-scout': 'claude-haiku-4-20250514',
}

AGENT_TOKEN_COSTS: dict[str, float] = {
  'job-scout': 0.01,
  'company-researcher': 0.05,
  'hr-intel': 0.05,
  'networking-strategist': 0.05,
  'profile-analyst': 0.08,
  'resume-architect': 0.08,
  'cover-letter-writer': 0.05,
  'skill-advisor': 0.05,
  'market-analyst': 0.15,
  'interview-coach': 0.12,
  'offer-evaluator': 0.15,
  'salary-negotiator': 0.12,
}


def get_model_for_agent(agent_name: str) -> str:
  return AGENT_MODEL_MAP.get(agent_name, 'claude-sonnet-4-20250514')


@lru_cache(maxsize=1)
def get_async_client() -> AsyncAnthropic:
  return AsyncAnthropic(api_key=settings.anthropic_api_key or None)


def compute_input_hash(*args) -> str:
  """Compute a hash of inputs for checkpoint/dedup purposes."""
  content = json.dumps(args, sort_keys=True, default=str)
  return hashlib.sha256(content.encode()).hexdigest()[:16]


def make_cached_block(data: str) -> dict:
  """Create a prompt-cacheable content block for frequently reused data."""
  return {
    'type': 'text',
    'text': data,
    'cache_control': {'type': 'ephemeral'}
  }


async def call_agent(
  agent_name: str,
  system_prompt: str,
  user_message: str,
  tools: list[dict] | None = None,
  cached_context: str | None = None,
  max_tokens: int = 4096,
) -> dict:
  """
  Main LLM call entry point.

  Args:
    agent_name: maps to model via AGENT_MODEL_MAP
    system_prompt: agent's system instructions
    user_message: the task description
    tools: optional tool_use definitions for structured output
    cached_context: optional large data block to cache (e.g., user profile)
    max_tokens: response token limit

  Returns:
    dict with keys: content (str), tool_output (dict|None), usage (dict)
  """
  client = get_async_client()
  model = get_model_for_agent(agent_name)

  system_blocks = [{'type': 'text', 'text': system_prompt}]
  if cached_context:
    system_blocks.append(make_cached_block(cached_context))

  kwargs = {
    'model': model,
    'max_tokens': max_tokens,
    'system': system_blocks,
    'messages': [{'role': 'user', 'content': user_message}],
  }
  if tools:
    kwargs['tools'] = tools
    kwargs['tool_choice'] = {'type': 'auto'}

  response = await client.messages.create(**kwargs)

  content = ''
  tool_output = None
  for block in response.content:
    if block.type == 'text':
      content += block.text
    elif block.type == 'tool_use':
      tool_output = block.input

  return {
    'content': content,
    'tool_output': tool_output,
    'usage': {
      'input_tokens': response.usage.input_tokens,
      'output_tokens': response.usage.output_tokens,
      'model': model,
    },
  }
