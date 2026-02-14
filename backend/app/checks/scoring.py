"""Scoring utilities for audit checks."""

from app.schemas.audit import CheckResult
from app.logging_config import get_logger

logger = get_logger(__name__)


# Severity weights for score calculation
SEVERITY_WEIGHTS = {
    "pass": 1.0,
    "info": 0.8,
    "warning": 0.4,
    "critical": 0.0,
}


def calculate_score(checks: list[CheckResult]) -> float:
    """Calculate a 0-100 score from a list of check results.

    Scoring:
    - pass: full credit
    - info: 80% credit
    - warning: 40% credit
    - critical: 0% credit

    Returns:
        Score from 0 to 100, rounded to 1 decimal.
    """
    if not checks:
        return 0.0

    total_weight = 0.0
    earned_weight = 0.0

    for check in checks:
        # Exclude 'info' checks from scoring completely (neutral)
        if check.severity == "info":
            continue

        weight = 1.0  # Each check has equal weight
        total_weight += weight
        earned_weight += weight * SEVERITY_WEIGHTS.get(check.severity, 0.5)

    if total_weight == 0:
        return 0.0

    return round((earned_weight / total_weight) * 100, 1)


def calculate_overall_score(
    seo_score: float,
    aeo_score: float,
    geo_score: float,
) -> float:
    """Calculate the overall score as a weighted average.

    Weights: SEO 40%, AEO 30%, GEO 30%
    """
    return round(
        (seo_score * 0.4) + (aeo_score * 0.3) + (geo_score * 0.3),
        1,
    )


def get_critical_issues(checks: list[CheckResult]) -> list[CheckResult]:
    """Get only critical severity issues."""
    return [c for c in checks if c.severity == "critical"]


def get_warnings(checks: list[CheckResult]) -> list[CheckResult]:
    """Get only warning severity issues."""
    return [c for c in checks if c.severity == "warning"]


def get_passed(checks: list[CheckResult]) -> list[CheckResult]:
    """Get only passed checks."""
    return [c for c in checks if c.severity == "pass"]
