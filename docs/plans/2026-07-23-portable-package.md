# Portable Dropi CAS Package Implementation Plan

**Goal:** Build an isolated, installable Python package for configurable logistics rules, local persistence, safe dry-run evaluation, and future Dropi/browser adapters.

**Architecture:** The package keeps business rules and SQLite persistence independent from browser or messaging integrations. Runtime configuration is supplied by a user-owned TOML file; no account-specific paths, channels, credentials, or customer data are bundled.

**Tech stack:** Python 3.10+, standard library, optional pandas/openpyxl for spreadsheet adapters in a later integration layer, pytest for tests.

## Scope boundaries

- Create only `/home/lenovo/rac/code/dropi-cas-automation/`.
- Do not modify existing automation, skills, cron jobs, databases, reports, browser profiles, or environment files.
- Do not include credentials, session tokens, account IDs, channel IDs, historical data, or business-specific naming.
- The first package version is a working core with CLI install/doctor/init/evaluate commands. It does not connect to Dropi or create cases until a separately configured adapter is added.

## Tasks

1. Write tests for configurable eligibility rules and verify they fail before implementation.
2. Implement a dependency-free core model and rule engine.
3. Add isolated SQLite storage with an explicit schema and audit events.
4. Add TOML configuration parsing, safe directory initialization, and validation.
5. Add a CLI with `init`, `doctor`, and `evaluate` commands; `evaluate` accepts local JSON only and never calls external systems.
6. Add packaging metadata, an installer script, configuration example, safety documentation, and a Hermes skill guide.
7. Run test suite, compile sources, install into a new temporary virtual environment, and exercise the CLI with local sample data.
8. Add a separate, explicit opt-in read-only browser session diagnostic adapter. Do not add external writes, report generation, case creation, evidence upload, messaging, or scheduling until each is designed and tested independently.
