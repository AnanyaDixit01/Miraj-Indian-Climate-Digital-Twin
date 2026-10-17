"""Rule-based climate risk screening for dashboard decision support.

These helpers deliberately produce screening indicators rather than official
weather warnings. They operate on the observed grid statistics already
calculated by the dashboard and do not depend on Streamlit.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ClimateAlert:
    """A serializable climate screening result for one observation grid."""

    level: str
    title: str
    message: str
    action: str


def assess_climate_alert(variable: str, mean_value: float, peak_value: float) -> ClimateAlert:
    """Classify an observed climate grid using simple operational thresholds.

    Rainfall bands follow the daily accumulation thresholds described in the
    MIRR project direction. Temperature uses a 40 degree Celsius screening
    threshold; local IMD criteria can also depend on geography and anomalies,
    so this must not be presented as an official heatwave declaration.

    Parameters
    ----------
    variable:
        Dataset variable key, for example ``rainfall`` or ``temperature``.
    mean_value:
        Spatial mean for the selected state and date.
    peak_value:
        Maximum grid-cell value for the selected state and date.
    """
    if not _is_finite(mean_value) or not _is_finite(peak_value):
        return ClimateAlert(
            level="unavailable",
            title="Insufficient data",
            message="A risk indicator could not be calculated for this selection.",
            action="Check dataset coverage before using this view.",
        )

    if variable == "rainfall":
        return _assess_rainfall(peak_value)

    if variable == "temperature":
        if peak_value >= 40.0:
            return ClimateAlert(
                level="high",
                title="High heat screening signal",
                message=f"The maximum grid-cell temperature is {peak_value:.1f} °C.",
                action="Review local IMD bulletins and heat-action guidance.",
            )
        return ClimateAlert(
            level="normal",
            title="No high-heat signal",
            message=f"The maximum grid-cell temperature is {peak_value:.1f} °C.",
            action="Continue routine temperature monitoring.",
        )

    return ClimateAlert(
        level="monitor",
        title="Monitoring view",
        message=f"State mean is {mean_value:.1f} and the grid-cell peak is {peak_value:.1f}.",
        action="Compare the trend with local observations and official bulletins.",
    )


def _assess_rainfall(peak_value: float) -> ClimateAlert:
    """Return a rainfall screening band from the maximum daily value."""
    if peak_value >= 204.5:
        return ClimateAlert(
            level="extreme",
            title="Extremely heavy rainfall signal",
            message=f"Peak daily rainfall is {peak_value:.1f} mm (at least 204.5 mm).",
            action="Check official warnings and local emergency guidance immediately.",
        )
    if peak_value >= 115.6:
        return ClimateAlert(
            level="high",
            title="Very heavy rainfall signal",
            message=f"Peak daily rainfall is {peak_value:.1f} mm (115.6–204.4 mm).",
            action="Monitor flood-prone locations and official warnings closely.",
        )
    if peak_value >= 64.5:
        return ClimateAlert(
            level="elevated",
            title="Heavy rainfall signal",
            message=f"Peak daily rainfall is {peak_value:.1f} mm (64.5–115.5 mm).",
            action="Review local forecasts, drainage conditions, and IMD bulletins.",
        )
    return ClimateAlert(
        level="normal",
        title="No heavy-rainfall signal",
        message=f"Peak daily rainfall is {peak_value:.1f} mm, below 64.5 mm.",
        action="Continue routine rainfall monitoring.",
    )


def _is_finite(value: float) -> bool:
    """Return whether a numeric input can be used in an alert rule."""
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False
