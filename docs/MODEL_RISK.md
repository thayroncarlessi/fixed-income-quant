# Model risk and intended use

This repository is research software. It does not provide investment advice and
does not claim that the displayed quotes are executable.

## Information Ratio

- The result depends on the sampling frequency and annualization factor.
- Portfolio and CDI observations must be aligned externally.
- Serial correlation, stale marks and nonlinear exposures can understate
  tracking error.
- Short histories produce unstable estimates.
- The rating thresholds are conventions, not universal standards.

## Bond quote model

- Modified duration is a local linear approximation and omits convexity.
- Yield and credit-spread shocks are represented by constant annualized
  volatilities and a constant correlation.
- Liquidity is reduced to one arrival/intensity parameter.
- The model omits fees, taxes, settlement, order priority, partial fills,
  counterparty limits and jump/default risk.
- Inventory is treated as a scalar rather than a portfolio of correlated risks.
- The hard inventory limit disables one quote side but is not a complete risk
  management system.

## Monte Carlo risk engine

- Yield and spread shocks are Gaussian, with constant volatility and
  correlation over the selected horizon.
- The duration-convexity approximation is local and can become inaccurate under
  large shocks, embedded options or discontinuous credit events.
- Expected Shortfall is estimated from a finite simulated tail and therefore
  has sampling error.
- The random seed supports reproducibility, not predictive certainty.
- Reported VaR and Expected Shortfall exclude liquidity, transaction costs,
  default recovery uncertainty and model calibration error.

Before production use, calibrate with instrument-level data, backtest out of
sample, stress nonlinear and default scenarios, and add independent market,
credit, liquidity and operational controls.

Primary conceptual reference:

Marco Avellaneda and Sasha Stoikov, “High-frequency trading in a limit order
book,” *Quantitative Finance* 8(3), 217–224, 2008.
https://doi.org/10.1080/14697680701381228
