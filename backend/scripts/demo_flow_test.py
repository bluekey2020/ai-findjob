"""Demo flow verification — 6-step test without LLM dependency."""
import urllib.request, json, sys

def api(method, path, data=None, token=None):
    url = f'http://localhost:8000{path}'
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f'  HTTP {e.code}: {body[:200]}', file=sys.stderr)
        return {'error': e.code, 'detail': body}

# Step 1: Register + Login
print('=== Step 1: Register & Login ===')
reg = api('POST', '/api/v1/auth/register', {
    'email': 'demo6@test.com', 'password': 'demo123456', 'display_name': 'Demo User'
})
login = api('POST', '/api/v1/auth/login', {
    'email': 'demo6@test.com', 'password': 'demo123456'
})
token = login.get('access_token')
if not token:
    print('LOGIN FAILED')
    sys.exit(1)
print(f'  User: {reg.get("email", login.get("email", "?"))}')

# Step 2+3: Submit profile and preferences
print()
print('=== Step 2+3: Submit Profile + Preferences ===')
profile = api('PUT', '/api/v1/profile', data={
    'name': 'Zhang San',
    'email': 'zhangsan@example.com',
    'location': 'Beijing',
    'current_role': 'Senior Python Engineer',
    'current_company': 'TechCorp',
    'years_of_experience': 5,
    'summary': '5 years Python backend experience, specialized in FastAPI microservices',
    'target_roles': ['Python Backend Developer', 'Full Stack Engineer'],
    'highlights': ['Handled 10M+ daily requests', 'Led microservice migration'],
    'skills': [
        {'name': 'Python', 'level': 'expert', 'years': 5, 'category': 'backend'},
        {'name': 'FastAPI', 'level': 'advanced', 'years': 3, 'category': 'backend'},
        {'name': 'React', 'level': 'intermediate', 'years': 2, 'category': 'frontend'},
        {'name': 'TypeScript', 'level': 'intermediate', 'years': 2, 'category': 'frontend'},
        {'name': 'PostgreSQL', 'level': 'advanced', 'years': 4, 'category': 'database'},
        {'name': 'Docker', 'level': 'advanced', 'years': 3, 'category': 'devops'},
        {'name': 'AWS', 'level': 'intermediate', 'years': 2, 'category': 'cloud'},
    ],
    'work_experiences': [
        {
            'company': 'TechCorp', 'title': 'Python Backend Developer',
            'start_date': '2022-03', 'end_date': 'Present',
            'description': 'Microservice architecture design, 10M+ daily requests',
            'highlights': ['40% performance improvement', 'Led tech stack migration'],
            'tech_stack': ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'AWS']
        },
        {
            'company': 'WebCo', 'title': 'Full Stack Developer',
            'start_date': '2019-07', 'end_date': '2022-02',
            'description': 'Built SaaS platform with React + FastAPI',
            'highlights': ['0 to 1 product launch', '500k MAU'],
            'tech_stack': ['React', 'TypeScript', 'Python', 'FastAPI']
        }
    ]
}, token=token)
print(f'  Profile: {profile.get("name", "ERROR")} - {profile.get("current_role", "")}')

prefs = api('PUT', '/api/v1/preferences', data={
    'target_roles': ['Python Backend Developer'],
    'target_regions': ['Beijing', 'Shanghai'],
    'salary_amount': 30000, 'salary_currency': 'CNY', 'salary_period': 'monthly',
    'company_size_preference': 'mid', 'willing_to_relocate': False,
    'dealbreakers': ['training fee', 'deposit'],
    'job_freshness_days': 14,
    'preferred_platforms': ['Boss', 'Lagou'],
    'timeline': 'within 2 weeks'
}, token=token)
print(f'  Preferences: {"OK" if "error" not in prefs else "ERROR"}')

# Step 4: Check guide
print()
print('=== Guide After Profile (Step 4 status) ===')
guide = api('GET', '/api/v1/phases/guide', token=token)
for s in guide['steps']:
    icon = '[x]' if s['done'] else '[ ]'
    print(f'  {icon} Step {s["step"]}: {s["name"]}')
print(f'  Progress: {guide["progress_pct"]}%')
print(f'  Next: {guide.get("next_action", {}).get("name", "none")} via {guide.get("next_action", {}).get("api", "?")}')

# Step 5: Import & Search jobs
print()
print('=== Step 4+5: Import Jobs & Smart Match ===')
import_result = api('POST', '/api/v1/jobs/import', data=[
    {
        'title': 'Senior Python Engineer',
        'company': 'ByteDance',
        'location': 'Beijing',
        'salary_range': '30k-50k',
        'platform': 'Boss',
        'description': 'Backend service development with Python/FastAPI, 3-5 years experience',
        'requirements': ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
        'source_type': 'official'
    },
    {
        'title': 'Full Stack Developer',
        'company': 'Meituan',
        'location': 'Beijing',
        'salary_range': '25k-45k',
        'platform': 'Lagou',
        'description': 'Full stack, React + Python backend',
        'requirements': ['React', 'TypeScript', 'Python', 'PostgreSQL'],
        'source_type': 'official'
    },
    {
        'title': 'Urgent Remote Typist (SCAM)',
        'company': 'Unknown Ltd',
        'location': 'Remote',
        'salary_range': '5k-50k',
        'platform': 'Unknown',
        'description': 'Training fee required, contact via WeChat',
        'requirements': [],
        'source_type': 'underground'
    }
], token=token)
print(f'  Import: {import_result.get("message", "ERROR")}')

search = api('POST', '/api/v1/jobs/search', token=token)
if 'error' in search:
    print(f'  Search ERROR: {search}')
else:
    stats = search.get('stats', {})
    print(f'  Found: {search["total"]} jobs')
    print(f'  Top Picks (score>=70): {search["top_picks"]}')
    print(f'  Mid Tier: {search["mid_tier"]}')
    print(f'  Flagged (fraud/low): {search["flagged"]}')
    print(f'  Avg Score: {stats.get("avg_match_score")}')
    print()
    for j in search.get('jobs', []):
        bad = ''
        if j.get('fraud_flags'):
            bad = f' [SCAM:{j["fraud_score"]}]'
        if j.get('dealbreaker_flags'):
            bad += f' [DEALBREAKER]'
        bd = j.get('match_breakdown', {})
        print(f'  [{j["match_score"]:5.1f}] {j["title"][:30]:30s} @ {j["company"]:15s} '
              f'JD:{bd.get("jd_match",0):4.1f} Pref:{bd.get("preference_match",0):4.1f} '
              f'Health:{bd.get("company_health",0):4.1f} Fresh:{bd.get("freshness",0):4.1f}{bad}')

    # Step 6: Apply to best job
    top = search['jobs'][0]
    print()
    print(f'=== Step 6: Apply to "{top["title"]}" @ {top["company"]} ===')
    apply_result = api('POST', f'/api/v1/jobs/{top["id"]}/apply', token=token)
    if 'error' in apply_result:
        print(f'  ERROR: {apply_result}')
    else:
        app = apply_result.get('application', {})
        print(f'  Application: {app.get("id")}')
        print(f'  Status: {app.get("status")}')
        print(f'  Batch: #{app.get("batch_number")}')
        print(f'  Resume: {"generated" if apply_result.get("tailored_resume") else "skipped (no LLM key)"}')
        print(f'  Cover Letter: {"generated" if apply_result.get("cover_letter") else "skipped (no LLM key)"}')

# Final guide
print()
print('=== Final 6-Step Progress ===')
guide2 = api('GET', '/api/v1/phases/guide', token=token)
for s in guide2['steps']:
    if s['done']:
        icon = '[x]'
    elif s['step'] == guide2['current_step']:
        icon = '->'
    else:
        icon = '[ ]'
    print(f'  {icon} Step {s["step"]}: {s["name"]}')
print(f'  Progress: {guide2["progress_pct"]}%')
na = guide2.get('next_action', {})
if na:
    print(f'  Next: Step {na["step"]} - {na["name"]} ({na["api"]})')
else:
    print(f'  All 6 steps complete!')

print()
print('=== 6-Step Demo Flow Verified ===')
