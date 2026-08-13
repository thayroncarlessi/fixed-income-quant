# Security Policy

## Scope

This repository contains research software for fixed-income analytics and market-risk modeling. It is not a production custody, execution, accounting, or investment-advice system.

## Reporting a vulnerability

Please do not open a public issue for a suspected security problem. Contact the maintainer through the GitHub account @thayroncarlessi with a private description, reproduction steps, affected commit, and impact assessment. Do not include client data, credentials, tokens, or other secrets.

## Responsible disclosure

The maintainer will acknowledge a report, validate the finding, and coordinate a fix or mitigation before public disclosure. Reports involving leaked secrets should include the suspected location and should be rotated immediately.

## Data and credentials

Never commit client information, market credentials, API tokens, private keys, OAuth files, local databases, or unredacted reports. Use synthetic fixtures for tests and examples.

## Model and operational risk

Quantitative results are research outputs. Every external use must record the data source, observation date, model version, parameters, and limitations. Changes to risk, pricing, or simulation logic require tests and independent review.

## Supported versions

Only the default branch and the most recent tagged release receive maintenance attention.
