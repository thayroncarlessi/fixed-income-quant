"""Benchmark-relative performance analytics."""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InformationRatioResult:
    """Auditable components of an annualized Information Ratio."""

    information_ratio: float
    annualized_active_return: float
    tracking_error: float
    mean_period_active_return: float
    observations: int
    periods_per_year: int
    rating: str


def _finite_returns(values: Iterable[float], *, name: str) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain only numeric returns") from exc

    if not result:
        raise ValueError(f"{name} must not be empty")
    if not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must contain only finite returns")
    return result


def _rate_information_ratio(value: float) -> str:
    if value < 0.30:
        return "weak"
    if value < 0.50:
        return "acceptable"
    if value <= 1.00:
        return "good"
    return "exceptional"


def information_ratio(
    portfolio_returns: Iterable[float],
    benchmark_returns: Iterable[float],
    *,
    periods_per_year: int = 252,
) -> InformationRatioResult:
    """Calculate annualized active return, tracking error and Information Ratio.

    Inputs are aligned simple returns expressed as decimals. Tracking error uses
    the sample standard deviation, so at least two observations are required.
    """

    portfolio = _finite_returns(portfolio_returns, name="portfolio_returns")
    benchmark = _finite_returns(benchmark_returns, name="benchmark_returns")

    if len(portfolio) != len(benchmark):
        raise ValueError("portfolio_returns and benchmark_returns must have equal length")
    if len(portfolio) < 2:
        raise ValueError("at least two aligned observations are required")
    if isinstance(periods_per_year, bool) or not isinstance(periods_per_year, int):
        raise ValueError("periods_per_year must be a positive integer")
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be a positive integer")

    active_returns = tuple(
        portfolio_return - benchmark_return
        for portfolio_return, benchmark_return in zip(portfolio, benchmark, strict=True)
    )
    mean_active = statistics.fmean(active_returns)
    annualized_active_return = mean_active * periods_per_year
    tracking_error = statistics.stdev(active_returns) * math.sqrt(periods_per_year)

    if math.isclose(tracking_error, 0.0, abs_tol=1e-15):
        raise ValueError("information ratio is undefined when tracking error is zero")

    ratio = annualized_active_return / tracking_error
    return InformationRatioResult(
        information_ratio=ratio,
        annualized_active_return=annualized_active_return,
        tracking_error=tracking_error,
        mean_period_active_return=mean_active,
        observations=len(active_returns),
        periods_per_year=periods_per_year,
        rating=_rate_information_ratio(ratio),
    )
