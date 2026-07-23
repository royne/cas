# Dropi CAS Automation

Portable, account-neutral Dropi CAS automation package. It owns its workspace, SQLite database, browser operations, evidence, and reports without depending on another installation.

## What version 0.1.0 does

- Installs in its own Python virtual environment.
- Reads a private TOML configuration file.
- Creates only its configured workspace: SQLite data, evidence, and report directories.
- Downloads and imports the official orders XLSX.
- Reads a guide's visible order history and stores real movements.
- Evaluates local candidates against a configurable no-movement threshold.
- Validates remote eligibility, captures evidence, creates a CAS through the official UI, records it locally, and supports protected follow-up sending.
- Generates local summaries for orders, open cases, and follow-ups.

Local commands remain offline by default. Browser reads require `--allow-external-read`; case creation and follow-up writes require `--allow-external-writes`. Browser tokens remain in the authenticated browser session and are never printed or stored by the package.

## Isolation guarantees

The package does not contain account-specific paths, identifiers, channel names, credentials, browser profiles, historical records, or operational reports.

Its default runtime is relative to the private configuration file. Example: a configuration at `/opt/dropi-cas/config.toml` with `root = "./runtime"` creates data only under `/opt/dropi-cas/runtime/`.

## Install

```bash
cd dropi-cas-automation
./scripts/install.sh
cp config.example.toml config.toml
```

The installer defaults to `.venv` inside this package. To use another location:

```bash
./scripts/install.sh /opt/dropi-cas/.venv
```

## Validate safely

```bash
.venv/bin/dropi-cas doctor --config ./config.toml
.venv/bin/dropi-cas init --config ./config.toml
```

`doctor` is local-only. `init` creates the configured local directories and SQLite database only.

## Evaluate local JSON

Example input:

```json
[
  {
    "order_id": "example-001",
    "guide": "GUIDE-001",
    "carrier": "carrier-name",
    "current_status": "EN TRANSPORTE",
    "last_movement_at": "2026-07-20T10:00:00+00:00"
  }
]
```

Run:

```bash
.venv/bin/dropi-cas evaluate --config ./config.toml --input ./orders.json
```

The command returns JSON decisions and saves an audit record to the package's configured SQLite database.

## Read-only Dropi session diagnostic

Prerequisite: the user must already have an authenticated browser session available to browser-harness.

```bash
.venv/bin/dropi-cas diagnose-dropi --config ./config.toml --allow-external-read
```

Without the opt-in flag, the command stops before starting a browser runner:

```bash
.venv/bin/dropi-cas diagnose-dropi --config ./config.toml
```

The result only includes the page URL and booleans for login/orders visibility. It never prints browser storage, cookies, or tokens.

## Operational commands

```bash
# Read-only Dropi operations
.venv/bin/dropi-cas sync --config ./config.toml --allow-external-read
.venv/bin/dropi-cas refresh-history --config ./config.toml --guide GUIDE --allow-external-read

# Local-only operations
.venv/bin/dropi-cas candidates --config ./config.toml
.venv/bin/dropi-cas run --config ./config.toml --dry-run
.venv/bin/dropi-cas followups --config ./config.toml --dry-run
.venv/bin/dropi-cas report --config ./config.toml

# Real case creation: begin with one controlled guide.
.venv/bin/dropi-cas run --config ./config.toml --execute --limit 1 \
  --allow-external-read --allow-external-writes \
  --case-service-type-id "YOUR_SERVICE_TYPE_ID"

# Real follow-ups: rechecks movement and active-case status before sending.
.venv/bin/dropi-cas followups --config ./config.toml --execute \
  --allow-external-read --allow-external-writes \
  --case-service-type-id "YOUR_SERVICE_TYPE_ID"
```

`run --execute` affects real operations: it refreshes the guide, validates it, captures evidence, creates a case only when Dropi confirms it is not already open, and records confirmed cases locally.

## Per-installation customization

`config.toml` controls the workspace path and no-movement threshold. CLI flags provide the browser command, batch limit, and account-specific CAS service type. Every installation needs its own authenticated browser session; no credentials belong in `config.toml` or this repository.

## Test

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
