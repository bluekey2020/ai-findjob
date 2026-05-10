"""Test fraud detection heuristics — no LLM calls needed."""
import pytest
from app.services.job_search import compute_fraud_score


def test_clean_job_passes():
    score, flags, dealbreakers = compute_fraud_score({
        'description': 'We are looking for a Python developer with 3+ years experience in Django and FastAPI.',
        'title': 'Senior Python Developer',
        'requirements': ['Python', 'Django', 'FastAPI', 'PostgreSQL'],
        'salary_range': '30K-50K',
        'source_credibility': 'official',
    })
    assert score < 20, f'Clean job should have low fraud score, got {score}'
    assert len(dealbreakers) == 0


def test_payment_scam_detected():
    score, flags, dealbreakers = compute_fraud_score({
        'description': 'Looking for developers. Training fee of 5000 required before starting.',
        'title': 'Python Developer',
        'requirements': [],
        'salary_range': '50K-100K',
        'source_credibility': 'third_party',
    })
    assert any('training fee' in db.lower() for db in dealbreakers), \
        f'Should detect training fee dealbreaker, got {dealbreakers}'
    assert score > 20


def test_vague_job_flagged():
    score, flags, dealbreakers = compute_fraud_score({
        'description': 'We are hiring multiple positions. Looking for talented people to join our team.',
        'title': 'Various Positions',
        'requirements': [],
        'salary_range': '',
        'source_credibility': 'third_party',
    })
    assert any('vague' in f.lower() for f in flags), f'Should flag vague job, got {flags}'


def test_third_party_source_flagged():
    score, flags, dealbreakers = compute_fraud_score({
        'description': 'Great opportunity for a software engineer with 3 years experience.',
        'title': 'Software Engineer',
        'requirements': ['Python', 'JavaScript'],
        'salary_range': '25K-40K',
        'source_credibility': 'third_party',
    })
    assert any('third-party' in f.lower() for f in flags), \
        f'Should flag third-party source, got {flags}'


def test_wide_salary_range_flagged():
    score, flags, dealbreakers = compute_fraud_score({
        'description': 'Hiring a senior engineer with cloud experience.',
        'title': 'Senior Engineer',
        'requirements': ['AWS', 'Kubernetes', 'Python'],
        'salary_range': '20K-80K',  # 4x ratio
        'source_credibility': 'official',
    })
    assert score > 10 or any('salary' in f.lower() for f in flags), \
        f'Wide salary range should be suspicious, got score={score}, flags={flags}'


def test_fraud_score_max_100():
    score, _, _ = compute_fraud_score({
        'description': 'training fee deposit registration fee processing fee',
        'title': 'Developer',
        'requirements': [],
        'salary_range': '5K-100K',
        'source_credibility': 'third_party',
    })
    assert score <= 100, f'Fraud score should not exceed 100, got {score}'


def test_dealbreaker_triggers_high_score():
    score, _, dealbreakers = compute_fraud_score({
        'description': 'Pay a training fee to start. Contact on WeChat: xxx.',
        'title': 'Developer',
        'requirements': [],
        'salary_range': '',
        'source_credibility': 'third_party',
    })
    assert len(dealbreakers) > 0
    assert score > 30
