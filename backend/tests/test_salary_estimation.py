"""Test Zillow-style salary estimation model."""
import pytest
from app.services.market_analysis import estimate_salary


def test_basic_estimate():
    est = estimate_salary('python', 'Beijing', 5, 'large')
    assert est['estimate']['low'] > 0
    assert est['estimate']['mid'] > est['estimate']['low']
    assert est['estimate']['high'] > est['estimate']['mid']
    assert est['estimate']['currency'] == 'CNY'
    assert est['estimate']['period'] == 'annual'


def test_experience_increases_salary():
    junior = estimate_salary('python', 'Beijing', 1, 'mid')
    senior = estimate_salary('python', 'Beijing', 10, 'mid')
    assert senior['estimate']['mid'] > junior['estimate']['mid'], \
        'Senior salary should be higher than junior'


def test_tier1_city_premium():
    beijing = estimate_salary('python', 'Beijing', 3, 'mid')
    chengdu = estimate_salary('python', 'Chengdu', 3, 'mid')
    assert beijing['estimate']['mid'] > chengdu['estimate']['mid'], \
        f'Beijing ({beijing["estimate"]["mid"]}) should be higher than Chengdu ({chengdu["estimate"]["mid"]})'


def test_company_size_affects_salary():
    startup = estimate_salary('python', 'Beijing', 3, 'startup')
    bigco = estimate_salary('python', 'Beijing', 3, 'enterprise')
    assert bigco['estimate']['mid'] > startup['estimate']['mid'], \
        'Big company salary should exceed startup'


def test_skill_premium_adds_value():
    no_premium = estimate_salary('python', 'Beijing', 3, 'mid')
    with_premium = estimate_salary('python', 'Beijing', 3, 'mid', ['ai', 'kubernetes'])
    assert with_premium['estimate']['mid'] > no_premium['estimate']['mid'], \
        f'With premium {with_premium["estimate"]["mid"]} should exceed without {no_premium["estimate"]["mid"]}'
    assert len(with_premium['estimate']['factors']) > 0, 'Should list premium factors'


def test_confidence_depends_on_data():
    with_city = estimate_salary('python', 'Beijing')
    without_city = estimate_salary('python')
    assert with_city['estimate']['confidence'] >= without_city['estimate']['confidence']


def test_ai_role_premium():
    ai_eng = estimate_salary('ai_engineer', 'Beijing', 3, 'mid')
    py_dev = estimate_salary('python', 'Beijing', 3, 'mid')
    assert ai_eng['estimate']['mid'] > py_dev['estimate']['mid'], \
        f'AI engineer ({ai_eng["estimate"]["mid"]}) should earn more than Python dev ({py_dev["estimate"]["mid"]})'


def test_all_roles_return_valid():
    roles = ['frontend', 'backend', 'fullstack', 'devops', 'mobile', 'security', 'qa', 'sre']
    for role in roles:
        est = estimate_salary(role, 'Shanghai', 3, 'mid')
        assert est['estimate']['mid'] > 50000, f'{role} salary should be reasonable, got {est["estimate"]["mid"]}'
