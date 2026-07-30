# Roadmap - Motor Quantitativo Brasileiro

O objetivo é construir um motor aberto, auditável e documentado em português
para análise quantitativa de renda fixa brasileira.

## Fase 1 - Performance e risco

- [x] Information Ratio contra CDI;
- [x] Tracking Error e retorno ativo anualizado;
- [x] VaR e Expected Shortfall paramétricos;
- [x] Monte Carlo de juros e crédito em Julia;
- [x] market making com duration, crédito e inventário.

## Fase 2 - Instrumentos e curvas

- [ ] fluxos de caixa com calendários e convenções explícitas;
- [ ] duration, convexidade, DV01 e spread duration por instrumento;
- [ ] bootstrap e interpolação de curvas;
- [ ] títulos prefixados, indexados ao CDI e à inflação;
- [ ] integração clara com o projeto `finmath-br`.

## Fase 3 - Carteiras

- [ ] agregação de DV01 e risco por vértice;
- [ ] decomposição de P&L;
- [ ] cenários paralelos, inclinação e curvatura;
- [ ] stress de crédito, liquidez e default;
- [ ] limites e contribuições marginais de risco.

## Fase 4 - Dados brasileiros

- [ ] adaptadores opcionais para fontes públicas;
- [ ] metadados de origem, horário e licença;
- [ ] cache reproduzível;
- [ ] exemplos com dados simulados quando a redistribuição não for permitida.

Fontes como B3, ANBIMA e provedores comerciais exigem revisão de licença antes
de qualquer redistribuição.

## Fase 5 - Produto

- [ ] CLI em português;
- [ ] notebooks educacionais;
- [ ] API local;
- [ ] dashboard de risco;
- [ ] documentação bilíngue completa;
- [ ] releases versionados e changelog.

## Critérios para aceitar novos módulos

1. fórmula e unidades documentadas;
2. entradas validadas;
3. resultados intermediários expostos;
4. testes numéricos e casos extremos;
5. ausência de chamadas ocultas a dados;
6. riscos e limitações registrados;
7. exemplo em português.
