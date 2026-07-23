# fixed-income-quant

[![CI](https://github.com/thayroncarlessi/fixed-income-quant/actions/workflows/ci.yml/badge.svg)](https://github.com/thayroncarlessi/fixed-income-quant/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)

Typed quantitative tools for fixed-income performance and market making, with
Brazilian CDI benchmarks as a first-class use case.

## Information Ratio against CDI

The package calculates annualized active return, ex-post tracking error and
Information Ratio from aligned portfolio and CDI returns.

```python
from fixed_income_quant import information_ratio

fund = [0.00102, 0.00061, 0.00074, 0.00088, 0.00056]
cdi = [0.00055, 0.00055, 0.00056, 0.00055, 0.00056]
result = information_ratio(fund, cdi, periods_per_year=252)
print(result.information_ratio, result.tracking_error, result.rating)
```

## Duration- and credit-aware bond quotes

The quote engine decomposes annualized price variance into yield-duration risk,
spread-duration risk and their covariance. Inventory changes the reservation
price; a hard limit disables the side that would add risk.

```python
from fixed_income_quant import BondRiskModel, QuoteParameters, quote_bond

risk = BondRiskModel(
    modified_duration=4.2,
    yield_volatility=0.01,
    spread_duration=3.8,
    credit_spread_volatility=0.0075,
    rates_credit_correlation=0.20,
)
params = QuoteParameters(
    risk_aversion=0.02,
    liquidity=1.50,
    horizon_years=1 / 252,
    inventory_limit=20,
)
quote = quote_bond(
    mid_price=99.75,
    inventory=8,
    risk_model=risk,
    parameters=params,
)
print(quote.bid, quote.ask, quote.reservation_price)
```

## Julia Monte Carlo risk engine

The repository also includes a native Julia package for high-volume,
duration-and-credit risk simulations. It generates reproducible correlated yield
and spread shocks, applies a duration-convexity price approximation, and reports
loss-positive Value at Risk and Expected Shortfall.

```julia
using FixedIncomeQuant

model = BondRiskModel(
    modified_duration = 4.2,
    yield_volatility = 0.01,
    spread_duration = 3.8,
    credit_spread_volatility = 0.0075,
    rates_credit_correlation = 0.20,
    convexity = 24.0,
)
config = MonteCarloConfig(
    scenarios = 100_000,
    horizon_years = 10 / 252,
    confidence_level = 0.99,
    seed = 2026,
)
pnl = simulate_bond_pnl(
    price = 99.75,
    quantity = 1_000,
    model = model,
    config = config,
)
report = risk_report(pnl, config)
println(report.value_at_risk, report.expected_shortfall)
```

Run the Julia tests and the one-million-scenario benchmark:

```bash
julia --project=julia/FixedIncomeQuant \
  -e 'using Pkg; Pkg.instantiate(); Pkg.test()'
julia --project=julia/FixedIncomeQuant \
  julia/FixedIncomeQuant/benchmarks/monte_carlo.jl
```

## Principles

- Explicit units and annualization.
- Deterministic calculations with no hidden data calls.
- Auditable component results, not unexplained scalars.
- Fail-closed validation.
- Research honesty: the bond model is documented as an extension, not a
  production claim.

## Install and test

```bash
pip install git+https://github.com/thayroncarlessi/fixed-income-quant.git
pip install -e ".[dev]"
pytest
ruff check .
```

Read [Methodology](docs/METHODOLOGY.md) and [Model risk](docs/MODEL_RISK.md).

[finmath-br](https://github.com/thayroncarlessi/finmath-br) remains the
deterministic Brazilian financial-math foundation; this repository adds
performance, risk decomposition and quoting decisions.

MIT licensed. Research software; not investment, accounting or legal advice.
