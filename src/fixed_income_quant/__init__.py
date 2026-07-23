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

__all__ = [
    "BondQuote",
    "BondRiskModel",
    "InformationRatioResult",
    "QuoteParameters",
    "information_ratio",
    "quote_bond",
]

__version__ = "0.1.0"
