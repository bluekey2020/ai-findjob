"""Test Phase state machine logic."""
import pytest
from app.engine.state_machine import (
    PhaseDefinition, PHASES, get_phase_info,
)


def test_all_phases_defined():
    assert len(PHASES) == 6, f'Expected 6 phases, got {len(PHASES)}'


def test_phase_numbers_sequential():
    for i, phase in enumerate(PHASES):
        assert phase.number == i, f'Phase {i} has number {phase.number}'


def test_phase_0_no_requirements():
    p0 = PHASES[0]
    assert p0.number == 0
    assert len(p0.requires) == 0, 'Phase 0 should have no requirements'


def test_phase_1_requires_preferences():
    p1 = PHASES[1]
    assert 'preferences' in p1.requires


def test_phase_2_requires_profile():
    p2 = PHASES[2]
    assert 'profile' in p2.requires
    assert 'preferences' in p2.requires


def test_phase_3_requires_jobs():
    p3 = PHASES[3]
    assert 'jobs' in p3.requires


def test_phase_4_requires_applications():
    p4 = PHASES[4]
    assert 'applications' in p4.requires


def test_phase_5_requires_applications():
    p5 = PHASES[5]
    assert 'applications' in p5.requires


def test_get_phase_info_valid():
    for i in range(6):
        pd = get_phase_info(i)
        assert pd is not None
        assert pd.number == i
        assert pd.name


def test_get_phase_info_invalid():
    pd = get_phase_info(99)
    assert pd is None


def test_get_phase_info_negative():
    pd = get_phase_info(-1)
    assert pd is None


def test_each_phase_has_agents():
    for phase in PHASES:
        assert len(phase.agents) > 0, f'Phase {phase.number} needs agents'
        assert all(isinstance(a, str) for a in phase.agents)


def test_each_phase_has_description():
    for phase in PHASES:
        assert phase.description, f'Phase {phase.number} needs description'
        assert phase.gate_description, f'Phase {phase.number} needs gate description'
