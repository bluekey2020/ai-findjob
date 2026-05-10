"""Test offer evaluation pairwise weights computation."""
import pytest
from app.services.offer_evaluation import compute_pairwise_weights


def test_weights_sum_to_100():
    comparisons = [
        {'dim_a': 'salary_equity', 'dim_b': 'growth_potential', 'winner': 'salary_equity'},
        {'dim_a': 'salary_equity', 'dim_b': 'culture_team', 'winner': 'salary_equity'},
        {'dim_a': 'growth_potential', 'dim_b': 'culture_team', 'winner': 'growth_potential'},
    ]
    weights = compute_pairwise_weights(comparisons)
    assert sum(weights.values()) == 100, f'Weights should sum to 100, got {sum(weights.values())}: {weights}'


def test_all_dimensions_present():
    weights = compute_pairwise_weights([])
    expected_dims = [
        'salary_equity', 'growth_potential', 'culture_team',
        'wlb_benefits', 'stability_risk', 'location_commute', 'brand_network',
    ]
    for dim in expected_dims:
        assert dim in weights, f'{dim} should be in weights'


def test_empty_comparisons_equal_weights():
    weights = compute_pairwise_weights([])
    values = list(weights.values())
    # All close to ~14% (100/7)
    for v in values:
        assert 10 <= v <= 20, f'Each weight should be ~14, got {v}'


def test_winner_gets_higher_weight():
    comparisons = [
        {'dim_a': 'salary_equity', 'dim_b': 'growth_potential', 'winner': 'salary_equity'},
        {'dim_a': 'salary_equity', 'dim_b': 'wlb_benefits', 'winner': 'salary_equity'},
        {'dim_a': 'salary_equity', 'dim_b': 'stability_risk', 'winner': 'salary_equity'},
    ]
    weights = compute_pairwise_weights(comparisons)
    assert weights['salary_equity'] > weights['growth_potential'], \
        f'Winner should have higher weight: {weights}'
