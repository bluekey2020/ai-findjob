#!/usr/bin/env python3
"""Data layer for AI Job Hunter. Read, write, validate, and render entities.

Usage:
  python scripts/data-layer.py read <entity>
  python scripts/data-layer.py write <entity> [json_string]
  python scripts/data-layer.py validate <entity>
  python scripts/data-layer.py view <entity>

Entities: profile, preferences, jobs, companies, applications, dashboard, feedback
Output paths: docs/data/<entity>.json, docs/views/<entity>.md
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Windows 终端 UTF-8 编码修复
if sys.platform == 'win32':
  sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'docs' / 'data'
VIEW_DIR = ROOT / 'docs' / 'views'
SCHEMA_DIR = DATA_DIR / 'schemas'

ENTITIES = ['profile', 'preferences', 'jobs', 'companies', 'applications', 'dashboard', 'feedback']

# ── helpers ──────────────────────────────────────────

def data_path(entity): return DATA_DIR / f'{entity}.json'
def schema_path(entity): return SCHEMA_DIR / f'{entity}.schema.json'
def view_path(entity): return VIEW_DIR / f'{entity}.md'

def load_json(path):
  with open(path, 'r', encoding='utf-8') as f:
    return json.load(f)

def save_json(path, data):
  with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

def log(msg): print(msg, file=sys.stderr)

# ── read ─────────────────────────────────────────────

def cmd_read(entity):
  path = data_path(entity)
  if not path.exists():
    log(f'Error: {path} does not exist')
    sys.exit(1)
  data = load_json(path)
  print(json.dumps(data, ensure_ascii=False, indent=2))

# ── write ────────────────────────────────────────────

def cmd_write(entity, json_str):
  if not json_str:
    # read from stdin
    json_str = sys.stdin.read()
  try:
    data = json.loads(json_str)
  except json.JSONDecodeError as e:
    log(f'Error: invalid JSON: {e}')
    sys.exit(1)

  path = data_path(entity)
  # update metadata
  if 'metadata' in data:
    data['metadata']['updated_at'] = datetime.now().isoformat()
  elif isinstance(data, list):
    pass  # no metadata for root arrays

  save_json(path, data)
  log(f'OK: wrote {path}')

# ── validate ─────────────────────────────────────────

def validate_type(value, type_spec, path='$'):
  """Simple structural validation. type_spec is a str, dict, or composite type string."""
  errors = []

  # ── dict-based nested spec (e.g. {'name': 'str', 'email': 'str'}) ──
  if isinstance(type_spec, dict):
    if not isinstance(value, dict):
      errors.append(f'{path}: expected object, got {type(value).__name__}')
    else:
      for sub_field, sub_spec in type_spec.items():
        if sub_field in value and value[sub_field] is not None:
          errors += validate_type(value[sub_field], sub_spec, f'{path}.{sub_field}')
    return errors

  # ── string-based type specs ──
  if not isinstance(type_spec, str):
    return errors  # skip unknown specs

  # Handle composite type strings like list<{...}> or list<str>
  if type_spec.startswith('list<'):
    if not isinstance(value, list):
      errors.append(f'{path}: expected list, got {type(value).__name__}')
    else:
      inner = type_spec[5:-1]  # strip list<...>
      if isinstance(inner, str) and inner.startswith('{'):
        # list<{key:type,...}> — validate each item against the object spec
        # We can't easily parse the inner object spec from a string, so skip deep validation
        pass
    return errors

  # Strip enum hints (e.g. "str:startup|mid|large|any" -> treat as "str")
  base_type = type_spec.split(':')[0] if ':' in type_spec else type_spec

  if base_type == 'str':
    if not isinstance(value, str):
      errors.append(f'{path}: expected str, got {type(value).__name__}')
  elif base_type == 'int':
    if not isinstance(value, int) or isinstance(value, bool):
      errors.append(f'{path}: expected int, got {type(value).__name__}')
  elif base_type == 'bool':
    if not isinstance(value, bool):
      errors.append(f'{path}: expected bool, got {type(value).__name__}')

  return errors


def validate_entity(entity):
  """Validate a data entity against its schema (if exists)."""
  data_path_ = data_path(entity)
  schema_path_ = schema_path(entity)

  if not data_path_.exists():
    log(f'Error: {data_path_} does not exist')
    return False

  data = load_json(data_path_)

  if not schema_path_.exists():
    log(f'Warning: no schema found for {entity}, skipping validation')
    return True

  schema = load_json(schema_path_)
  errors = []

  # Get the entity-specific schema definition
  entity_schema = schema.get(entity, schema)
  required_fields = entity_schema.get('required_fields', [])
  fields = entity_schema.get('fields', {})

  # Check required fields
  for field in required_fields:
    parts = field.split('.')
    current = data
    for part in parts:
      if not isinstance(current, dict) or part not in current:
        errors.append(f'Missing required field: {field}')
        break
      current = current[part]

  # Check field-level types
  for field, type_spec in fields.items():
    if field in data and data[field] is not None:
      errors += validate_type(data[field], type_spec, field)

  if errors:
    log(f'Validation failed for {entity}:')
    for err in errors:
      log(f'  - {err}')
    return False
  else:
    log(f'OK: {entity} is valid')
    return True

def cmd_validate(entity):
  ok = validate_entity(entity)
  sys.exit(0 if ok else 1)

# ── view ─────────────────────────────────────────────

def view_profile(data):
  lines = ['# 用户结构化画像', '']
  basics = data.get('basics', {})
  if basics.get('name'):
    lines.append(f"**姓名:** {basics['name']}")
  if basics.get('email'):
    lines.append(f"**邮箱:** {basics['email']}")
  if basics.get('location') or basics.get('city'):
    loc = f"{basics.get('city','')} {basics.get('location','')}".strip()
    lines.append(f"**所在地:** {loc}")
  lines.append('')

  if data.get('summary'):
    lines.append('## 自我介绍')
    lines.append('')
    lines.append(data['summary'])
    lines.append('')

  skills = data.get('skills', [])
  if skills:
    lines.append('## 技能')
    lines.append('')
    lines.append('| 技能 | 水平 | 年限 | 类别 |')
    lines.append('|------|------|------|------|')
    for s in skills:
      lines.append(f"| {s.get('name','')} | {s.get('level','')} | {s.get('years','')} | {s.get('category','')} |")
    lines.append('')

  work = data.get('work_experience', [])
  if work:
    lines.append('## 工作经历')
    lines.append('')
    for w in work:
      dates = f"{w.get('start_date','')} — {w.get('end_date','')}"
      lines.append(f"### {w.get('title','')} @ {w.get('company','')}")
      lines.append(f"*{dates}*")
      lines.append('')
      if w.get('description'):
        lines.append(w['description'])
        lines.append('')
    lines.append('')

  meta = data.get('metadata', {})
  if meta.get('updated_at'):
    lines.append(f"*最后更新: {meta['updated_at']}*")

  return '\n'.join(lines)

def view_preferences(data):
  lines = ['# 求职偏好', '']
  lines.append(f"- **语言:** {data.get('language', 'zh-CN')}")
  roles = data.get('target_roles', [])
  lines.append(f"- **目标岗位:** {', '.join(roles) if roles else '未设置'}")
  regions = data.get('target_regions', [])
  lines.append(f"- **目标地区:** {', '.join(regions) if regions else '未设置'}")

  salary = data.get('salary_expectation', {})
  if salary.get('amount'):
    lines.append(f"- **薪资期望:** {salary['amount']} {salary.get('currency','CNY')}/{salary.get('period','monthly')}")

  lines.append(f"- **愿意 relocate:** {'是' if data.get('willing_to_relocate') else '否'}")
  lines.append(f"- **公司规模偏好:** {data.get('company_size_preference', 'any')}")
  lines.append(f"- **时效过滤:** {data.get('job_freshness_days', 14)} 天内")
  dreams = data.get('dream_companies', [])
  lines.append(f"- **梦司:** {', '.join(dreams) if dreams else '未设置'}")

  meta = data.get('metadata', {})
  if meta.get('updated_at'):
    lines.append('')
    lines.append(f"*最后更新: {meta['updated_at']}*")

  return '\n'.join(lines)

def view_jobs(data):
  lines = ['# 职位列表', '']
  jobs = data.get('jobs', [])
  top = set(data.get('top_picks', []))
  lines.append(f'**总计:** {len(jobs)} 个职位')
  lines.append('')

  for j in jobs:
    star = '★ ' if j.get('id') in top else ''
    lines.append(f"## {star}{j.get('title','')} @ {j.get('company','')}")
    lines.append('')
    lines.append(f"- **地点:** {j.get('location','')} ({j.get('region','')})")
    lines.append(f"- **平台:** {j.get('platform','')}")
    if j.get('salary_range'):
      lines.append(f"- **薪资:** {j.get('salary_range')}")
    lines.append(f"- **状态:** {j.get('status','new')}")
    if j.get('url'):
      lines.append(f"- **链接:** {j.get('url')}")
    if j.get('description'):
      lines.append(f"- **描述:** {j['description'][:200]}")
    lines.append('')

  return '\n'.join(lines)

def view_companies(data):
  lines = ['# 公司研究', '']
  companies = data.get('companies', [])
  lines.append(f'**总计:** {len(companies)} 家公司')
  lines.append('')

  for c in companies:
    lines.append(f"## {c.get('name','')}")
    lines.append('')
    lines.append(f"- **行业:** {c.get('industry','')}")
    lines.append(f"- **规模:** {c.get('size','')}")
    lines.append(f"- **财务健康:** {c.get('financial_health','unknown')}")
    if c.get('culture_summary'):
      lines.append(f"- **文化:** {c['culture_summary']}")
    risks = c.get('risk_signals', [])
    if risks:
      lines.append(f"- **风险信号:** {', '.join(risks)}")
    lines.append('')

  return '\n'.join(lines)

def view_applications(data):
  lines = ['# 投递追踪', '']
  apps = data.get('applications', [])
  stats = data.get('stats', {})
  lines.append(f"**总计:** {stats.get('total',len(apps))} | "
               f"已投: {stats.get('applied',0)} | "
               f"面试中: {stats.get('interviewing',0)} | "
               f"Offer: {stats.get('offered',0)}")
  lines.append('')
  lines.append('| 公司 | 岗位 | 状态 | 投递日期 | 下一步 |')
  lines.append('|------|------|------|----------|--------|')
  for a in apps:
    lines.append(f"| {a.get('company','')} | {a.get('role','')} | {a.get('status','')} | "
                 f"{a.get('applied_date','')} | {a.get('next_step','')} |")
  lines.append('')

  return '\n'.join(lines)

def view_feedback(data):
  lines = ['# 反馈日志', '']
  events = data.get('events', [])
  stats = data.get('stats', {})
  lines.append(f"**总事件:** {stats.get('total_events', 0)} | "
               f"已应用改进: {stats.get('applied_improvements', 0)}")
  lines.append('')
  if events:
    lines.append('| 时间 | 类型 | 公司 | 岗位 | 原因 | 状态 |')
    lines.append('|------|------|------|------|------|------|')
    for e in events[-30:]:
      lines.append(f"| {e.get('timestamp','')} | {e.get('type','')} | {e.get('source_company','')} | "
                   f"{e.get('source_role','')} | {e.get('reason','')[:40]} | {e.get('status','')} |")
    lines.append('')
  return '\n'.join(lines)

def view_dashboard(data):
  lines = ['# 求职进度仪表盘', '']
  stats = data.get('stats', {})
  funnel = data.get('funnel', {})

  lines.append('## 总览')
  lines.append('')
  lines.append(f"- **当前阶段:** Phase {stats.get('current_phase','0')}")
  lines.append(f"- **活跃天数:** {stats.get('days_active',0)}")
  lines.append(f"- **平均匹配度:** {stats.get('avg_match_score',0)}/100")
  lines.append('')

  lines.append('## 漏斗')
  lines.append('')
  stages = ['discovered', 'screened', 'shortlisted', 'applied', 'phone_screen',
            'technical', 'onsite', 'offer', 'accepted']
  labels = ['发现', '粗筛', '精选', '已投递', '电话面试', '技术面', '现场面', 'Offer', '已接受']
  max_val = max(funnel.values()) if funnel else 1

  for stage, label in zip(stages, labels):
    count = funnel.get(stage, 0)
    bar = '█' * (count * 20 // max_val) if max_val > 0 else ''
    lines.append(f"**{label}:** {count} {bar}")
  lines.append('')

  timeline = data.get('timeline', [])
  if timeline:
    lines.append('## 时间线')
    lines.append('')
    lines.append('| 日期 | 事件 | 公司 | 岗位 | 详情 |')
    lines.append('|------|------|------|------|------|')
    for t in timeline[-20:]:  # 最近 20 条
      lines.append(f"| {t.get('date','')} | {t.get('event','')} | {t.get('company','')} | "
                   f"{t.get('role','')} | {t.get('detail','')} |")
    lines.append('')

  recent = data.get('recent_activity', [])
  if recent:
    lines.append('## 最近动态')
    lines.append('')
    for r in recent[-10:]:
      lines.append(f"- [{r.get('timestamp','')}] {r.get('action','')} — {r.get('description','')}")
    lines.append('')

  return '\n'.join(lines)

VIEW_FUNCTIONS = {
  'profile': view_profile,
  'preferences': view_preferences,
  'jobs': view_jobs,
  'companies': view_companies,
  'applications': view_applications,
  'dashboard': view_dashboard,
  'feedback': view_feedback,
}

def cmd_view(entity):
  data_path_ = data_path(entity)
  if not data_path_.exists():
    log(f'Error: {data_path_} does not exist')
    sys.exit(1)

  data = load_json(data_path_)
  view_fn = VIEW_FUNCTIONS.get(entity)
  if not view_fn:
    log(f'Error: no view function for {entity}')
    sys.exit(1)

  md = view_fn(data)

  # ensure views directory exists
  VIEW_DIR.mkdir(parents=True, exist_ok=True)

  out_path = view_path(entity)
  with open(out_path, 'w', encoding='utf-8') as f:
    f.write(md)

  log(f'OK: view written to {out_path}')
  print(md)

# ── main ─────────────────────────────────────────────

def usage():
  log('Usage: python scripts/data-layer.py <read|write|validate|view> <entity> [json_string]')
  log(f'Entities: {", ".join(ENTITIES)}')
  sys.exit(1)

def main():
  if len(sys.argv) < 2:
    usage()

  cmd = sys.argv[1]

  if cmd not in ('read', 'write', 'validate', 'view'):
    log(f'Error: unknown command "{cmd}"')
    usage()

  if cmd == 'read':
    if len(sys.argv) < 3: usage()
    cmd_read(sys.argv[2])

  elif cmd == 'write':
    if len(sys.argv) < 3: usage()
    json_str = sys.argv[3] if len(sys.argv) > 3 else None
    cmd_write(sys.argv[2], json_str)

  elif cmd == 'validate':
    if len(sys.argv) < 3: usage()
    cmd_validate(sys.argv[2])

  elif cmd == 'view':
    if len(sys.argv) < 3: usage()
    cmd_view(sys.argv[2])

if __name__ == '__main__':
  main()
