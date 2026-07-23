# Methodology

## Information Ratio against CDI

The implementation accepts aligned portfolio and benchmark simple returns in
decimal form. For daily Brazilian data, the default annualization factor is 252.

For active return \(a_t = r_{portfolio,t} - r_{benchmark,t}\):

- annualized active return is \(\bar{a} \times P\);
- ex-post tracking error is the sample standard deviation of \(a_t\), multiplied
  by \(\sqrt{P}\);
- Information Ratio is annualized active return divided by tracking error.

The result exposes every component used in the ratio. Missing observations must
be aligned before calling the function. A zero tracking error is rejected because
the ratio is undefined.

The qualitative labels are intentionally explicit:

| Information Ratio | Label |
|---:|---|
| below 0.30 | weak |
| 0.30 to below 0.50 | acceptable |
| 0.50 through 1.00 | good |
| above 1.00 | exceptional |

These labels are descriptive conventions, not investment recommendations.

## Duration- and credit-aware quotes

The quote engine starts with an Avellaneda-Stoikov-style reservation price and
spread, adapted to an annualized bond price variance.

The proportional price variance combines rates and credit:

\[
\sigma_r^2 =
(D_y \sigma_y)^2 +
(D_s \sigma_s)^2 +
2 \rho (D_y \sigma_y)(D_s \sigma_s)
\]

where \(D_y\) is modified duration, \(\sigma_y\) is yield volatility,
\(D_s\) is spread duration, \(\sigma_s\) is credit-spread volatility and
\(\rho\) is their correlation. Yield and spread volatilities are decimal changes
per year, such as `0.01` for 100 basis points.

For mid-price \(S\), annual price variance is \(S^2 \sigma_r^2\). With inventory
\(q\), risk aversion \(\gamma\), liquidity \(k\) and remaining horizon \(T\):

\[
r = S - q \gamma \sigma_p^2 T
\]

\[
\delta = \frac{\gamma \sigma_p^2 T}{2}
+ \frac{\ln(1 + \gamma/k)}{\gamma}
\]

The raw bid and ask are \(r-\delta\) and \(r+\delta\). The bid rounds down and
the ask rounds up to avoid silently tightening the calculated spread. At the
inventory limit, the side that would add exposure is disabled.

## Julia Monte Carlo risk engine

The Julia package simulates correlated Gaussian yield and credit-spread changes
over a configurable horizon. If \(z_1\) and \(z_2\) are independent standard
normal variables, the shocks are:

\[
\Delta y = \sigma_y \sqrt{T} z_1
\]

\[
\Delta s = \sigma_s \sqrt{T}
(\rho z_1 + \sqrt{1-\rho^2}z_2)
\]

For price \(P\), signed quantity \(Q\), modified duration \(D_y\), spread
duration \(D_s\) and convexity \(C\), simulated P&L is:

\[
\text{P\&L} = PQ
\left(-D_y\Delta y-D_s\Delta s+\frac{1}{2}C(\Delta y)^2\right)
\]

Value at Risk is reported as a positive loss quantile. Expected Shortfall is the
mean loss at or beyond that quantile. A fixed random seed makes each simulation
reproducible.
