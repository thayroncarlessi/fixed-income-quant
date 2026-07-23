module FixedIncomeQuant

using Random
using Statistics

export BondRiskModel
export MonteCarloConfig
export RiskReport
export annual_price_return_variance
export risk_report
export simulate_bond_pnl

"""
    BondRiskModel(; modified_duration, yield_volatility,
                    spread_duration=0.0, credit_spread_volatility=0.0,
                    rates_credit_correlation=0.0, convexity=0.0)

Annualized rates and credit-spread risk for a fixed-income instrument.
Volatilities are decimal yield changes, so `0.01` means 100 basis points.
"""
struct BondRiskModel
    modified_duration::Float64
    yield_volatility::Float64
    spread_duration::Float64
    credit_spread_volatility::Float64
    rates_credit_correlation::Float64
    convexity::Float64

    function BondRiskModel(;
        modified_duration::Real,
        yield_volatility::Real,
        spread_duration::Real = 0.0,
        credit_spread_volatility::Real = 0.0,
        rates_credit_correlation::Real = 0.0,
        convexity::Real = 0.0,
    )
        values = Float64.(
            (
                modified_duration,
                yield_volatility,
                spread_duration,
                credit_spread_volatility,
                rates_credit_correlation,
                convexity,
            ),
        )
        all(isfinite, values) || throw(ArgumentError("risk parameters must be finite"))
        all(>=(0.0), values[[1, 2, 3, 4, 6]]) ||
            throw(ArgumentError("durations, volatilities and convexity must be non-negative"))
        -1.0 <= values[5] <= 1.0 ||
            throw(ArgumentError("rates_credit_correlation must be between -1 and 1"))
        return new(values...)
    end
end

"""
    MonteCarloConfig(; scenarios=100_000, horizon_years=1 / 252,
                       confidence_level=0.99, seed=42)

Controls for a reproducible correlated-shock simulation.
"""
struct MonteCarloConfig
    scenarios::Int
    horizon_years::Float64
    confidence_level::Float64
    seed::Int

    function MonteCarloConfig(;
        scenarios::Integer = 100_000,
        horizon_years::Real = 1 / 252,
        confidence_level::Real = 0.99,
        seed::Integer = 42,
    )
        scenarios >= 100 ||
            throw(ArgumentError("scenarios must be at least 100"))
        horizon = Float64(horizon_years)
        confidence = Float64(confidence_level)
        isfinite(horizon) && horizon > 0 ||
            throw(ArgumentError("horizon_years must be finite and positive"))
        isfinite(confidence) && 0.5 < confidence < 1.0 ||
            throw(ArgumentError("confidence_level must be between 0.5 and 1"))
        return new(Int(scenarios), horizon, confidence, Int(seed))
    end
end

"""Summary risk statistics calculated from simulated profit and loss."""
struct RiskReport
    mean_pnl::Float64
    pnl_volatility::Float64
    value_at_risk::Float64
    expected_shortfall::Float64
    worst_loss::Float64
    scenarios::Int
    confidence_level::Float64
end

"""
    annual_price_return_variance(model)

Annual variance of proportional price changes under the linear
duration-and-spread approximation.
"""
function annual_price_return_variance(model::BondRiskModel)::Float64
    rates_risk = model.modified_duration * model.yield_volatility
    credit_risk = model.spread_duration * model.credit_spread_volatility
    variance = (
        rates_risk^2 +
        credit_risk^2 +
        2.0 * model.rates_credit_correlation * rates_risk * credit_risk
    )
    return max(variance, 0.0)
end

"""
    simulate_bond_pnl(; price, quantity, model, config=MonteCarloConfig())

Simulate profit and loss from correlated Gaussian yield and credit-spread
shocks. `quantity` is the signed number of price units held.
"""
function simulate_bond_pnl(;
    price::Real,
    quantity::Real,
    model::BondRiskModel,
    config::MonteCarloConfig = MonteCarloConfig(),
)::Vector{Float64}
    clean_price = Float64(price)
    position = Float64(quantity)
    isfinite(clean_price) && clean_price > 0 ||
        throw(ArgumentError("price must be finite and positive"))
    isfinite(position) && !iszero(position) ||
        throw(ArgumentError("quantity must be finite and non-zero"))

    rng = MersenneTwister(config.seed)
    pnl = Vector{Float64}(undef, config.scenarios)
    horizon_scale = sqrt(config.horizon_years)
    residual_scale = sqrt(max(1.0 - model.rates_credit_correlation^2, 0.0))
    market_value = clean_price * position

    for index in eachindex(pnl)
        rates_factor = randn(rng)
        independent_credit_factor = randn(rng)
        credit_factor = (
            model.rates_credit_correlation * rates_factor +
            residual_scale * independent_credit_factor
        )
        yield_shock = model.yield_volatility * horizon_scale * rates_factor
        spread_shock = (
            model.credit_spread_volatility * horizon_scale * credit_factor
        )
        proportional_return = (
            -model.modified_duration * yield_shock -
            model.spread_duration * spread_shock +
            0.5 * model.convexity * yield_shock^2
        )
        pnl[index] = market_value * proportional_return
    end
    return pnl
end

"""
    risk_report(pnl, config)

Calculate loss-positive historical Value at Risk and Expected Shortfall from
simulated P&L. Expected Shortfall is the mean loss at or beyond VaR.
"""
function risk_report(
    pnl::AbstractVector{<:Real},
    config::MonteCarloConfig,
)::RiskReport
    length(pnl) == config.scenarios ||
        throw(ArgumentError("pnl length must equal config.scenarios"))
    values = Float64.(pnl)
    all(isfinite, values) || throw(ArgumentError("pnl must contain only finite values"))

    losses = .-values
    value_at_risk = quantile(losses, config.confidence_level)
    tail_losses = filter(loss -> loss >= value_at_risk, losses)
    return RiskReport(
        mean(values),
        std(values),
        value_at_risk,
        mean(tail_losses),
        maximum(losses),
        config.scenarios,
        config.confidence_level,
    )
end

end
