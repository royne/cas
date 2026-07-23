---
name: dropi-cas-automation
description: Install, configure, validate, and extend the portable Dropi CAS Automation package without embedding credentials or account-specific data.
version: 0.1.0
created_by: agent
---

# Portable Dropi CAS Automation

Use this skill when a user asks to install or extend the standalone package in a new environment.

## Safety boundary

The base package is local-only. It can initialize its own workspace and evaluate local JSON, but it does not connect to a website, create cases, upload evidence, send messages, or schedule jobs.

The `diagnose-dropi` command is a narrow exception: it is a real browser-harness read-only session check and requires `--allow-external-read`. It must never be used as implicit authorization for external writes.

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

## Read-only browser diagnostic

Only after the user explicitly authorizes a browser read and has signed in manually:

```bash
.venv/bin/dropi-cas diagnose-dropi --config ./config.toml --allow-external-read
```

This command may open/switch to the orders page. It returns only URL/login/orders visibility metadata and must not print or persist browser tokens, cookies, localStorage, or customer data.

## Local evaluation

Prepare an input JSON array with `order_id`, `guide`, `carrier`, `current_status`, and `last_movement_at` fields, then run:

```bash
.venv/bin/dropi-cas evaluate --config ./config.toml --input ./orders.json
```

## Before adding any external adapter

1. Confirm the data source and whether automation is allowed.
2. Keep credentials outside source control.
3. Implement a dry-run/read-only mode first.
4. Require explicit opt-in for external writes such as case creation, file upload, or messaging.
5. Add tests for retries, duplicate prevention, evidence requirements, and audit persistence.
