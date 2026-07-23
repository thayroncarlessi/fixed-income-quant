using FixedIncomeQuant
using Statistics
using Test

@testset "BondRiskModel" begin
    model = BondRiskModel(
        modified_duration = 4.2,
        yield_volatility = 0.01,
        spread_duration = 3.8,
        credit_spread_volatility = 0.0075,
        rates_credit_correlation = 0.20,
        convexity = 24.0,
    )
    rates_risk = 4.2 * 0.01
    credit_risk = 3.8 * 0.0075
    expected = rates_risk^2 + credit_risk^2 + 2 * 0.20 * rates_risk * credit_risk
    @test annual_price_return_variance(model) ≈ expected

    @test_throws ArgumentError BondRiskModel(
        modified_duration = -1,
        yield_volatility = 0.01,
    )
    @test_throws ArgumentError BondRiskModel(
        modified_duration = 1,
        yield_volatility = 0.01,
        rates_credit_correlation = 1.1,
    )
end

@testset "Monte Carlo simulation" begin
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

    first_run = simulate_bond_pnl(
        price = 99.75,
        quantity = 1_000,
        model = model,
        config = config,
    )
    second_run = simulate_bond_pnl(
        price = 99.75,
        quantity = 1_000,
        model = model,
        config = config,
    )

    @test first_run == second_run
    @test length(first_run) == config.scenarios

    market_value = 99.75 * 1_000
    analytical_volatility = (
        market_value *
        sqrt(annual_price_return_variance(model) * config.horizon_years)
    )
    @test std(first_run) ≈ analytical_volatility rtol = 0.03

    report = risk_report(first_run, config)
    @test report.scenarios == 100_000
    @test report.confidence_level == 0.99
    @test report.value_at_risk > 0
    @test report.expected_shortfall >= report.value_at_risk
    @test report.worst_loss >= report.expected_shortfall
end

@testset "Fail-closed validation" begin
    model = BondRiskModel(modified_duration = 4, yield_volatility = 0.01)
    config = MonteCarloConfig(scenarios = 100)

    @test_throws ArgumentError MonteCarloConfig(scenarios = 99)
    @test_throws ArgumentError MonteCarloConfig(confidence_level = 1.0)
    @test_throws ArgumentError simulate_bond_pnl(
        price = 0,
        quantity = 1,
        model = model,
        config = config,
    )
    @test_throws ArgumentError simulate_bond_pnl(
        price = 100,
        quantity = 0,
        model = model,
        config = config,
    )
    @test_throws ArgumentError risk_report([1.0, 2.0], config)
end
