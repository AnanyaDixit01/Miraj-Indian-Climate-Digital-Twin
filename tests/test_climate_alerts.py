"""Tests for rule-based climate risk screening."""

import math

import pytest

from src.climate_alerts import assess_climate_alert


@pytest.mark.parametrize(
    ("peak", "expected_level"),
    [
        (10.0, "normal"),
        (64.5, "elevated"),
        (115.6, "high"),
        (204.5, "extreme"),
    ],
)
def test_rainfall_threshold_boundaries(peak, expected_level):
    """Each documented rainfall boundary should enter the correct band."""
    result = assess_climate_alert("rainfall", mean_value=5.0, peak_value=peak)

    assert result.level == expected_level
    assert result.action


def test_temperature_high_heat_screening():
    """A 40 degree grid-cell peak should trigger the heat screening signal."""
    result = assess_climate_alert("temperature", mean_value=35.0, peak_value=40.0)

    assert result.level == "high"
    assert "heat" in result.title.lower()


@pytest.mark.parametrize("missing_value", [math.nan, None, "not-a-number"])
def test_invalid_values_return_unavailable(missing_value):
    """Missing statistics should not create a misleading risk category."""
    result = assess_climate_alert("rainfall", missing_value, 20.0)

    assert result.level == "unavailable"


def test_other_variables_receive_monitoring_summary():
    """Variables without formal rules should still receive neutral guidance."""
    result = assess_climate_alert("humidity", mean_value=70.0, peak_value=90.0)

    assert result.level == "monitor"
    assert "70.0" in result.message
