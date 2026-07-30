# fixed-income-quant

[English](README.md) | **Português**

Ferramentas quantitativas tipadas para performance, risco e formação de preços
em renda fixa, com CDI e convenções brasileiras como casos de uso de primeira
classe.

O projeto é público, auditável e voltado a pesquisa. Nenhuma função consulta
dados externos de forma oculta.

## O que já existe

- Information Ratio de fundos contra CDI;
- retorno ativo anualizado e Tracking Error ex-post;
- classificação explícita do Information Ratio;
- cotações bid/ask inspiradas em Avellaneda-Stoikov;
- ajuste de risco por duration, spread duration e correlação juros-crédito;
- VaR e Expected Shortfall paramétricos em Python;
- Monte Carlo de juros e crédito em Julia;
- limites de inventário e arredondamento por tick.

## Information Ratio contra CDI

```python
from fixed_income_quant import information_ratio

fundo = [0.00102, 0.00061, 0.00074, 0.00088, 0.00056]
cdi = [0.00055, 0.00055, 0.00056, 0.00055, 0.00056]

resultado = information_ratio(fundo, cdi, periods_per_year=252)
print(resultado.information_ratio)
print(resultado.tracking_error)
print(resultado.rating)
```

As faixas descritivas atualmente expostas são:

| Information Ratio | Classificação |
|---:|---|
| abaixo de 0,30 | fraco |
| 0,30 a menos de 0,50 | aceitável |
| 0,50 até 1,00 | bom |
| acima de 1,00 | excepcional |

Os valores retornados pela API permanecem em inglês para estabilidade técnica:
`weak`, `acceptable`, `good` e `exceptional`.

## VaR e Expected Shortfall paramétricos

O módulo Python combina risco de juros e crédito, dimensiona a volatilidade pelo
horizonte e retorna perdas positivas:

```python
from fixed_income_quant import BondRiskModel, parametric_bond_risk

modelo = BondRiskModel(
    modified_duration=4.2,
    yield_volatility=0.01,
    spread_duration=3.8,
    credit_spread_volatility=0.0075,
    rates_credit_correlation=0.20,
)

risco = parametric_bond_risk(
    price=99.75,
    quantity=1_000,
    risk_model=modelo,
    horizon_years=10 / 252,
    confidence_level=0.99,
)

print(risco.value_at_risk)
print(risco.expected_shortfall)
print(risco.pnl_volatility)
```

O resultado também informa separadamente as parcelas de variância de juros,
crédito e covariância. Isso permite auditar a origem do risco.

## Market making com risco de duration e crédito

```python
from fixed_income_quant import BondRiskModel, QuoteParameters, quote_bond

modelo = BondRiskModel(
    modified_duration=4.2,
    yield_volatility=0.01,
    spread_duration=3.8,
    credit_spread_volatility=0.0075,
    rates_credit_correlation=0.20,
)
parametros = QuoteParameters(
    risk_aversion=0.02,
    liquidity=1.50,
    horizon_years=1 / 252,
    inventory_limit=20,
)

cotacao = quote_bond(
    mid_price=99.75,
    inventory=8,
    risk_model=modelo,
    parameters=parametros,
)
print(cotacao.bid, cotacao.ask, cotacao.reservation_price)
```

## Instalação e testes

```bash
pip install git+https://github.com/thayroncarlessi/fixed-income-quant.git
pip install -e ".[dev]"
pytest
ruff check .
```

## Princípios

- unidades e anualização explícitas;
- resultados intermediários auditáveis;
- validação fail-closed;
- cálculos determinísticos;
- documentação em português e inglês;
- separação clara entre pesquisa e uso produtivo.

Consulte a [metodologia](docs/METHODOLOGY.md), os
[riscos de modelo](docs/MODEL_RISK.md) e o
[roadmap em português](docs/ROADMAP.pt-BR.md).

O projeto usa licença MIT. Software de pesquisa; não constitui recomendação de
investimento, parecer contábil ou aconselhamento jurídico.
