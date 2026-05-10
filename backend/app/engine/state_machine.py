"""Phase state machine — 6-phase pipeline with gating and feedback loops."""
from dataclasses import dataclass
from typing import Callable, Awaitable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.profile import Profile
from app.models.preferences import Preferences
from app.models.job import Job
from app.models.company import Company
from app.models.tracking import DashboardSnapshot


@dataclass
class PhaseDefinition:
  number: int
  name: str
  description: str
  requires: list[str]       # entity names that must exist
  gate_description: str     # human-readable gate condition
  agents: list[str]         # agents that run in this phase


PHASES: list[PhaseDefinition] = [
  PhaseDefinition(0, '入职引导', '智能推断偏好，确认关键约束',
    [], '用户确认求职偏好',
    ['career-coach']),
  PhaseDefinition(1, '画像构建', '解析简历材料，生成结构化画像和默认简历',
    ['preferences'], '完成结构化画像 + 默认简历 + 技能缺口分析',
    ['profile-analyst', 'skill-advisor', 'resume-architect']),
  PhaseDefinition(2, '市场调研与职位发现', '搜索职位、调研公司、分析市场行情',
    ['profile', 'preferences'], '发现至少5个职位 + 公司调研完成',
    ['market-analyst', 'job-scout', 'company-researcher', 'hr-intel']),
  PhaseDefinition(3, '批量定制投递', '为每个目标岗位定制简历和求职信',
    ['jobs'], '至少生成1份定制简历和求职信',
    ['resume-architect', 'cover-letter-writer', 'networking-strategist']),
  PhaseDefinition(4, '面试准备', '公司专项面试训练和模拟',
    ['applications'], '用户标记进入面试阶段',
    ['interview-coach', 'company-researcher', 'salary-negotiator']),
  PhaseDefinition(5, 'Offer 决策', '多Offer对比和薪资谈判',
    ['applications'], '收到Offer后',
    ['offer-evaluator', 'salary-negotiator']),
]


async def get_current_phase(db: AsyncSession, user_id: str) -> int:
  result = await db.execute(
    select(DashboardSnapshot)
    .where(DashboardSnapshot.user_id == user_id)
    .order_by(DashboardSnapshot.snapshot_date.desc())
    .limit(1)
  )
  snap = result.scalar_one_or_none()
  return snap.current_phase if snap else 0


async def set_phase(db: AsyncSession, user_id: str, phase: int):
  snap = DashboardSnapshot(user_id=user_id, current_phase=phase)
  db.add(snap)
  await db.flush()


def get_phase_info(phase_num: int) -> PhaseDefinition | None:
  for p in PHASES:
    if p.number == phase_num:
      return p
  return None


async def check_phase_requirements(db: AsyncSession, user_id: str, phase_num: int) -> tuple[bool, list[str]]:
  """Check if requirements for entering a phase are met. Returns (met, missing)."""
  pd = get_phase_info(phase_num)
  if not pd:
    return False, ['Invalid phase']

  missing = []
  for req in pd.requires:
    if req == 'preferences':
      r = await db.execute(select(Preferences).where(Preferences.user_id == user_id))
      if not r.scalar_one_or_none():
        missing.append('preferences — 请先完成求职偏好设置')
    elif req == 'profile':
      r = await db.execute(select(Profile).where(Profile.user_id == user_id))
      if not r.scalar_one_or_none():
        missing.append('profile — 请先完成个人画像')
    elif req == 'jobs':
      r = await db.execute(select(Job).where(Job.user_id == user_id))
      if not r.scalars().first():
        missing.append('jobs — 请先搜索职位')
    elif req == 'applications':
      from app.models.application import Application
      r = await db.execute(select(Application).where(Application.user_id == user_id))
      if not r.scalars().first():
        missing.append('applications — 还没有投递记录')

  return len(missing) == 0, missing


async def can_advance(db: AsyncSession, user_id: str) -> tuple[bool, str, int]:
  """Check if user can advance to next phase. Returns (can_advance, reason, current_phase)."""
  current = await get_current_phase(db, user_id)

  if current >= 5:
    return False, '已完成所有阶段', current

  met, missing = await check_phase_requirements(db, user_id, current)
  if not met:
    pd = get_phase_info(current)
    return False, f'Phase {current} ({pd.name}) 未完成: {"; ".join(missing)}', current

  return True, '', current


async def advance_phase(db: AsyncSession, user_id: str) -> dict:
  """Advance to next phase. Returns status info."""
  ok, reason, current = await can_advance(db, user_id)
  if not ok:
    return {'success': False, 'current_phase': current, 'reason': reason}

  new_phase = current + 1
  await set_phase(db, user_id, new_phase)

  pd = get_phase_info(new_phase)
  return {
    'success': True,
    'previous_phase': current,
    'current_phase': new_phase,
    'phase_name': pd.name if pd else 'Unknown',
    'agents': pd.agents if pd else [],
    'gate': pd.gate_description if pd else '',
  }


async def get_feedback_loop_status(db: AsyncSession, user_id: str) -> dict:
  """Query which feedback loops are active and their state."""
  from app.models.tracking import FeedbackEvent

  result = await db.execute(
    select(FeedbackEvent)
    .where(FeedbackEvent.user_id == user_id)
    .order_by(FeedbackEvent.created_at.desc())
    .limit(30)
  )
  events = result.scalars().all()

  loops = {'A': False, 'B': False, 'C': False, 'D': False}
  for e in events:
    if e.status == 'pending':
      if e.event_type == 'interview_feedback':
        loops['A'] = True
      elif e.event_type == 'application_rejected':
        loops['B'] = True
      elif e.event_type == 'offer_received':
        loops['D'] = True

  # Loop C is active whenever Phase 3 is running
  phase = await get_current_phase(db, user_id)
  loops['C'] = (phase == 3)

  return {
    'active_loops': [k for k, v in loops.items() if v],
    'loop_details': {
      'A': '面试反馈 → 技能缺口更新',
      'B': '被拒分析 → 画像优化',
      'C': '简历 ↔ 求职信 双向通信',
      'D': 'Offer数据 → 偏好校准',
    },
    'total_events': len(events),
    'pending_events': sum(1 for e in events if e.status == 'pending'),
  }
