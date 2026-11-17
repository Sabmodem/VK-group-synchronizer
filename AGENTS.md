# AGENTS.md

## Setup

1. Create virtual environment and install deps:
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

2. Configure environment:
- Rename `.env.example` → `.env` and fill in values (VK tokens, Google Sheets ID/credentials, spreadsheet bounds)
- Replace `credentials.json` with Google service account credentials

## Usage

```bash
python3 presentation/cli.py <command>
```

Available commands:
- `sync` — Create groups + update + mark as processed
- `create` — Create groups only
- `update` — Update existing groups only
- `subscribe` — Subscribe admin account to all groups (must run before `grant_admin`)
- `grant_admin` — Give admin rights to specified account (run after `subscribe`)

⚠️ `subscribe` and `grant_admin` must run sequentially in that order.

## Dry Run

Set `DRY_RUN=True` in `.env` to simulate operations without making changes.

## Architecture

Hexagonal architecture:
- `presentation/` — CLI entrypoint (click)
- `application/` — use cases (business logic)
- `domain/` — entities, interfaces, services, exceptions
- `infrastructure/` — external adapters (VK API, Google Sheets, captcha solvers)

## Known Constraints

- VK API rate limits: 0.5s delay between requests
- Captcha challenges require manual solving via console solver
- Only processes rows where `updating = TRUE` (Google Sheets boolean, not string)
- Skips cells containing "-"
- Reads credentials from `.env` + `credentials.json` path
