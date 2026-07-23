using FixedIncomeQuant
using Statistics

model = BondRiskModel(
    modified_duration = 4.2,
    yield_volatility = 0.01,
    spread_duration = 3.8,
    credit_spread_volatility = 0.0075,
    rates_credit_correlation = 0.20,
    convexity = 24.0,
)
config = MonteCarloConfig(
    scenarios = 1_000_000,
    horizon_years = 10 / 252,
    confidence_level = 0.99,
    seed = 2026,
)

# Warm up compilation before measuring execution.
simulate_bond_pnl(price = 99.75, quantity = 1_000, model = model, config = config)

elapsed = @elapsed pnl = simulate_bond_pnl(
    price = 99.75,
    quantity = 1_000,
    model = model,
    config = config,
)
report = risk_report(pnl, config)

println("Scenarios: ", config.scenarios)
println("Elapsed seconds: ", round(elapsed, digits = 4))
println("Scenarios per second: ", round(Int, config.scenarios / elapsed))
println("P&L volatility: ", round(std(pnl), digits = 2))
println("99% VaR: ", round(report.value_at_risk, digits = 2))
println("99% Expected Shortfall: ", round(report.expected_shortfall, digits = 2))
