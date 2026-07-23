import math

import pytest

from fixed_income_quant import information_ratio


def test_information_ratio_returns_auditable_components() -> None:
    portfolio = [0.00102, 0.00061, 0.00074, 0.00088, 0.00056]
    benchmark = [0.00055, 0.00055, 0.00056, 0.00055, 0.00056]

    result = information_ratio(portfolio, benchmark, periods_per_year=252)

    assert result.observations == 5
    assert result.periods_per_year == 252
    assert result.annualized_active_return == pytest.approx(
        result.mean_period_active_return * 252
    )
    assert result.information_ratio == pytest.approx(
        result.annualized_active_return / result.tracking_error
    )
    assert result.rating in {"weak", "acceptable", "good", "exceptional"}


@pytest.mark.parametrize(
    ("ratio_returns", "expected"),
    [
        ([0.01, -0.01], "weak"),
        ([0.002, 0.001], "exceptional"),
    ],
)
def test_rating_is_exposed(ratio_returns: list[float], expected: str) -> None:
    result = information_ratio(ratio_returns, [0.0, 0.0], periods_per_year=2)
    assert result.rating == expected


@pytest.mark.parametrize(
    ("portfolio", "benchmark", "message"),
    [
        ([], [], "must not be empty"),
        ([0.01], [0.01], "at least two"),
        ([0.01, 0.02], [0.01], "equal length"),
        ([0.01, math.nan], [0.0, 0.0], "finite"),
        ([0.01, 0.01], [0.0, 0.0], "tracking error is zero"),
    ],
)
def test_information_ratio_rejects_invalid_data(
    portfolio: list[float],
    benchmark: list[float],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        information_ratio(portfolio, benchmark)


@pytest.mark.parametrize("periods", [0, -1, 252.0, True])
def test_information_ratio_rejects_invalid_annualization(periods: object) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        information_ratio([0.01, 0.02], [0.0, 0.0], periods_per_year=periods)  # type: ignore[arg-type]
