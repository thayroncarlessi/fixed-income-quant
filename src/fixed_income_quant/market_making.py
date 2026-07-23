"""Duration- and credit-aware bond quote calculations."""

from __future__ import annotations

import math
from dataclasses import dataclass


def _require_finite(value: float, *, name: str) -> float:
    try:
        converted = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")
    return converted


@dataclass(frozen=True, slots=True)
class BondRiskModel:
    """Annualized yield and credit-spread risk expressed in decimal units."""

    modified_duration: float
    yield_volatility: float
    spread_duration: float = 0.0
    credit_spread_volatility: float = 0.0
    rates_credit_correlation: float = 0.0

    def __post_init__(self) -> None:
        non_negative = (
            "modified_duration",
            "yield_volatility",
            "spread_duration",
            "credit_spread_volatility",
        )
        for name in non_negative:
            value = _require_finite(getattr(self, name), name=name)
            if value < 0:
                raise ValueError(f"{name} must be non-negative")
            object.__setattr__(self, name, value)

        correlation = _require_finite(
            self.rates_credit_correlation,
            name="rates_credit_correlation",
        )
        if not -1.0 <= correlation <= 1.0:
            raise ValueError("rates_credit_correlation must be between -1 and 1")
        object.__setattr__(self, "rates_credit_correlation", correlation)

    @property
    def annual_price_return_variance(self) -> float:
        """Variance of proportional price changes from rates and credit risk."""

        rates_risk = self.modified_duration * self.yield_volatility
        credit_risk = self.spread_duration * self.credit_spread_volatility
        variance = (
            rates_risk**2
            + credit_risk**2
            + 2.0 * self.rates_credit_correlation * rates_risk * credit_risk
        )
        return max(variance, 0.0)


@dataclass(frozen=True, slots=True)
class QuoteParameters:
    """Avellaneda-Stoikov-style controls in annualized price units."""

    risk_aversion: float
    liquidity: float
    horizon_years: float
    inventory_limit: float
    tick_size: float = 0.01

    def __post_init__(self) -> None:
        positive = (
            "risk_aversion",
            "liquidity",
            "horizon_years",
            "inventory_limit",
            "tick_size",
        )
        for name in positive:
            value = _require_finite(getattr(self, name), name=name)
            if value <= 0:
                raise ValueError(f"{name} must be positive")
            object.__setattr__(self, name, value)


@dataclass(frozen=True, slots=True)
class BondQuote:
    """Quote and risk components returned by :func:`quote_bond`."""

    bid: float | None
    ask: float | None
    reservation_price: float
    optimal_half_spread: float
    annual_price_variance: float
    annual_price_return_variance: float
    inventory: float


def _round_down(value: float, tick_size: float) -> float:
    return math.floor((value + 1e-12) / tick_size) * tick_size


def _round_up(value: float, tick_size: float) -> float:
    return math.ceil((value - 1e-12) / tick_size) * tick_size


def quote_bond(
    *,
    mid_price: float,
    inventory: float,
    risk_model: BondRiskModel,
    parameters: QuoteParameters,
) -> BondQuote:
    """Produce inventory-aware two-sided quotes for a bond.

    Inventory is positive when long. At the hard limit, the side that would add
    exposure is disabled. Bid prices round down and asks round up to the tick.
    """

    mid = _require_finite(mid_price, name="mid_price")
    position = _require_finite(inventory, name="inventory")
    if mid <= 0:
        raise ValueError("mid_price must be positive")
    if not isinstance(risk_model, BondRiskModel):
        raise TypeError("risk_model must be a BondRiskModel")
    if not isinstance(parameters, QuoteParameters):
        raise TypeError("parameters must be QuoteParameters")

    return_variance = risk_model.annual_price_return_variance
    price_variance = mid**2 * return_variance
    risk_term = parameters.risk_aversion * price_variance * parameters.horizon_years
    reservation_price = mid - position * risk_term
    liquidity_term = math.log1p(
        parameters.risk_aversion / parameters.liquidity
    ) / parameters.risk_aversion
    half_spread = 0.5 * risk_term + liquidity_term

    raw_bid = reservation_price - half_spread
    raw_ask = reservation_price + half_spread
    bid = None
    ask = None

    if position < parameters.inventory_limit:
        bid = _round_down(raw_bid, parameters.tick_size)
        if bid <= 0:
            bid = None
    if position > -parameters.inventory_limit:
        ask = _round_up(raw_ask, parameters.tick_size)

    return BondQuote(
        bid=bid,
        ask=ask,
        reservation_price=reservation_price,
        optimal_half_spread=half_spread,
        annual_price_variance=price_variance,
        annual_price_return_variance=return_variance,
        inventory=position,
    )
