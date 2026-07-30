import math
from statistics import NormalDist

import pytest

from fixed_income_quant import BondRiskModel, parametric_bond_risk


@pytest.fixture
def risk_model() -> BondRiskModel:
    return BondRiskModel(
        modified_duration=4.2,
        yield_volatility=0.01,
        spread_duration=3.8,
        credit_spread_volatility=0.0075,
        rates_credit_correlation=0.20,
    )


def test_parametric_risk_returns_auditable_components(risk_model: BondRiskModel) -> None:
    result = parametric_bond_risk(
        price=99.75,
        quantity=1_000,
        risk_model=risk_model,
        horizon_years=10 / 252,
        confidence_level=0.99,
    )

    annual_variance = risk_model.annual_price_return_variance
    expected_pnl_volatility = 99.75 * 1_000 * math.sqrt(annual_variance * 10 / 252)
    quantile = NormalDist().inv_cdf(0.99)

    assert result.market_value == pytest.approx(99_750)
    assert result.pnl_volatility == pytest.approx(expected_pnl_volatility)
    assert result.value_at_risk == pytest.approx(quantile * expected_pnl_volatility)
    assert result.expected_shortfall > result.value_at_risk > 0
    assert (
        result.rates_variance_component
        + result.credit_variance_component
        + result.covariance_component
    ) == pytest.approx(annual_variance)


def test_risk_scales_with_position_and_square_root_of_time(
    risk_model: BondRiskModel,
) -> None:
    one_day = parametric_bond_risk(
        price=100,
        quantity=10,
        risk_model=risk_model,
        horizon_years=1 / 252,
    )
    four_days = parametric_bond_risk(
        price=100,
        quantity=-20,
        risk_model=risk_model,
        horizon_years=4 / 252,
    )

    assert four_days.market_value == pytest.approx(2 * one_day.market_value)
    assert four_days.pnl_volatility == pytest.approx(4 * one_day.pnl_volatility)


def test_zero_risk_model_returns_zero_loss_statistics() -> None:
    result = parametric_bond_risk(
        price=100,
        quantity=10,
        risk_model=BondRiskModel(modified_duration=0, yield_volatility=0),
    )

    assert result.pnl_volatility == 0
    assert result.value_at_risk == 0
    assert result.expected_shortfall == 0


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"price": 0, "quantity": 1}, "price must be positive"),
        ({"price": 100, "quantity": 0}, "quantity must be non-zero"),
        ({"price": 100, "quantity": 1, "horizon_years": 0}, "horizon_years"),
        ({"price": 100, "quantity": 1, "confidence_level": 0.5}, "confidence_level"),
        ({"price": 100, "quantity": 1, "confidence_level": 1}, "confidence_level"),
    ],
)
def test_parametric_risk_rejects_invalid_inputs(
    risk_model: BondRiskModel,
    kwargs: dict[str, float],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        parametric_bond_risk(risk_model=risk_model, **kwargs)


def test_parametric_risk_requires_bond_risk_model() -> None:
    with pytest.raises(TypeError, match="BondRiskModel"):
        parametric_bond_risk(
            price=100,
            quantity=1,
            risk_model=object(),  # type: ignore[arg-type]
        )
