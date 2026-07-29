---
name: dropi-cas-automation
description: Install, configure, validate, and extend the portable Dropi CAS Automation package without embedding credentials or account-specific data.
version: 0.1.0
created_by: agent
---

# Portable Dropi CAS Automation

Use this skill when a user asks to install or extend the standalone package in a new environment.

## Safety boundary

The package has local-only commands, read-only browser commands, and protected write commands. A read flag never authorizes writing.

- Reads require `--allow-external-read`.
- Creating CAS or sending follow-ups requires `--execute` and `--allow-external-writes`.
- A dry-run never creates cases, uploads evidence, or sends messages.
- Start every new installation with one reviewed guide (`--limit 1`) before any batch execution.

Never place passwords, tokens, cookies, browser profiles, channel identifiers, customer data, or operational databases in the package repository or its example configuration.

## Installation

```bash
cd /path/to/dropi-cas-automation
./scripts/install.sh
cp config.example.toml config.toml
.venv/bin/dropi-cas doctor --config ./config.toml
.venv/bin/dropi-cas init --config ./config.toml
```

`doctor` only parses configuration. `init` creates only the directories and SQLite database under `[workspace].root`.

## Normal operating sequence

Only after the user explicitly authorizes browser reads and has signed in manually:

```bash
.venv/bin/dropi-cas diagnose-dropi --config ./config.toml --allow-external-read
.venv/bin/dropi-cas sync --config ./config.toml --allow-external-read
.venv/bin/dropi-cas refresh-history --config ./config.toml --guide GUIDE --allow-external-read
.venv/bin/dropi-cas candidates --config ./config.toml
.venv/bin/dropi-cas run --config ./config.toml --dry-run
.venv/bin/dropi-cas followups --config ./config.toml --dry-run
.venv/bin/dropi-cas report --config ./config.toml
```

`sync` downloads the official XLSX to the package workspace. `refresh-history` reads one order's visible history. `run --dry-run` and `followups --dry-run` are local audits and must remain non-destructive.

## Real external writes

Only after a user reviews the dry-run result and explicitly approves the affected order:

```bash
.venv/bin/dropi-cas run --config ./config.toml --execute --limit 1 \
  --allow-external-read --allow-external-writes \
  --case-service-type-id "YOUR_SERVICE_TYPE_ID"

.venv/bin/dropi-cas followups --config ./config.toml --execute \
  --allow-external-read --allow-external-writes \
  --case-service-type-id "YOUR_SERVICE_TYPE_ID"
```

Before creating a CAS, the package refreshes history, validates eligibility, captures visible evidence, and checks for an existing case. Follow-ups refresh history and require an active-case confirmation before messaging.

## Scheduler

The package does not schedule itself. A user may later configure Hermes Cron or another scheduler to run safe dry-runs or explicitly approved operating commands. Never schedule external writes without a separate review and authorization policy.

## Before adding or changing an external adapter

1. Confirm the data source and whether automation is allowed.
2. Keep credentials outside source control.
3. Implement a dry-run/read-only mode first.
4. Require explicit opt-in for external writes such as case creation, file upload, or messaging.
5. Add tests for retries, duplicate prevention, evidence requirements, and audit persistence.
