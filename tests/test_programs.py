"""Unit tests for app.programs business logic."""
import pytest

from app.programs import PROGRAMS, estimate_calories


def test_programs_catalog_has_three_entries():
    assert set(PROGRAMS.keys()) == {"FL", "MG", "BG"}


@pytest.mark.parametrize(
    "key,expected_factor",
    [("FL", 22), ("MG", 35), ("BG", 26)],
)
def test_program_calorie_factors(key, expected_factor):
    assert PROGRAMS[key]["calorie_factor"] == expected_factor


def test_each_program_has_required_fields():
    required = {"key", "name", "workout", "diet", "color", "calorie_factor"}
    for program in PROGRAMS.values():
        assert required.issubset(program.keys())


def test_estimate_calories_muscle_gain():
    # 80 kg * 35 = 2800
    assert estimate_calories(80, "MG") == 2800


def test_estimate_calories_fat_loss():
    # 70 kg * 22 = 1540
    assert estimate_calories(70, "FL") == 1540


def test_estimate_calories_truncates_to_int():
    # 70.5 * 26 = 1833.0  -> int() -> 1833
    assert estimate_calories(70.5, "BG") == 1833


def test_estimate_calories_rejects_non_positive_weight():
    with pytest.raises(ValueError):
        estimate_calories(0, "MG")
    with pytest.raises(ValueError):
        estimate_calories(-5, "MG")


def test_estimate_calories_rejects_unknown_program():
    with pytest.raises(KeyError):
        estimate_calories(70, "ZZ")
