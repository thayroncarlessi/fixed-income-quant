import pytest

from fixed_income_quant import BondRiskModel, QuoteParameters, quote_bond


@pytest.fixture
def risk_model() -> BondRiskModel:
    return BondRiskModel(
        modified_duration=4.2,
        yield_volatility=0.01,
        spread_duration=3.8,
        credit_spread_volatility=0.0075,
        rates_credit_correlation=0.20,
    )


@pytest.fixture
def parameters() -> QuoteParameters:
    return QuoteParameters(
        risk_aversion=0.02,
        liquidity=1.50,
        horizon_years=1 / 252,
        inventory_limit=20,
    )


def test_risk_model_includes_rates_credit_covariance(risk_model: BondRiskModel) -> None:
    rates = 4.2 * 0.01
    credit = 3.8 * 0.0075
    expected = rates**2 + credit**2 + 2 * 0.20 * rates * credit
    assert risk_model.annual_price_return_variance == pytest.approx(expected)


def test_long_inventory_moves_reservation_price_down(
    risk_model: BondRiskModel,
    parameters: QuoteParameters,
) -> None:
    flat = quote_bond(
        mid_price=99.75,
        inventory=0,
        risk_model=risk_model,
        parameters=parameters,
    )
    long = quote_bond(
        mid_price=99.75,
        inventory=8,
        risk_model=risk_model,
        parameters=parameters,
    )

    assert long.reservation_price < flat.reservation_price
    assert long.bid is not None and long.ask is not None
    assert long.bid < long.ask
    assert long.bid * 100 == pytest.approx(round(long.bid * 100))
    assert long.ask * 100 == pytest.approx(round(long.ask * 100))


def test_inventory_limit_disables_risk_increasing_side(
    risk_model: BondRiskModel,
    parameters: QuoteParameters,
) -> None:
    long_limit = quote_bond(
        mid_price=100,
        inventory=20,
        risk_model=risk_model,
        parameters=parameters,
    )
    short_limit = quote_bond(
        mid_price=100,
        inventory=-20,
        risk_model=risk_model,
        parameters=parameters,
    )

    assert long_limit.bid is None and long_limit.ask is not None
    assert short_limit.ask is None and short_limit.bid is not None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"modified_duration": -1, "yield_volatility": 0.01},
        {"modified_duration": 1, "yield_volatility": -0.01},
        {
            "modified_duration": 1,
            "yield_volatility": 0.01,
            "rates_credit_correlation": 1.1,
        },
    ],
)
def test_risk_model_rejects_invalid_parameters(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        BondRiskModel(**kwargs)


def test_quote_rejects_non_positive_mid(
    risk_model: BondRiskModel,
    parameters: QuoteParameters,
) -> None:
    with pytest.raises(ValueError, match="mid_price must be positive"):
        quote_bond(
            mid_price=0,
            inventory=0,
            risk_model=risk_model,
            parameters=parameters,
        )
