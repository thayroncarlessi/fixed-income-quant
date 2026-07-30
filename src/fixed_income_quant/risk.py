"""Analytical fixed-income risk under a Gaussian duration-credit model."""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

from .market_making import BondRiskModel


def _finite(value: float, *, name: str) -> float:
    try:
        converted = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")
    return converted


@dataclass(frozen=True, slots=True)
class ParametricBondRisk:
    """Auditable Gaussian VaR and Expected Shortfall for one bond position."""

    market_value: float
    annual_price_return_volatility: float
    horizon_price_return_volatility: float
    pnl_volatility: float
    value_at_risk: float
    expected_shortfall: float
    confidence_level: float
    horizon_years: float
    rates_variance_component: float
    credit_variance_component: float
    covariance_component: float


def parametric_bond_risk(
    *,
    price: float,
    quantity: float,
    risk_model: BondRiskModel,
    horizon_years: float = 1 / 252,
    confidence_level: float = 0.99,
) -> ParametricBondRisk:
    """Calculate loss-positive Gaussian VaR and Expected Shortfall.

    ``price`` and ``quantity`` determine the absolute market value exposed to
    risk. Yield and credit-spread volatilities come from ``risk_model`` in
    annual decimal yield units. The result is zero-mean and linear in duration,
    so it excludes convexity, jump/default losses and liquidity costs.
    """

    clean_price = _finite(price, name="price")
    position = _finite(quantity, name="quantity")
    horizon = _finite(horizon_years, name="horizon_years")
    confidence = _finite(confidence_level, name="confidence_level")

    if clean_price <= 0:
        raise ValueError("price must be positive")
    if position == 0:
        raise ValueError("quantity must be non-zero")
    if horizon <= 0:
        raise ValueError("horizon_years must be positive")
    if not 0.5 < confidence < 1.0:
        raise ValueError("confidence_level must be between 0.5 and 1")
    if not isinstance(risk_model, BondRiskModel):
        raise TypeError("risk_model must be a BondRiskModel")

    rates_risk = risk_model.modified_duration * risk_model.yield_volatility
    credit_risk = risk_model.spread_duration * risk_model.credit_spread_volatility
    rates_variance = rates_risk**2
    credit_variance = credit_risk**2
    covariance = 2.0 * risk_model.rates_credit_correlation * rates_risk * credit_risk

    annual_variance = risk_model.annual_price_return_variance
    annual_volatility = math.sqrt(annual_variance)
    horizon_volatility = annual_volatility * math.sqrt(horizon)
    market_value = abs(clean_price * position)
    pnl_volatility = market_value * horizon_volatility

    standard_normal = NormalDist()
    quantile = standard_normal.inv_cdf(confidence)
    normal_density = math.exp(-0.5 * quantile**2) / math.sqrt(2.0 * math.pi)
    value_at_risk = quantile * pnl_volatility
    expected_shortfall = normal_density / (1.0 - confidence) * pnl_volatility

    return ParametricBondRisk(
        market_value=market_value,
        annual_price_return_volatility=annual_volatility,
        horizon_price_return_volatility=horizon_volatility,
        pnl_volatility=pnl_volatility,
        value_at_risk=value_at_risk,
        expected_shortfall=expected_shortfall,
        confidence_level=confidence,
        horizon_years=horizon,
        rates_variance_component=rates_variance,
        credit_variance_component=credit_variance,
        covariance_component=covariance,
    )
