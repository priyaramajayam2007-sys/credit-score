import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scoring import SCORE_MAX, SCORE_MIN, score_from_inputs, validate_inputs


def test_score_stays_in_range():
    res = score_from_inputs([30000] * 6, [3000] * 6, platforms=2, tenure_months=12)
    assert SCORE_MIN <= res["score"] <= SCORE_MAX


def test_steady_income_beats_volatile_income():
    steady = score_from_inputs([30000] * 6, [3000] * 6, 2, 12)
    volatile = score_from_inputs([5000, 60000, 8000, 55000, 6000, 52000], [3000] * 6, 2, 12)
    assert steady["score"] > volatile["score"]


def test_more_savings_gives_higher_score():
    low = score_from_inputs([30000] * 6, [300] * 6, 2, 12)
    high = score_from_inputs([30000] * 6, [6000] * 6, 2, 12)
    assert high["score"] > low["score"]


def test_longer_history_and_more_platforms_help():
    new = score_from_inputs([30000] * 6, [3000] * 6, 1, 3)
    experienced = score_from_inputs([30000] * 6, [3000] * 6, 3, 30)
    assert experienced["score"] > new["score"]


def test_zero_income_does_not_crash():
    res = score_from_inputs([0] * 6, [0] * 6, 1, 1)
    assert SCORE_MIN <= res["score"] <= SCORE_MAX


def test_validation_catches_bad_input():
    assert validate_inputs([1000, 2000], [1500, 100])      # savings > income
    assert validate_inputs([-5, 2000], [0, 0])             # negative income
    assert validate_inputs([0, 0], [0, 0])                 # no income at all
    assert validate_inputs([1000, 2000], [100, 200]) == []  # valid
