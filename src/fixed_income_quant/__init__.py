"""Transparent quantitative tools for fixed-income research."""

from .market_making import (
    BondQuote,
    BondRiskModel,
    QuoteParameters,
    quote_bond,
)
from .performance import (
    InformationRatioResult,
    information_ratio,
)
from .risk import (
    ParametricBondRisk,
    parametric_bond_risk,
)

__all__ = [
    "BondQuote",
    "BondRiskModel",
    "InformationRatioResult",
    "ParametricBondRisk",
    "QuoteParameters",
    "information_ratio",
    "parametric_bond_risk",
    "quote_bond",
]

__version__ = "0.1.0"
