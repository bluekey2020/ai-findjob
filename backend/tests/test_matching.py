"""Test bidirectional matching algorithm."""
import pytest
from datetime import date, timedelta
from app.services.job_search import _compute_bidirectional_match


def _make_context(skill_names=None, skill_levels=None, prefs=None):
    """Build a mock context object for matching."""
    class MockSkill:
        def __init__(self, name, level='intermediate', years=3):
            self.name = name
            self.level = level
            self.years = years

    class MockProfile:
        skills = [MockSkill(n, skill_levels[n] if skill_levels and n in skill_levels else 'intermediate',
                           3) for n in (skill_names or [])]

    class MockPrefs:
        salary_expectation = prefs.get('salary_expectation', 0) if prefs else 0
        target_locations = prefs.get('target_locations', []) if prefs else []
        company_size_preference = prefs.get('company_size_preference', '') if prefs else ''
        dealbreakers = prefs.get('dealbreakers', []) if prefs else []

    return {
        'profile': MockProfile(),
        'prefs': MockPrefs(),
        'skills': {s.name.lower(): s for s in MockProfile.skills},
    }


def test_perfect_skill_match():
    context = _make_context(['python', 'fastapi', 'postgresql', 'docker', 'aws'])
    job = {
        'title': 'Python Developer',
        'requirements': ['python', 'fastapi', 'postgresql', 'docker'],
        'company': 'TechCo',
        'location': 'Beijing',
        'salary_range': '30K-50K',
        'source_type': 'official',
        'posted_date': date.today().isoformat(),
    }
    result = _compute_bidirectional_match(job, context)
    assert result['bidirectional_score'] > 50
    assert result['match_breakdown']['jd_match'] > 70
    assert len(result['match_reasons']) >= 3


def test_partial_skill_match():
    context = _make_context(['python', 'javascript'])
    job = {
        'title': 'Full Stack Developer',
        'requirements': ['python', 'javascript', 'react', 'docker', 'kubernetes'],
        'company': 'StartupCo',
        'location': 'Shanghai',
        'salary_range': '25K-45K',
        'source_type': 'official',
        'posted_date': date.today().isoformat(),
    }
    result = _compute_bidirectional_match(job, context)
    assert result['bidirectional_score'] < 70
    assert len(result['missing_skills']) >= 1


def test_no_skills_match():
    context = _make_context(['java', 'spring'])
    job = {
        'title': 'Python Developer',
        'requirements': ['python', 'fastapi', 'django'],
        'company': 'PythonCo',
        'location': 'Beijing',
        'salary_range': '30K-50K',
        'source_type': 'official',
        'posted_date': date.today().isoformat(),
    }
    result = _compute_bidirectional_match(job, context)
    assert result['match_breakdown']['jd_match'] < 30


def test_location_preference_matches():
    context = _make_context(
        ['python'],
        prefs={'target_locations': ['Beijing', 'Shanghai']}
    )
    job = {
        'title': 'Python Dev',
        'requirements': ['python'],
        'company': 'BeijingCo',
        'location': 'Beijing, China',
        'salary_range': '30K-50K',
        'source_type': 'official',
        'posted_date': date.today().isoformat(),
    }
    result = _compute_bidirectional_match(job, context)
    assert result['match_breakdown']['preference_match'] > 50


def test_dealbreaker_penalizes():
    context = _make_context(
        ['python'],
        prefs={'dealbreakers': ['996', 'overtime']}
    )
    job = {
        'title': 'Python Dev',
        'requirements': ['python'],
        'description': 'Must be willing to work 996 schedule',
        'company': 'SweatShop',
        'location': 'Beijing',
        'salary_range': '40K-60K',
        'source_type': 'official',
        'posted_date': date.today().isoformat(),
    }
    result = _compute_bidirectional_match(job, context)
    assert result['match_breakdown']['preference_match'] < 50, \
        f'Dealbreaker should reduce pref match, got {result["match_breakdown"]["preference_match"]}'


def test_old_job_loses_freshness():
    context = _make_context(['python'])
    old_job = {
        'title': 'Python Dev',
        'requirements': ['python'],
        'company': 'OldCo',
        'location': 'Beijing',
        'salary_range': '30K-50K',
        'source_type': 'official',
        'posted_date': (date.today() - timedelta(days=60)).isoformat(),
    }
    fresh_job = {
        'title': 'Python Dev',
        'requirements': ['python'],
        'company': 'NewCo',
        'location': 'Beijing',
        'salary_range': '30K-50K',
        'source_type': 'official',
        'posted_date': date.today().isoformat(),
    }
    old_result = _compute_bidirectional_match(old_job, context)
    fresh_result = _compute_bidirectional_match(fresh_job, context)
    assert fresh_result['match_breakdown']['freshness'] > old_result['match_breakdown']['freshness']


def test_fraud_score_affects_health():
    context = _make_context(['python'])
    clean_job = {
        'title': 'Python Dev',
        'requirements': ['python'],
        'company': 'CleanCo',
        'location': 'Beijing',
        'salary_range': '30K-50K',
        'source_type': 'official',
        'posted_date': date.today().isoformat(),
        'fraud_score': 0,
    }
    fraud_job = {
        'title': 'Python Dev',
        'requirements': ['python'],
        'company': 'SusCo',
        'location': 'Beijing',
        'salary_range': '30K-50K',
        'source_type': 'third_party',
        'posted_date': date.today().isoformat(),
        'fraud_score': 50,
    }
    clean_result = _compute_bidirectional_match(clean_job, context)
    fraud_result = _compute_bidirectional_match(fraud_job, context)
    assert clean_result['match_breakdown']['company_health'] > fraud_result['match_breakdown']['company_health']
